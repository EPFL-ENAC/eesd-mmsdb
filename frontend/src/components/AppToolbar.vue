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
    <q-space />
    <span v-if="!$q.screen.lt.md">
      <q-btn
        flat
        round
        icon="menu_book"
        :title="t('resources')"
        @click="showResources = true"
      ></q-btn>
      <q-btn
        flat
        round
        icon="info"
        :title="t('introduction')"
        @click="showIntro = true"
      ></q-btn>
      <q-btn
        flat
        round
        icon="settings"
        :to="'/admin'"
        class="on-left"
      ></q-btn>
    </span>
    <q-btn v-if="$q.screen.lt.md" flat round icon="more_vert">
      <q-popup-proxy>
        <q-list class="bg-white">
          <q-item v-if="$q.screen.lt.sm" clickable v-close-popup to="/">
            <q-item-section>
              <q-item-label>{{ t('home') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item v-if="$q.screen.lt.sm" clickable v-close-popup to="/data-hub">
            <q-item-section>
              <q-item-label>{{ t('data_hub') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item v-if="$q.screen.lt.sm" clickable v-close-popup to="/explore">
            <q-item-section>
              <q-item-label>{{ t('explore') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item
            v-if="$q.screen.lt.sm"
            clickable
            v-close-popup
            to="/contribute"
          >
            <q-item-section>
              <q-item-label>{{ t('contribute') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-separator v-if="$q.screen.lt.sm" />
          <q-item clickable v-close-popup @click="showResources = true">
            <q-item-section>
              <q-item-label>{{ t('resources') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable v-close-popup @click="showIntro = true">
            <q-item-section>
              <q-item-label>{{ t('introduction') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable v-close-popup :to="'/admin'">
            <q-item-section>
              <q-item-label>{{ t('administration') }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-popup-proxy>
    </q-btn>
    <a href="https://www.epfl.ch/labs/eesd/" target="_blank" class="q-mt-sm">
      <img
        src="/EESD_logo.png"
        style="height: 25px"
        class="float-right q-mb-xs"
      />
    </a>
  </q-toolbar>

  <simple-dialog
    v-model="showIntro"
    size="md"
    :content="IntroductionMd"
  />

  <simple-dialog v-model="showResources" :title="t('resources')">
    <q-list separator>
      <essential-link
        v-for="link in essentialLinks"
        :key="link.title"
        v-bind="link"
      />
    </q-list>
  </simple-dialog>

  <app-header url="interior-1.jpg" />
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import IntroductionMd from 'src/assets/introduction.md';
import essentialLinks from 'src/assets/links.json';
import AppHeader from 'src/components/AppHeader.vue';
import EssentialLink from 'src/components/EssentialLink.vue';
import SimpleDialog from 'src/components/SimpleDialog.vue';
import type { Settings } from 'src/stores/settings';

interface Props {
  noMenu?: boolean;
}

withDefaults(defineProps<Props>(), {
  noMenu: false,
});

const $q = useQuasar();
const { t } = useI18n();
const settingsStore = useSettingsStore();

const showIntro = ref(false);
const showResources = ref(false);

onMounted(() => {
  if (!settingsStore.settings?.intro_shown) {
    showIntro.value = true;
    settingsStore.saveSettings({ intro_shown: true } as Settings);
  }
});
</script>
