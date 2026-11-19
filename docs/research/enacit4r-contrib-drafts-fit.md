# Does enacit4r-contrib pattern A fit the MMSDB upload?

Spike on branch `spike/enacit4r-contrib-drafts`, library tag 0.3.1. Not for merge.

## Short answer

Yes for the back end. The library replaces the upload, the storage, the admin
list and the decisions with about 100 lines (`backend/api/views/contributions.py`).
Four tests pass (`backend/tests/test_contributions_drafts.py`). The browser
cannot use it without changes, and five gaps need a small library change.

Paths below: `mmsdb:` is this repository. `lib:` is
`enacit4r_contrib/` in the installed package.

## What fits as is

- Zip or loose files, files inside folders: `read_upload` expands the zip and
  keeps the folder paths (lib:bundle.py:32-86). `allow=["*.ply", ...]` matches
  in sub-folders because `fnmatch` `*` also matches `/`.
- Safe paths, size and count caps, junk files: better than today
  (mmsdb:backend/api/services/files.py:123 only checks `..` and `/`).
- Admin listing, one draft, file download: `GET /drafts`, `GET /drafts/{id}`,
  `GET /drafts/{id}/files/{path}` (lib:drafts.py:233-248).
- Admin check: `reviewer` is a FastAPI dependency. A 4-line wrapper on
  `get_admin_user` returns the GitHub login. No cookie gives 401, a
  non-admin token gives 403 (tested).
- States and history: today the state is a free string set by the admin
  (mmsdb:backend/api/views/files.py:442-448).
  The library allows only fixed moves (lib:drafts.py:38-41). It records who
  decided and the time (lib:drafts.py:191-213). This is better.
- Manual publication: `on_publish` copies the files to
  `UPLOAD_FILES_PATH/published/<id>/`. A person still moves them to the data repository.
- E-mail on decisions: `on_change` calls the existing `Mailer`.

## What does not fit

1. **Contributor fields.** The library requires `name`, `email` and
   `institution` (lib:pipeline.py:17-26). MMSDB has `affiliation` (optional)
   and `type`, `method`, `reference`, `comments`
   (mmsdb:backend/api/models/files.py:26-33).
   Suspect "MMSDB accepts name OR email": partly refuted. The view checks
   name or email (mmsdb:backend/api/views/files.py:215), but the model requires
   both keys and the form requires both
   (mmsdb:frontend/src/components/ContributeDialog.vue:21,29). The real gaps
   are the required `institution` and the four extra fields, which the
   library drops.
   *Change:* `contribution_router(..., contributor=Model)` and
   `FolderDraftStore(..., contributor=Model)`, default `Contributor`. The router
   reads the fields of that model (lib:api.py:28-29, 128-133) and `Draft.from_dict` builds it
   (lib:drafts.py:81).

2. **Wire format.** The browser sends one `contribution` JSON field
   (mmsdb:frontend/src/stores/contribute.ts:127). The library reads one form field
   per contributor field (lib:api.py:128-133). Today's browser gets 422.
   *Change:* after (1), the library needs no change. Change the browser
   to send flat fields. Or accept an optional `contributor` JSON field in the router.

3. **No hook at submission.** Today the admins get an e-mail at upload
   (mmsdb:backend/api/views/files.py:226). `on_change` runs only on decisions
   (lib:drafts.py:207-212). The spike subclasses `DraftSink` to send it.
   *Change:* `DraftSink(store, on_submit=...)`, called after `save` and with
   errors logged as `on_change` does.

4. **No anonymous status.** The browser polls
   `GET /files/upload/{uuid}/_state` (mmsdb:backend/api/views/files.py:275,
   mmsdb:frontend/src/stores/contribute.ts:76). The library has no public route, and
   every route of `review_router` needs the reviewer.
   *Change:* add `GET /contributions/{id}/state` to `contribution_router`. It
   calls a `state(id)` method on the sink and returns only the state. This needs (5).

5. **Draft id leaks the name and is short.** The id is
   `<date>-<slug(name)>-<6 hex>` (lib:drafts.py:165): 24 random bits, and the
   contributor name in a URL. Today the id is a UUID4. With (4), a guessable id
   lets anyone read the state of the draft.
   *Change:* `secrets.token_urlsafe(16)` as id, or a `make_id` parameter.

6. **Unknown files in a zip.** Today they are dropped without a message
   (mmsdb:backend/api/services/files.py:136-141). The library refuses the whole upload
   (lib:bundle.py:79-80). The library behaviour is clearer. Keep it, but the
   upload form must show the issue list.
   *Change:* none. To keep the old behaviour, the library must check `skip`
   after `allow` (lib:bundle.py:71).

7. **Upper-case suffixes.** MMSDB lower-cases the name before the check. `fnmatchcase`
   is case-sensitive (lib:bundle.py:71,79), so the spike lists `*.PLY` too.
   `*.Ply` is still refused.
   *Change:* an `ignore_case=True` option on `read_upload` and the router.

8. **Route prefix.** The submit route is `/contributions`
   (lib:api.py:114). Mounted under `/contributions` it becomes
   `/contributions/contributions`. Small, but strange.
   *Change:* none. Mount it without a prefix or document it.

## A risk in MMSDB, not in the library

The drafts live in `UPLOAD_FILES_PATH/drafts`, as the ticket asks. The old
routes have no authentication. With one draft saved, an anonymous
`GET /files/upload/drafts` returned 200 and a zip of all drafts, with
`draft.json` and the contributor e-mails
(mmsdb:backend/api/views/files.py:286). `DELETE /files/upload/drafts` returned 500
and deleted nothing, only because the folder has no `info.json`.
Before production: put the drafts outside `UPLOAD_FILES_PATH`, or remove the old routes.

## Not done

- Front end: not changed (out of scope).
- Migration of the existing `<uuid>/info.json` uploads to drafts.
- The decision e-mail uses the "Data uploaded" template. A decision template is needed.
