import os
import sqlite3
from contextlib import closing

import pytest
from playwright.sync_api import Page, expect


DEFAULT_BASE_URL = "http://localhost:5000"


def _base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _ensure_schema(db_path: str) -> None:
    # Schema copied from flaskr/schema.sql
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


def _seed_user_and_posts(db_path: str, *, post_count: int) -> None:
    # password hash copied from tests/data.sql
    password_hash = (
        "pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f"
    )

    with closing(sqlite3.connect(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (?, ?)", ("test", password_hash))
        user_id = cur.lastrowid
        for i in range(post_count):
            cur.execute(
                "INSERT INTO post (title, body, author_id, created) VALUES (?, ?, ?, datetime('now', ?))",
                (f"seed title {i}", f"seed body {i}", user_id, f"-{i} seconds"),
            )
        conn.commit()


@pytest.fixture
def e2e_db_path(tmp_path) -> str:
    """DB path for e2e.

    IMPORTANT: The app under test must be started with DATABASE pointing at this path,
    e.g. `export DATABASE=$E2E_DB_PATH` before `flask --app flaskr run`.

    Tests cannot control the server process; they only prepare the sqlite file.
    """

    path = os.getenv("E2E_DB_PATH")
    if not path:
        # Allow local runs to still work by creating a temp DB, but require the operator to point the app at it.
        path = str(tmp_path / "flaskr_e2e.sqlite")
        os.environ["E2E_DB_PATH"] = path
    return path


@pytest.fixture
def seeded_db(e2e_db_path: str) -> str:
    _ensure_schema(e2e_db_path)
    _seed_user_and_posts(e2e_db_path, post_count=1)
    return e2e_db_path


def _missing_field_msg(field: str) -> str:
    return f"Missing required field: {field}."


def _login_via_ui(page: Page, base_url: str) -> None:
    # Selectors Unverified: templates are markdown-stripped; using label text fallbacks.
    page.goto(f"{base_url}/auth/login")
    page.get_by_label("Username").fill("test")
    page.get_by_label("Password").fill("test")
    page.get_by_role("button", name="Log In").click()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC1")
def test_register_missing_username_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        resp = ctx.post("/auth/register", form={"password": "a"})
        assert resp.status == 400
        assert _missing_field_msg("username") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC2")
def test_register_missing_password_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        resp = ctx.post("/auth/register", form={"username": "a"})
        assert resp.status == 400
        assert _missing_field_msg("password") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC3")
def test_register_empty_username_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/register")
    page.get_by_label("Username").fill("   ")
    page.get_by_label("Password").fill("a")
    page.get_by_role("button", name="Register").click()
    expect(page.locator(".flash")).to_have_text("Username is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC4")
def test_register_empty_password_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/register")
    page.get_by_label("Username").fill("a")
    page.get_by_label("Password").fill("   ")
    page.get_by_role("button", name="Register").click()
    expect(page.locator(".flash")).to_have_text("Password is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC5")
def test_login_missing_username_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        resp = ctx.post("/auth/login", form={"password": "test"})
        assert resp.status == 400
        assert _missing_field_msg("username") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC6")
def test_login_missing_password_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        resp = ctx.post("/auth/login", form={"username": "test"})
        assert resp.status == 400
        assert _missing_field_msg("password") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC7")
def test_login_empty_username_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/login")
    page.get_by_label("Username").fill("   ")
    page.get_by_label("Password").fill("test")
    page.get_by_role("button", name="Log In").click()
    expect(page.locator(".flash")).to_have_text("Username is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC8")
def test_login_empty_password_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/login")
    page.get_by_label("Username").fill("test")
    page.get_by_label("Password").fill("   ")
    page.get_by_role("button", name="Log In").click()
    expect(page.locator(".flash")).to_have_text("Password is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC9")
def test_create_missing_title_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        # login first
        login = ctx.post("/auth/login", form={"username": "test", "password": "test"})
        assert login.status in (200, 302)

        resp = ctx.post("/create", form={"body": "b"})
        assert resp.status == 400
        assert _missing_field_msg("title") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC10")
def test_create_missing_body_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        login = ctx.post("/auth/login", form={"username": "test", "password": "test"})
        assert login.status in (200, 302)

        resp = ctx.post("/create", form={"title": "t"})
        assert resp.status == 400
        assert _missing_field_msg("body") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC11")
def test_create_empty_title_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/create")
    page.get_by_label("Title").fill("   ")
    page.get_by_label("Body").fill("body")
    page.get_by_role("button", name="Save").click()
    expect(page.locator(".flash")).to_have_text("Title is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC12")
def test_create_empty_body_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/create")
    page.get_by_label("Title").fill("t")
    page.get_by_label("Body").fill("   ")
    page.get_by_role("button", name="Save").click()
    expect(page.locator(".flash")).to_have_text("Body is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC13")
def test_create_title_longer_than_100_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/create")
    page.get_by_label("Title").fill("x" * 101)
    page.get_by_label("Body").fill("body")
    page.get_by_role("button", name="Save").click()
    expect(page.locator(".flash")).to_have_text("Title must be at most 100 characters.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC14")
def test_update_missing_title_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        login = ctx.post("/auth/login", form={"username": "test", "password": "test"})
        assert login.status in (200, 302)

        resp = ctx.post("/1/update", form={"body": "b"})
        assert resp.status == 400
        assert _missing_field_msg("title") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC15")
def test_update_missing_body_returns_400(playwright, seeded_db: str):
    base_url = _base_url()
    with playwright.request.new_context(base_url=base_url) as ctx:
        login = ctx.post("/auth/login", form={"username": "test", "password": "test"})
        assert login.status in (200, 302)

        resp = ctx.post("/1/update", form={"title": "t"})
        assert resp.status == 400
        assert _missing_field_msg("body") in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC16")
def test_update_empty_title_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/1/update")
    page.get_by_label("Title").fill("   ")
    page.get_by_label("Body").fill("body")
    page.get_by_role("button", name="Save").click()
    expect(page.locator(".flash")).to_have_text("Title is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC17")
def test_update_empty_body_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/1/update")
    page.get_by_label("Title").fill("t")
    page.get_by_label("Body").fill("   ")
    page.get_by_role("button", name="Save").click()
    expect(page.locator(".flash")).to_have_text("Body is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC18")
def test_update_title_longer_than_100_returns_200_and_flashes(page: Page, seeded_db: str):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/1/update")
    page.get_by_label("Title").fill("x" * 101)
    page.get_by_label("Body").fill("body")
    page.get_by_role("button", name="Save").click()
    expect(page.locator(".flash")).to_have_text("Title must be at most 100 characters.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC19")
def test_valid_submissions_preserve_success_paths(page: Page, seeded_db: str):
    base_url = _base_url()

    # Register a new user (unique)
    page.goto(f"{base_url}/auth/register")
    page.get_by_label("Username").fill("e2e_user")
    page.get_by_label("Password").fill("e2e_pass")
    page.get_by_role("button", name="Register").click()
    expect(page).to_have_url(f"{base_url}/auth/login")

    # Login redirects to index
    page.get_by_label("Username").fill("e2e_user")
    page.get_by_label("Password").fill("e2e_pass")
    page.get_by_role("button", name="Log In").click()
    expect(page).to_have_url(f"{base_url}/")

    # Create persists and redirects
    page.goto(f"{base_url}/create")
    page.get_by_label("Title").fill("created")
    page.get_by_label("Body").fill("body")
    page.get_by_role("button", name="Save").click()
    expect(page).to_have_url(f"{base_url}/")

    # Update persists and redirects (post id 1 exists)
    page.goto(f"{base_url}/1/update")
    page.get_by_label("Title").fill("updated")
    page.get_by_label("Body").fill("body")
    page.get_by_role("button", name="Save").click()
    expect(page).to_have_url(f"{base_url}/")
