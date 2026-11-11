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
    response = client.post("/create", data={"title": "created", "body": "created body"})
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_create_title_at_max_length(client, auth, app):
    auth.login()
    response = client.post("/create", data={"title": "a" * 100, "body": "x"})
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    response = client.post(
        "/1/update", data={"title": "updated", "body": "updated body"}
    )
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"
        assert post["body"] == "updated body"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
@pytest.mark.parametrize(
    ("data", "message"),
    (
        ({"body": "x"}, b"Missing required field: title."),
        ({"title": "x"}, b"Missing required field: body."),
    ),
)
def test_create_update_missing_field_returns_400(client, auth, path, data, message):
    auth.login()
    response = client.post(path, data=data)
    assert response.status_code == 400
    assert message in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update"))
@pytest.mark.parametrize(
    ("title", "body", "message"),
    (
        ("", "x", b"Title is required."),
        ("   ", "x", b"Title is required."),
        ("", "", b"Title is required."),
        ("x", "", b"Body is required."),
        ("x", "   ", b"Body is required."),
        ("a" * 101, "x", b"Title must be at most 100 characters."),
    ),
)
def test_create_update_validate(client, auth, app, path, title, body, message):
    auth.login()
    response = client.post(path, data={"title": title, "body": body})
    assert response.status_code == 200
    assert message in response.data

    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(id) FROM post").fetchone()[0] == 1
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "test title"


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
