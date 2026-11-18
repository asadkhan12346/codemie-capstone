import os
import string

import pytest
from playwright.sync_api import expect


DEFAULT_BASE_URL = "http://localhost:5000"


def _base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _title_over_100() -> str:
    return "x" * 101


def _login_via_ui(page, base_url: str, username: str = "test", password: str = "test"):
    page.goto(f"{base_url}/auth/login")
    # Selectors: Unverified (templates are stripped of HTML in datasource)
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    page.locator("input[type='submit']").click()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC1")
def test_flaskr_4_ac1_register_missing_username_returns_400(request):
    base_url = _base_url()
    resp = request.post(f"{base_url}/auth/register", form={"password": "a"})
    assert resp.status == 400
    assert "Missing required field: username." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC2")
def test_flaskr_4_ac2_register_missing_password_returns_400(request):
    base_url = _base_url()
    resp = request.post(f"{base_url}/auth/register", form={"username": "a"})
    assert resp.status == 400
    assert "Missing required field: password." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC3")
def test_flaskr_4_ac3_register_empty_username_flashes_message(page):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/register")
    page.locator("input[name='username']").fill("   ")
    page.locator("input[name='password']").fill("a")
    page.locator("input[type='submit']").click()

    # flash message selector: Unverified
    expect(page.locator(".flash")).to_have_text("Username is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC4")
def test_flaskr_4_ac4_register_empty_password_flashes_message(page):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/register")
    page.locator("input[name='username']").fill("a")
    page.locator("input[name='password']").fill("   ")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Password is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC5")
def test_flaskr_4_ac5_login_missing_username_returns_400(request):
    base_url = _base_url()
    resp = request.post(f"{base_url}/auth/login", form={"password": "test"})
    assert resp.status == 400
    assert "Missing required field: username." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC6")
def test_flaskr_4_ac6_login_missing_password_returns_400(request):
    base_url = _base_url()
    resp = request.post(f"{base_url}/auth/login", form={"username": "test"})
    assert resp.status == 400
    assert "Missing required field: password." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC7")
def test_flaskr_4_ac7_login_empty_username_flashes_message(page):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/login")
    page.locator("input[name='username']").fill("   ")
    page.locator("input[name='password']").fill("test")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Username is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC8")
def test_flaskr_4_ac8_login_empty_password_flashes_message(page):
    base_url = _base_url()
    page.goto(f"{base_url}/auth/login")
    page.locator("input[name='username']").fill("test")
    page.locator("input[name='password']").fill("   ")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Password is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC9")
def test_flaskr_4_ac9_create_missing_title_returns_400(page, request):
    base_url = _base_url()

    # Log in to get a session cookie
    _login_via_ui(page, base_url)
    storage = page.context.storage_state()

    ctx = request.new_context(storage_state=storage)
    resp = ctx.post(f"{base_url}/create", form={"body": "hello"})
    assert resp.status == 400
    assert "Missing required field: title." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC10")
def test_flaskr_4_ac10_create_missing_body_returns_400(page, request):
    base_url = _base_url()

    _login_via_ui(page, base_url)
    storage = page.context.storage_state()

    ctx = request.new_context(storage_state=storage)
    resp = ctx.post(f"{base_url}/create", form={"title": "hello"})
    assert resp.status == 400
    assert "Missing required field: body." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC11")
def test_flaskr_4_ac11_create_empty_title_flashes_message(page):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/create")
    page.locator("input[name='title']").fill("   ")
    page.locator("textarea[name='body']").fill("x")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Title is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC12")
def test_flaskr_4_ac12_create_empty_body_flashes_message(page):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/create")
    page.locator("input[name='title']").fill("hi")
    page.locator("textarea[name='body']").fill("   ")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Body is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC13")
def test_flaskr_4_ac13_create_title_over_100_flashes_message(page):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/create")
    page.locator("input[name='title']").fill(_title_over_100())
    page.locator("textarea[name='body']").fill("x")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Title must be at most 100 characters.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC14")
def test_flaskr_4_ac14_update_missing_title_returns_400(page, request):
    base_url = _base_url()

    _login_via_ui(page, base_url)
    storage = page.context.storage_state()

    ctx = request.new_context(storage_state=storage)
    resp = ctx.post(f"{base_url}/1/update", form={"body": "hello"})
    assert resp.status == 400
    assert "Missing required field: title." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC15")
def test_flaskr_4_ac15_update_missing_body_returns_400(page, request):
    base_url = _base_url()

    _login_via_ui(page, base_url)
    storage = page.context.storage_state()

    ctx = request.new_context(storage_state=storage)
    resp = ctx.post(f"{base_url}/1/update", form={"title": "hello"})
    assert resp.status == 400
    assert "Missing required field: body." in resp.text()


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC16")
def test_flaskr_4_ac16_update_empty_title_flashes_message(page):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/1/update")
    page.locator("input[name='title']").fill("   ")
    page.locator("textarea[name='body']").fill("x")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Title is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC17")
def test_flaskr_4_ac17_update_empty_body_flashes_message(page):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/1/update")
    page.locator("input[name='title']").fill("hi")
    page.locator("textarea[name='body']").fill("   ")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Body is required.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC18")
def test_flaskr_4_ac18_update_title_over_100_flashes_message(page):
    base_url = _base_url()
    _login_via_ui(page, base_url)

    page.goto(f"{base_url}/1/update")
    page.locator("input[name='title']").fill(_title_over_100())
    page.locator("textarea[name='body']").fill("x")
    page.locator("input[type='submit']").click()

    expect(page.locator(".flash")).to_have_text("Title must be at most 100 characters.")


@pytest.mark.e2e
@pytest.mark.story("FLASKR-4")
@pytest.mark.ac("AC19")
def test_flaskr_4_ac19_valid_submissions_preserve_success_paths(page, request):
    base_url = _base_url()

    # register
    # Use a unique username per test run to avoid collisions.
    username = "u_" + "".join([string.ascii_lowercase[i % 26] for i in range(8)])
    page.goto(f"{base_url}/auth/register")
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill("a")
    page.locator("input[type='submit']").click()
    expect(page).to_have_url(f"{base_url}/auth/login")

    # login
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill("a")
    page.locator("input[type='submit']").click()
    expect(page).to_have_url(f"{base_url}/")

    # create
    page.goto(f"{base_url}/create")
    page.locator("input[name='title']").fill("valid")
    page.locator("textarea[name='body']").fill("valid body")
    page.locator("input[type='submit']").click()
    expect(page).to_have_url(f"{base_url}/")

    # update post id 1 (exists in test data for tutorial app)
    page.goto(f"{base_url}/1/update")
    page.locator("input[name='title']").fill("updated")
    page.locator("textarea[name='body']").fill("updated body")
    page.locator("input[type='submit']").click()
    expect(page).to_have_url(f"{base_url}/")
