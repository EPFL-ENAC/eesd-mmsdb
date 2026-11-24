"""The anonymous 3D upload as enacit4r-contrib drafts.

POST /contributions saves a draft; GET /contributions/{id}/state is public;
the admins review under /contributions/drafts.
"""

import shutil
from datetime import datetime
from pathlib import Path

from enacit4r_contrib import Issue, Pipeline
from enacit4r_contrib.api import contribution_router
from enacit4r_contrib.drafts import (
    Decision,
    Draft,
    DraftSink,
    FolderDraftStore,
    Review,
    review_router,
    secret_id,
)
from enacit4r_contrib.pipeline import Bundle
from fastapi import APIRouter, Depends
from pydantic import ConfigDict, Field

from api.auth import get_admin_user
from api.config import config
from api.models.auth import User
from api.models.files import Contribution, FileInfo, UploadInfo
from api.services.mailer import Mailer

SUFFIXES = [s.strip().lower() for s in config.UPLOAD_FILES_SUFFIX.split(",") if s]
# fnmatch "*" also matches "/", so "*.ply" covers files inside folders too.
ALLOW = [f"*{s}" for s in SUFFIXES]


class Contributor(Contribution):
    """The contribution form, with the required fields not blank."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^@\s]+@[^@\s]+$")


ROOT = Path(config.CONTRIBUTION_DRAFTS_PATH)
store = FolderDraftStore(ROOT / "drafts", contributor=Contributor)


async def validate(bundle: Bundle) -> list[Issue]:
    if not bundle:
        return [Issue(f"Add at least one 3D file ({', '.join(SUFFIXES)})")]
    return []


def upload_info(draft: Draft) -> UploadInfo:
    """The existing e-mail takes an UploadInfo: build one from the draft."""
    base = store.root / draft.id / "files"
    files = [FileInfo(name=p, size=(base / p).stat().st_size) for p in draft.files]
    return UploadInfo(
        path=draft.id,
        date=datetime.now().isoformat(),
        files=files,
        total_size=sum(f.size for f in files),
        state=draft.state.value,
        contribution=Contribution(**draft.contributor.model_dump()),
    )


async def notify(draft: Draft, decision: Decision | None = None) -> None:
    await Mailer().send_data_uploaded_email(upload_info(draft))


async def publish(draft: Draft, bundle: Bundle) -> None:
    """Copy the files to a staging folder. The real publication stays manual."""
    target = store.root.parent / "published" / draft.id
    shutil.rmtree(target, ignore_errors=True)
    for path, data in bundle.items():
        (target / path).parent.mkdir(parents=True, exist_ok=True)
        (target / path).write_bytes(data)


def admin_login(user: User = Depends(get_admin_user)) -> str:
    return user.username


sink = DraftSink(store, on_submit=notify, make_id=secret_id)

router = APIRouter()
router.include_router(
    contribution_router(
        Pipeline(validate, sink),
        allow=ALLOW,
        contributor=Contributor,
        public_state=sink.state,
        ignore_case=True,
        unexpected="Not a 3D model: only .ply, .obj and .stl files are taken",
    )
)
router.include_router(
    review_router(
        Review(store, on_publish=publish, on_change=notify), reviewer=admin_login
    ),
    prefix="/contributions",
)
