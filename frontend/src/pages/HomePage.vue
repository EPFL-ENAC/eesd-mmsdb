<template>
  <q-page>
    <div class="row">
      <div class="col"></div>
      <div class="col-8">
        <q-card flat class="q-mt-lg">
          <q-card-section>
            <q-markdown no-heading-anchor-links :src="IntroductionMd" />
          </q-card-section>
        </q-card>
        <q-btn flat color="primary" :label="t('search_catalog')" to="/data-hub" />
      </div>
      <div class="col"></div>
    </div>
    <div class="q-pa-md"></div>
  </q-page>
</template>

<script setup lang="ts">
import IntroductionMd from 'src/assets/introduction.md';

const { t } = useI18n();
</script>
