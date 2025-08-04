# MMS Database

_Masonry MicroStructure Database_

## Requirements

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- npm
- Make


## Deploying the website locally

Follow these instructions to run the MMS Database website locally. First, run:

```bash
make install
```

Then, edit the `.env` file in the root directory of the repository with the following content:

```env
PATH_PREFIX=
API_KEYS=...
S3_ENDPOINT_PROTOCOL=https://
S3_ENDPOINT_HOSTNAME=s3.epfl.ch
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_REGION=EU
S3_BUCKET=...
S3_PATH_PREFIX=frame/dev/
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

