# MMS Database

_Masonry MicroStructure Database_

## Requirements

- Git LFS
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- pre-commit (`pip install pre-commit`)
- npm
- Make


## Getting the data

After cloning the repository, make sure that you have Git LFS installed and that you have pulled the large files:

```bash
git config --global credential.helper store
git lfs install
git lfs pull
```

You must be on EPFL's network to be able to pull the data. You will be prompted for credentials.


## Deploying the website locally

Follow these instructions to run the MMS Database website locally. First, run:

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


## Contributing new wall microstructure data

To get started, make sure that you followed the instructions above to get the LFS data.

Then, create a new git branch for your changes:
```bash
git checkout main
git pull
git checkout -b feat/new-wall-data
```

### Add new data

New wall microstructure data should be added to the `data/original` directory, following the existing directory structure. Currently supported file formats are:
- `.ply`

The added walls should be registered in the `data/original/04_StoneMasonryMicrostructureDatabase` table for them to appear in the database.


### Generate downscaled data

After adding new data to the `data/original` directory, run the following command to generate downscaled versions of the 3D models, for presentation in the website:

```bash
make generate-low-quality-models
```

This will create new files in the `data/downscaled` directory.
At this point, you will be able to preview the changes locally by running the backend and frontend as described above.


### Create pull request

Once you are satisfied with your changes, commit them and push the branch to the repository. From the root directory of the repository, run:

```bash
git add .
git commit -m "Add new wall microstructure data"
git push origin feat/new-wall-data
```

Then, create a pull request on GitHub from your branch to the `main` branch of the repository. Make sure to provide a clear description of the changes you made.
