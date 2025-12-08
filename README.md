# MMS Database

_Masonry MicroStructure Database_

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- [npm](https://docs.npmjs.com/) Node.js package manager
- Git LFS
- Make


## Cloning the repository

### Without large files

To clone the repository without getting the large files, run:

```bash
export GIT_LFS_SKIP_SMUDGE=1
git clone <repository_url>
```

When running subsequent git commands (`checkout`, `pull`, ...), make sure to keep the `GIT_LFS_SKIP_SMUDGE` variable set to `1` in your shell environment to prevent large files from getting downloaded.


### With large files

You need to pull large files if you intend to contribute new wall microstructure data.
Make sure that you have Git LFS installed. Large files will be downloaded when cloning the repository.
If you have already cloned the repository and want to fetch the large files, run:

```bash
git config --global credential.helper store
git lfs install
git lfs pull
```

You must be on EPFL's network to be able to pull the data. You will be prompted for credentials.


## Contributing new wall microstructure data

To get started, make sure that you followed the instructions above to get the LFS data.

Then, create a new git branch for your changes:
```bash
git checkout main
git pull
git checkout -b feat/new-wall-data
```

### Add new data

1. New wall microstructure data should be added to the `backend/data/original/01_Microstructures_data/` directory, following the existing directory structure. Currently supported file formats are:
  - `.ply`
2. A matching rendered picture should be put in `backend/data/original/02_Rendered_walls_photos/`.
3. Stone metadata should be added to `backend/data/original/03_Stones_geometric_properties/` in `.csv` format, following the same structure as existing files.
4. The added walls should be registered in the `backend/data/original/04_StoneMasonryMicrostructureDatabase.csv` table for them to appear in the database.
4b. If you need to add new citations, please add them to `frontend/src/assets/wall_citation_items.json` and use the corresponding keys in the CSV table.


### Generate downscaled data

After adding new data to the `backend/data/original` directory, run the following command to generate downscaled versions of the 3D models, for presentation in the website:

```bash
make generate-low-quality-models
```

This will create new files in the `backend/data/downscaled` directory.
At this point, you will be able to preview the changes locally by running the backend and frontend as described above.


### Create pull request

Once you are satisfied with your changes, commit them and push the branch to the repository. From the root directory of the repository, run:

```bash
git add .
git commit -m "Add new wall microstructure data"
git push origin feat/new-wall-data
```

Then, create a pull request on GitHub from your branch to the `dev` branch of the repository. Make sure to provide a clear description of the changes you made.


### Review and dev deployment

After your pull request has been reviewed and approved, it will be merged into the `dev` branch and automatically deployed to the development server for validation.


### Production deployment

Once the changes have been validated on the development server, they can be merged into the `main` branch (by doing a pull request from `dev` to `main`). This will trigger an automatic deployment to the production server, making the new data available to all users.


## Deploying the website locally

Running the MMS Database website locally is a great way to test changes before pushing them to the main repository. This can also work if large files weren't cloned locally, in which case they will be downloaded on demand when running the backend.

> [!NOTE]
> If LFS data was not cloned, you need to set the variables `LFS_USERNAME` and `LFS_PASSWORD` in a `.env` file in the root directory of the repository.

Setup your environment by running:

```bash
make install
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
