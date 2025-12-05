<template>
  <div :class="['secondary-header', { 'home': isHome }]">
    <img src="/logo.svg" class="logo" alt="Logo" />

    <div class="title-group">
      <h1 class="title q-ml-sm">{{ t("title") }}</h1>
      <div class="subtitle" v-if="isHome">Regrouping {{ totalWalls.unwrapOrNull() ?? 0 }} walls across {{ numberOfSources.unwrapOrNull() ?? 0 }} sources</div>
    </div>

    <q-space />

    <div class="side-toolbar">
      <q-btn icon="format_quote" class="icons" flat round :title="t('citation')" @click="showCitation = true"></q-btn>
      <q-btn icon="mail" class="icons" flat round :title="t('contact')" @click="showContact = true"></q-btn>
      <q-btn icon="cloud_upload" class="icons" flat round :title="t('upload')" to="/contribute"></q-btn>
      <q-btn icon="handshake" class="icons" flat round :title="t('acknowledgements')"
        @click="showAcknowledgements = true"></q-btn>
    </div>
  </div>

  <!-- TODO: Remove -->
  <q-banner class="development-banner" dense>
    <template v-slot:avatar>
      <q-icon name="warning" color="amber" />
    </template>
    This website is currently under <strong>active development</strong>. Features and data may change. Please give your
    feedback using
    <a href="https://github.com/EPFL-ENAC/eesd-mmsdb/issues" target="_blank" rel="noopener">GitHub Issues</a>.
  </q-banner>

  <simple-dialog v-model="showCitation" :title="t('citation')">
    {{ t('citation_text') }}
    <citation-item v-for="item in citationItems" :key="item.title" v-bind="item" class="q-mt-sm q-mb-sm" />
  </simple-dialog>

  <simple-dialog v-model="showContact" :title="t('contact')">
    <div>
      {{ t('contact_text') }}
    </div>
    <q-list separator class="q-mt-md">
      <essential-link v-for="link in contactLinks" :key="link.title" v-bind="link" />
    </q-list>
  </simple-dialog>


  <simple-dialog v-model="showAcknowledgements" :title="t('acknowledgements')">
    <div>
      <p>
      Thanks to <a href="https://www.epfl.ch/schools/enac/about/data-at-enac/enac-it4research/">ENAC-IT4R</a> for developing the web-based interfaces, visualization features and search capabilities.
      </p>
      <p>
      This work was financed by <a href="https://www.snf.ch/fr">Swiss National Science Foundation (SNSF)</a> grant as part of the ETH Domain’s ORD program.
      </p>
    </div>
  </simple-dialog>
</template>

<script setup lang="ts">
import SimpleDialog from 'src/components/SimpleDialog.vue';
import EssentialLink from 'src/components/EssentialLink.vue';
import CitationItem from 'src/components/CitationItem.vue';
import contactLinks from 'src/assets/contact_links.json';
import citationItems from 'src/assets/citation_items.json';
import { useAsyncResultRef } from 'unwrapped/vue';
import { Result } from 'unwrapped/core';

const route = useRoute();

const isHome = computed(() => route.name === 'home');

const { t } = useI18n();
const showCitation = ref(false);
const showContact = ref(false);
const showAcknowledgements = ref(false);

const propertiesStore = usePropertiesStore()
const totalWalls = useAsyncResultRef(propertiesStore.getColumnValues("Wall ID").chain(values => Result.ok(values.length)));
const numberOfSources = useAsyncResultRef(propertiesStore.getColumnValues("Reference").chain(values => Result.ok(new Set(values).size)));

</script>

<style scoped lang="scss">
.secondary-header {
  --header-height: 3.125rem;

  min-height: var(--header-height);
  background-color: black;
  display: flex;
  align-items: center;
  flex-wrap: wrap;

  background-image: linear-gradient(to right, rgba(0, 0, 0, 1) 4rem, rgba(0, 0, 0, 0.6) 10rem, rgba(0, 0, 0, 0.9)), url("/banner_bg.png");
  background-size: cover;
  background-position: left center;

  text-shadow: 0 0 5px rgba(0, 0, 0, 1);
}

.secondary-header.home {
  --header-height: 8rem;
  background-image: linear-gradient(to right, rgba(0, 0, 0, 1) var(--header-height), rgba(0, 0, 0, 0.45) calc(var(--header-height) + 6rem), rgba(0, 0, 0, 0.7) 60rem, rgba(0, 0, 0, 0.9)), url("/banner_bg.png");
}

.logo {
  height: var(--header-height);
}

.title-group {
  color: white;
  margin-left: 0.4rem;
  margin-block: 0.6rem;
}

.title {
  font-size: 1.5rem;
  margin: 0;
  line-height: 1.8rem;
}

.home .title {
  font-size: 2.5rem;
  margin-bottom: 0.2rem;
}

.home .subtitle {
  font-size: 1.2rem;
}

.icons {
  color: white;
}

.development-banner {
  background: #fffbe6;
  color: #795548;
}

.side-toolbar {
  display: flex;
  align-items: center;
  margin-right: 0.5rem;
}

.home .side-toolbar {
  align-self: flex-end;
  margin-bottom: 0.5rem;
}
</style>
