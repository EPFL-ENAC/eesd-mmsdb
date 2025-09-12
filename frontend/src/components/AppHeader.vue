<template>
  <div class="secondary-header">
    <img
      src="mmsdb_logo_64px.png"
      class="logo q-ml-sm"
      alt="Logo"
    />

    <div>
      <h1 class="title q-ml-sm">{{ t("title" )}}</h1>
    </div>

    <q-space/>

    <q-btn
      icon="format_quote"
      class="icons"
      flat
      round
      :title="t('citation')"
      @click="showCitation = true"
    ></q-btn>
    <q-btn
      icon="mail"
      class="icons"
      flat
      round
      :title="t('contact')"
      @click="showContact = true"
    ></q-btn>
    <q-btn
      icon="cloud_upload"
      class="icons"
      flat
      round
      :title="t('upload')"
      @click="showUpload = true"
    ></q-btn>
    <q-btn
      icon="handshake"
      class="icons"
      flat
      round
      :title="t('acknowledgements')"
      @click="showAcknowledgements = true"
    ></q-btn>
  </div>

  <!-- TODO: Remove -->
  <q-banner class="development-banner" dense>
    <template v-slot:avatar>
      <q-icon name="warning" color="amber" />
    </template>
    This website is currently under <strong>active development</strong>. Features and data may change. Please give your feedback using
    <a href="https://github.com/EPFL-ENAC/eesd-mmsdb/issues" target="_blank" rel="noopener">GitHub Issues</a>.
  </q-banner>

  <simple-dialog v-model="showCitation" :title="t('citation')">
    {{ t('citation_text') }}
    <citation-item
      v-for="item in citationItems"
      :key="item.title"
      v-bind="item"
      class="q-mt-sm q-mb-sm"
    />
  </simple-dialog>

  <simple-dialog v-model="showContact" :title="t('contact')">
    <div>
      {{ t('contact_text') }}
    </div>
    <q-list separator class="q-mt-md">
      <essential-link
        v-for="link in contactLinks"
        :key="link.title"
        v-bind="link"
      />
    </q-list>
  </simple-dialog>

  <simple-dialog v-model="showUpload" :title="t('upload')">
    <div>
      {{ t('upload_text') }}
    </div>
  </simple-dialog>

  <simple-dialog v-model="showAcknowledgements" :title="t('acknowledgements')">
    <q-list separator class="q-mt-md">
    </q-list>
    <q-list separator class="q-mt-md">
      <essential-link
        v-for="link in acknowledgementsLinks"
        :key="link.title"
        v-bind="link"
      />
    </q-list>
  </simple-dialog>
</template>

<script setup lang="ts">
import SimpleDialog from 'src/components/SimpleDialog.vue';
import EssentialLink from 'src/components/EssentialLink.vue';
import CitationItem from 'src/components/CitationItem.vue';
import contactLinks from 'src/assets/contact_links.json';
import acknowledgementsLinks from 'src/assets/acknowledgements_links.json';
import citationItems from 'src/assets/citation_items.json';

const { t } = useI18n();
const showCitation = ref(false);
const showContact = ref(false);
const showUpload = ref(false);
const showAcknowledgements = ref(false);
</script>

<style scoped lang="scss">
$header-height: 3.125rem;

.secondary-header {
  min-height: $header-height;
  background-color: black;
  display: flex;
  align-items: center;
}

.logo {
  height: $header-height;
}

.title {
  color: white;
  font-size: 1.5rem;
  margin-top: 0.6rem;
  margin-bottom: 0.6rem;
  line-height: 1.8rem;
}

.icons {
  color: white;
}

.development-banner {
  background: #fffbe6;
  color: #795548;
}
</style>
