"""Spike: the anonymous 3D upload as enacit4r-contrib pattern A (drafts in storage).

Mounted under /contributions next to the old /files/upload routes.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from enacit4r_contrib import Contributor, Issue, Pipeline, Receipt, Report
from enacit4r_contrib.api import contribution_router
from enacit4r_contrib.drafts import (
    Decision,
    Draft,
    DraftSink,
    FolderDraftStore,
    Review,
    review_router,
)
from enacit4r_contrib.pipeline import Bundle
from fastapi import APIRouter, Depends

from api.auth import get_admin_user
from api.config import config
from api.models.auth import User
from api.models.files import Contribution, FileInfo, UploadInfo
from api.services.mailer import Mailer

SUFFIXES = [s.strip().lower() for s in config.UPLOAD_FILES_SUFFIX.split(",") if s]
# fnmatch "*" also matches "/", so "*.ply" covers files inside folders too.
# The match is case-sensitive: list the upper-case form as well.
ALLOW = [f"*{s}" for s in SUFFIXES] + [f"*{s.upper()}" for s in SUFFIXES]

store = FolderDraftStore(Path(config.UPLOAD_FILES_PATH) / "drafts")


async def validate(bundle: Bundle) -> list[Issue]:
    if not any(p.lower().endswith(tuple(SUFFIXES)) for p in bundle):
        return [Issue(f"Add at least one 3D file ({', '.join(SUFFIXES)})")]
    return [
        Issue("File type not allowed", file=p)
        for p in bundle
        if not p.lower().endswith(tuple(SUFFIXES))
    ]


def upload_info(draft: Draft) -> UploadInfo:
    """The old e-mail takes an UploadInfo: build one from the draft."""
    base = store.root / draft.id / "files"
    files = [FileInfo(name=p, size=(base / p).stat().st_size) for p in draft.files]
    c = draft.contributor
    return UploadInfo(
        path=draft.id,
        date=datetime.now().isoformat(),
        files=files,
        total_size=sum(f.size for f in files),
        state=draft.state.value,
        contribution=Contribution(
            name=c.name, email=c.email, affiliation=c.institution, comments=c.note
        ),
    )


async def notify(draft: Draft, decision: Decision | None = None) -> None:
    await Mailer().send_data_uploaded_email(upload_info(draft))


class NotifyingDraftSink(DraftSink):
    """The library has no hook at submission: wrap the sink to e-mail the admins."""

    async def submit(
        self, bundle: Bundle, contributor: Contributor, report: Report
    ) -> Receipt:
        receipt = await super().submit(bundle, contributor, report)
        try:
            await notify(await self.store.load(receipt.id))
        except Exception:
            # As in views/files.py: a failed e-mail must not fail the upload.
            logging.exception("upload e-mail failed for draft %s", receipt.id)
        return receipt


async def publish(draft: Draft, bundle: Bundle) -> None:
    """Copy the files to a staging folder. The real publication stays manual."""
    target = store.root.parent / "published" / draft.id
    shutil.rmtree(target, ignore_errors=True)
    for path, data in bundle.items():
        (target / path).parent.mkdir(parents=True, exist_ok=True)
        (target / path).write_bytes(data)


def admin_login(user: User = Depends(get_admin_user)) -> str:
    return user.username


router = APIRouter()
router.include_router(
    contribution_router(Pipeline(validate, NotifyingDraftSink(store)), allow=ALLOW)
)
router.include_router(
    review_router(Review(store, on_publish=publish, on_change=notify), reviewer=admin_login)
)
