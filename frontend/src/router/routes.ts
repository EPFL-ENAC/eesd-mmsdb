import { type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/HomePage.vue'),
      },
      {
        path: '/database',
        components: {
          default: () => import('pages/DatabasePage.vue'),
          drawer: () => import('components/DatabaseDrawer.vue'),
        },
        meta: { hasDrawer: true },
      },
      {
        path: '/correlations',
        components: {
          default: () => import('pages/CorrelationsPage.vue'),
          drawer: () => import('components/CorrelationsDrawer.vue'),
        },
        meta: { hasDrawer: true },
      },
      {
        path: '/quality-index',
        component: () => import('pages/QualityIndexPage.vue'),
      },
      {
        path: '/others',
        component: () => import('pages/OthersPage.vue'),
      },
      {
        path: '/about',
        component: () => import('pages/AboutPage.vue'),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
