# MMS Database

_Masonry MicroStructure Database_

## Requirements

- Git LFS
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- [npm](https://docs.npmjs.com/) Node.js package manager
- Make


## Getting the data

After cloning the repository, make sure that you have Git LFS installed and that you have pulled the large files:

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

1. New wall microstructure data should be added to the `data/original/01_Microstructures_data/` directory, following the existing directory structure. Currently supported file formats are:
  - `.ply`
2. A matching rendered picture should be put in `data/original/02_Rendered_walls_photos/`.
3. Stone metadata should be added to `data/original/03_Stones_geometric_properties/` in `.csv` format, following the same structure as existing files.
4. The added walls should be registered in the `data/original/04_StoneMasonryMicrostructureDatabase.csv` table for them to appear in the database.
4b. If you need to add new citations, please add them to `frontend/src/assets/wall_citation_items.json` and use the corresponding keys in the CSV table.


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

Then, create a pull request on GitHub from your branch to the `dev` branch of the repository. Make sure to provide a clear description of the changes you made.


### Review and dev deployment

After your pull request has been reviewed and approved, it will be merged into the `dev` branch and automatically deployed to the development server for validation.


### Production deployment

Once the changes have been validated on the development server, they can be merged into the `main` branch (by doing a pull request from `dev` to `main`). This will trigger an automatic deployment to the production server, making the new data available to all users.


## Deploying the website locally

Running the MMS Database website locally is a great way to test changes before pushing them to the main repository. Setup your environment by running:

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
