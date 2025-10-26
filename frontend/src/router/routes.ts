import { type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
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
        redirect: '/quality-index/line-of-minimum-trace',
        children: [
          {
            path: 'line-of-minimum-trace',
            components: {
              default: () => import('pages/LineOfMinimumTracePage.vue'),
              drawer: () => import('components/QualityIndexDrawer.vue'),
            },
            meta: { hasDrawer: true },
          },
          {
            path: 'mqi-calculator',
            components: {
              default: () => import('pages/QualityIndexPage.vue'),
              drawer: () => import('components/QualityIndexDrawer.vue'),
            },
            meta: { hasDrawer: true },
          },
        ],
      },
      {
        path: '/others',
        component: () => import('pages/OthersPage.vue'),
      },
      {
        path: '/about',
        component: () => import('pages/AboutPage.vue'),
      },
      {
        path: '/contribute',
        component: () => import('pages/ContributePage.vue'),
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
