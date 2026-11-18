import os
import sqlite3
from contextlib import closing

import pytest
from playwright.sync_api import Page, expect


DEFAULT_BASE_URL = "http://localhost:5000"
PAGE_SIZE = 10


def _base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _ensure_schema(db_path: str) -> None:
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS user;
            DROP TABLE IF EXISTS post;

            CREATE TABLE user (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL
            );

            CREATE TABLE post (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              author_id INTEGER NOT NULL,
              created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              title TEXT NOT NULL,
              body TEXT NOT NULL,
              FOREIGN KEY (author_id) REFERENCES user (id)
            );
            """
        )
        conn.commit()


def _seed_posts(db_path: str, *, post_count: int) -> None:
    # password hash copied from tests/data.sql
    password_hash = (
        "pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f"
    )

    with closing(sqlite3.connect(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (?, ?)", ("test", password_hash))
        user_id = cur.lastrowid
        for i in range(post_count):
            # created DESC should show i=0 first (newest)
            cur.execute(
                "INSERT INTO post (title, body, author_id, created) VALUES (?, ?, ?, datetime('now', ?))",
                (f"p{i:03d}", f"body{i}", user_id, f"-{i} seconds"),
            )
        conn.commit()


@pytest.fixture
def e2e_db_path(tmp_path) -> str:
    path = os.getenv("E2E_DB_PATH")
    if not path:
        path = str(tmp_path / "flaskr_e2e.sqlite")
        os.environ["E2E_DB_PATH"] = path
    return path


@pytest.fixture
def seeded_many_posts_db(e2e_db_path: str) -> str:
    _ensure_schema(e2e_db_path)
    _seed_posts(e2e_db_path, post_count=21)
    return e2e_db_path


def _extract_titles(page: Page) -> list[str]:
    # Unverified selector: index template is markdown-stripped; use headings for post titles.
    return [t.strip() for t in page.locator("h1").all_text_contents() if t.strip() and t.strip() != "Flaskr"]


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC1")
def test_index_default_shows_newest_10_posts(seeded_many_posts_db: str, page: Page):
    base_url = _base_url()
    page.goto(f"{base_url}/")

    titles = _extract_titles(page)
    assert len(titles) == PAGE_SIZE
    # newest are p000..p009
    assert titles[0] == "p000"
    assert titles[-1] == "p009"


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC2")
def test_index_page_2_shows_next_posts_no_overlap(seeded_many_posts_db: str, page: Page):
    base_url = _base_url()
    page.goto(f"{base_url}/")
    page1 = _extract_titles(page)

    page.goto(f"{base_url}/?page=2")
    page2 = _extract_titles(page)

    assert 1 <= len(page2) <= PAGE_SIZE
    assert set(page1).isdisjoint(set(page2))
    assert page2[0] == "p010"


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC3")
def test_invalid_page_defaults_to_1(seeded_many_posts_db: str, page: Page):
    base_url = _base_url()

    page.goto(f"{base_url}/")
    titles_page1 = _extract_titles(page)

    page.goto(f"{base_url}/?page=abc")
    expect(page).to_have_url(f"{base_url}/?page=abc")
    assert _extract_titles(page) == titles_page1

    page.goto(f"{base_url}/?page=0")
    expect(page).to_have_url(f"{base_url}/?page=0")
    assert _extract_titles(page) == titles_page1


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC4")
def test_page_higher_than_max_shows_empty_list(seeded_many_posts_db: str, page: Page):
    base_url = _base_url()

    page.goto(f"{base_url}/?page=999")
    titles = _extract_titles(page)
    assert titles == []


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC5")
def test_ui_has_pagination_navigation_links_unverified(seeded_many_posts_db: str, page: Page):
    base_url = _base_url()
    page.goto(f"{base_url}/")

    # Template markup is unverified in AC; look for common link text.
    # If feature implementation uses different labels, adjust accordingly.
    has_next = page.get_by_role("link", name="Next").count() > 0
    has_prev = page.get_by_role("link", name="Previous").count() > 0
    assert has_next or has_prev
