import pytest

from flaskr.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None


@pytest.fixture
def many_posts(app):
    # 24 extra posts on top of the seeded one (25 total), oldest is "paged-01"
    with app.app_context():
        db = get_db()
        for n in range(1, 25):
            db.execute(
                "INSERT INTO post (title, body, author_id, created)"
                " VALUES (?, ?, 1, ?)",
                (f"paged-{n:02d}", "body", f"2019-01-{n:02d} 00:00:00"),
            )
        db.commit()


def titles(response):
    return {f"paged-{n:02d}" for n in range(1, 25) if f"paged-{n:02d}".encode() in response.data}


def test_index_page_1_shows_newest_10(client, many_posts):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.count(b'<article class="post">') == 10
    assert titles(response) == {f"paged-{n:02d}" for n in range(15, 25)}


def test_index_page_2_has_no_overlap(client, many_posts):
    page1 = titles(client.get("/"))
    response = client.get("/?page=2")
    assert response.status_code == 200
    assert response.data.count(b'<article class="post">') == 10
    assert titles(response) == {f"paged-{n:02d}" for n in range(5, 15)}
    assert not page1 & titles(response)


def test_index_last_page_has_remaining_posts(client, many_posts):
    response = client.get("/?page=3")
    assert response.status_code == 200
    assert response.data.count(b'<article class="post">') == 5
    assert b"test title" in response.data


@pytest.mark.parametrize("page", ("abc", "0", "-1", "", "1.5"))
def test_index_invalid_page_defaults_to_1(client, many_posts, page):
    response = client.get("/", query_string={"page": page})
    assert response.status_code == 200
    assert titles(response) == {f"paged-{n:02d}" for n in range(15, 25)}


def test_index_page_too_high_is_empty(client, many_posts):
    response = client.get("/?page=999")
    assert response.status_code == 200
    assert b'<article class="post">' not in response.data
    assert b"Next" not in response.data


def test_index_pagination_links(client, many_posts):
    first = client.get("/").data
    assert b'href="/?page=2"' in first
    assert b"Previous" not in first

    middle = client.get("/?page=2").data
    assert b'href="/?page=1"' in middle
    assert b'href="/?page=3"' in middle

    last = client.get("/?page=3").data
    assert b'href="/?page=2"' in last
    assert b"Next" not in last


def test_index_no_pagination_links_for_few_posts(client):
    data = client.get("/").data
    assert b"Previous" not in data
    assert b"Next" not in data


def test_index_exactly_one_full_page_has_no_next(app, client):
    with app.app_context():
        db = get_db()
        for n in range(9):
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, 'b', 1)",
                (f"fill-{n}",),
            )
        db.commit()

    response = client.get("/")
    assert response.data.count(b'<article class="post">') == 10
    assert b"Next" not in response.data
