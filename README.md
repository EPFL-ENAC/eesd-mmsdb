# MMS Database

_Masonry MicroStructure Database_

## Requirements

- Git LFS
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- pre-commit (`pip install pre-commit`)
- npm
- Make


## Deploying the website locally

Follow these instructions to run the MMS Database website locally. First, make sure all data is cloned:

```bash
git lfs install
git lfs pull
```

Then, run:

```bash
make install
```

Then, edit the `.env` file in the root directory of the repository with the following content (most fields must be left empty for local deployment):

```env
PATH_PREFIX=
LFS_USERNAME=
LFS_PASSWORD=
LFS_SERVER_URL=
LFS_GIT_REF=
LFS_CLONED_REPO_PATH=".."
```


### Backend

In one shell, run:

```bash
make run-backend
```

The interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Frontend

In another shell, run:

```bash
make run-frontend
```

The website will be available at [http://localhost:9000](http://localhost:9000).

