import io
import json
import time
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from api.auth import get_admin_user
from api.config import config
from api.main import app
from api.models.auth import User
from api.views import contributions

PERSON = {
    "name": "Ada Example",
    "email": "ada@example.org",
    "affiliation": "EPFL",
    "type": "Real",
    "method": "Photogrammetry",
}
FORM = {"contributor": json.dumps(PERSON)}


@pytest.fixture
def client(tmp_path, monkeypatch, request):
    monkeypatch.setattr(contributions.store, "root", tmp_path / "drafts")
    monkeypatch.setattr(config, "UPLOAD_FILES_PATH", str(tmp_path / "upload"))
    mailer = AsyncMock()
    monkeypatch.setattr(contributions, "Mailer", lambda: mailer)
    # The router rate-limits per client: give each test its own client key.
    c = TestClient(app, headers={"x-forwarded-for": request.node.name})
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
    return client.post("/contributions", data=FORM, files=[("files", (name, data))])


def test_zip_with_one_ply_makes_a_submitted_draft(client):
    r = upload(client)
    assert r.status_code == 201, r.text
    draft = (client.tmp / "drafts" / r.json()["id"] / "draft.json").read_text()
    assert '"state": "submitted"' in draft
    assert "OC01/stone_1.ply" in draft
    assert '"method": "Photogrammetry"' in draft
    # The e-mail to the admins goes out at submission.
    client.mailer.send_data_uploaded_email.assert_awaited_once()
    info = client.mailer.send_data_uploaded_email.await_args.args[0]
    assert info.contribution.email == "ada@example.org"


def test_upper_case_suffix_is_allowed(client):
    r = upload(client, name="STONE.PLY", data=b"ply\n")
    assert r.status_code == 201, r.text


def test_blank_name_is_refused(client):
    form = {"contributor": json.dumps({**PERSON, "name": " "})}
    files = [("files", ("a.ply", b"ply\n"))]
    r = client.post("/contributions", data=form, files=files)
    assert r.status_code == 422, r.text


def test_public_state_shows_only_the_state(client):
    id_ = upload(client).json()["id"]
    assert len(id_) >= 22
    r = client.get(f"/contributions/{id_}/state")
    assert r.status_code == 200, r.text
    assert r.json() == {"id": id_, "state": "submitted"}
    assert "ada@example.org" not in r.text
    assert client.get("/contributions/nope/state").status_code == 404


def test_drafts_live_outside_the_upload_folder():
    assert not contributions.ROOT.resolve().is_relative_to(
        Path(config.UPLOAD_FILES_PATH).resolve()
    )


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


# The four code-scanning alerts on the old /files/upload routes.


def test_anonymous_download_of_an_upload_is_refused(client):
    (client.tmp / "upload" / "abc").mkdir(parents=True)
    (client.tmp / "upload" / "abc" / "a.ply").write_bytes(b"ply\n")
    assert client.get("/files/upload/abc/a.ply").status_code == 401
    assert client.get("/files/upload/abc").status_code == 401
    as_admin()
    assert client.get("/files/upload/abc/a.ply").content == b"ply\n"


def test_anonymous_delete_of_an_upload_is_refused(client):
    (client.tmp / "upload" / "abc").mkdir(parents=True)
    assert client.delete("/files/upload/abc").status_code == 401
    assert (client.tmp / "upload" / "abc").exists()


def test_admin_cannot_delete_the_upload_root(client):
    (client.tmp / "upload" / "abc").mkdir(parents=True)
    as_admin()
    # A "/" in the name never reaches the route (it answers 405).
    for folder in ("%2E", "%2E%2E", "%2E%00"):
        for route in ("/files/upload/", "/files/upload-info/"):
            r = client.delete(route + folder)
            assert r.status_code == 400, (route, folder, r.text)
            assert r.json()["detail"] == "Invalid upload folder name"
    assert (client.tmp / "upload" / "abc").exists()
    # A single upload folder (with its info.json) can still be deleted, on both routes.
    for folder, route in (("abc", "/files/upload/"), ("def", "/files/upload-info/")):
        (client.tmp / "upload" / folder).mkdir(exist_ok=True)
        (client.tmp / "upload" / folder / "info.json").write_text("{}")
        assert client.delete(route + folder).status_code == 200
        assert not (client.tmp / "upload" / folder).exists()


def test_anonymous_state_of_an_upload_is_refused(client):
    folder = client.tmp / "upload" / "abc"
    folder.mkdir(parents=True)
    (folder / "info.json").write_text(
        json.dumps({"path": "abc", "date": "d", "files": [], "total_size": 0})
    )
    assert client.get("/files/upload/abc/_state").status_code == 401
    as_admin()
    r = client.get("/files/upload/abc/_state")
    assert r.json() == {"path": "abc", "state": "uploaded"}
