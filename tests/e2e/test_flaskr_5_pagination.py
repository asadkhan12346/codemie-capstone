import os
from datetime import datetime, timedelta

import pytest
from playwright.sync_api import expect


DEFAULT_BASE_URL = "http://localhost:5000"


def _base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _login(page, base_url: str, username: str = "test", password: str = "test"):
    page.goto(f"{base_url}/auth/login")
    # Selectors: Unverified (templates are stripped of HTML in datasource)
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    page.locator("input[type='submit']").click()


def _seed_posts_more_than_10(page, base_url: str, total: int = 12):
    """Create posts via UI so tests can run against a running app.

    This avoids directly accessing the sqlite database file from the e2e tests.
    """
    _login(page, base_url)

    # Create total posts with unique titles.
    for i in range(total):
        page.goto(f"{base_url}/create")
        page.locator("input[name='title']").fill(f"e2e post {i:02d}")
        page.locator("textarea[name='body']").fill("body")
        page.locator("input[type='submit']").click()
        expect(page).to_have_url(f"{base_url}/")


def _extract_post_titles(page):
    # Templates are stripped; we use heading tags based on the tutorial's HTML.
    # Selector: Unverified
    return page.locator("article.post h1").all_inner_texts()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC1")
def test_flaskr_5_ac1_index_without_page_shows_newest_10(page):
    base_url = _base_url()
    _seed_posts_more_than_10(page, base_url, total=12)

    page.goto(f"{base_url}/")
    titles = _extract_post_titles(page)

    assert len(titles) == 10


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC2")
def test_flaskr_5_ac2_page_2_shows_next_posts_no_overlap(page):
    base_url = _base_url()
    _seed_posts_more_than_10(page, base_url, total=12)

    page.goto(f"{base_url}/")
    page1 = set(_extract_post_titles(page))

    page.goto(f"{base_url}/?page=2")
    page2 = set(_extract_post_titles(page))

    assert page1.isdisjoint(page2)
    assert len(page2) <= 10


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC3")
@pytest.mark.parametrize("invalid", ["abc", "0"])
def test_flaskr_5_ac3_invalid_page_defaults_to_page_1(page, invalid: str):
    base_url = _base_url()
    _seed_posts_more_than_10(page, base_url, total=12)

    page.goto(f"{base_url}/")
    page1_titles = _extract_post_titles(page)

    page.goto(f"{base_url}/?page={invalid}")
    invalid_titles = _extract_post_titles(page)

    assert invalid_titles == page1_titles


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC4")
def test_flaskr_5_ac4_page_above_max_returns_empty_list(page):
    base_url = _base_url()
    _seed_posts_more_than_10(page, base_url, total=12)

    page.goto(f"{base_url}/?page=9999")
    titles = _extract_post_titles(page)
    assert titles == []


@pytest.mark.e2e
@pytest.mark.story("FLASKR-5")
@pytest.mark.ac("AC5")
def test_flaskr_5_ac5_ui_has_next_previous_navigation_links(page):
    base_url = _base_url()
    _seed_posts_more_than_10(page, base_url, total=12)

    page.goto(f"{base_url}/")

    # UI selectors: Unverified. We check link text.
    pagination = page.get_by_role("link", name="Next")
    prev = page.get_by_role("link", name="Previous")

    assert pagination.count() + prev.count() >= 1
