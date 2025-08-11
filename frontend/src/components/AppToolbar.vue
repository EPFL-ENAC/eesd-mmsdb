<template>
  <q-toolbar>
    <a href="https://epfl.ch" target="_blank" class="q-mt-sm">
      <img src="/EPFL_logo.png" :style="`height: ${$q.screen.lt.md ? '15px' : '25px'}`" />
    </a>
    <q-tabs
      v-if="!$q.screen.lt.sm"
      shrink
      stretch
      active-color="primary"
      class="q-ml-md"
    >
      <q-route-tab :label="t('home')" :title="t('home_info')" to="/" exact />
      <q-route-tab :label="t('database')" :title="t('database_info')" to="/database" exact />
      <q-route-tab :label="t('correlations')" :title="t('correlations')" to="/correlations" exact />
      <q-route-tab :label="t('quality_index')" :title="t('quality_index_info')" to="/quality-index" exact />
      <q-route-tab :label="t('others')" :title="t('others_info')" to="/others" exact />
      <q-route-tab :label="t('about')" :title="t('about_info')" to="/about" exact />
    </q-tabs>

    <q-space/>

    <a href="https://www.epfl.ch/labs/eesd/" target="_blank" class="q-mt-sm">
      <img
        src="/EESD_logo.png"
        style="height: 25px"
        class="float-right q-mb-xs"
      />
    </a>
  </q-toolbar>

  <app-header/>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import AppHeader from 'src/components/AppHeader.vue';

interface Props {
  noMenu?: boolean;
}

withDefaults(defineProps<Props>(), {
  noMenu: false,
});

const $q = useQuasar();
const { t } = useI18n();

</script>
