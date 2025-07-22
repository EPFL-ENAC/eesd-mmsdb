# EPFL ENAC IT4R webmap

A web application template that displays data on a map in a mobile-fiendly way, based on:

- [quasar.dev](https://quasar.dev/)
- [maplibre.org](https://maplibre.org/)

### Install the dependencies

```bash
npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)

```bash
npm run dev
```

### Lint the files

```bash
npm run lint
```

### Format the files

```bash
npm run format
```

### Build the app for production

```bash
nom run build
```

### Customize the configuration

If this frontend application connects to a backend service, use the following environment variables:

- `API_URL`, the base URL of the backend server: `https://some-app.epfl.ch`
- `API_PATH`, the entry point of the backend's web services: `/api`

See documentation about the [quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-js) and how the API client is setup in the [src/boot/api.ts](https://github.com/EPFL-ENAC/it4r-webmap/blob/main/src/boot/api.ts) file.
