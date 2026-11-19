import io
import time
import zipfile
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from api.auth import get_admin_user
from api.config import config
from api.main import app
from api.models.auth import User
from api.views import contributions

FORM = {"name": "Ada Example", "email": "ada@example.org", "institution": "EPFL"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(contributions.store, "root", tmp_path / "drafts")
    mailer = AsyncMock()
    monkeypatch.setattr(contributions, "Mailer", lambda: mailer)
    c = TestClient(app)
    c.mailer = mailer
    c.tmp = tmp_path
    yield c
    app.dependency_overrides.clear()


def as_admin():
    app.dependency_overrides[get_admin_user] = lambda: User(
        username="octo-admin", full_name="Admin", role="admin"
    )


def token(role: str) -> str:
    now = int(time.time())
    claims = {"iss": "mmsdb", "id": 1, "sub": "someone", "role": role}
    claims |= {"iat": now, "exp": now + 60}
    return jwt.encode(claims, config.JWT_SECRET, algorithm="HS256")


def zip_with(name: str, data: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(name, data)
    return buf.getvalue()


def upload(client, name="wall.zip", data=None):
    data = zip_with("walls/OC01/stone_1.ply", b"ply\n") if data is None else data
    return client.post(
        "/contributions/contributions", data=FORM, files=[("files", (name, data))]
    )


def test_zip_with_one_ply_makes_a_submitted_draft(client):
    r = upload(client)
    assert r.status_code == 201, r.text
    draft = (client.tmp / "drafts" / r.json()["id"] / "draft.json").read_text()
    assert '"state": "submitted"' in draft
    assert "OC01/stone_1.ply" in draft
    # The e-mail to the admins goes out at submission.
    client.mailer.send_data_uploaded_email.assert_awaited_once()


def test_txt_only_is_refused(client):
    r = upload(client, name="notes.txt", data=b"hello")
    assert r.status_code == 422, r.text
    assert not r.json()["valid"]
    assert not (client.tmp / "drafts").exists()


def test_admin_lists_accepts_publishes(client):
    id_ = upload(client).json()["id"]
    as_admin()
    assert [d["id"] for d in client.get("/contributions/drafts").json()] == [id_]
    for state in ("accepted", "published"):
        r = client.post(f"/contributions/drafts/{id_}/decision", json={"state": state})
        assert r.status_code == 200, r.text
    history = r.json()["history"]
    assert [(h["state"], h["by"]) for h in history] == [
        ("accepted", "octo-admin"),
        ("published", "octo-admin"),
    ]
    published = client.tmp / "published" / id_ / "OC01" / "stone_1.ply"
    assert published.read_bytes() == b"ply\n"
    # One e-mail at submission, one per decision.
    assert client.mailer.send_data_uploaded_email.await_count == 3


def test_non_admin_is_refused(client):
    assert client.get("/contributions/drafts").status_code == 401
    client.cookies.set("token", token("contributor"))
    assert client.get("/contributions/drafts").status_code == 403
    client.cookies.set("token", token("admin"))
    assert client.get("/contributions/drafts").status_code == 200
