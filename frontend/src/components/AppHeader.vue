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
      :title="t('aknowledgements')"
      @click="showAknowledgements = true"
    ></q-btn>
  </div>

  <simple-dialog v-model="showCitation" :title="t('citation')">
    <div>
      {{ t('citation_text') }}
    </div>
    <q-card class="q-mt-md">
      <q-card-section>
        <div>
          <q-icon name="article" class="q-mr-xs" />
          <span>
            Shah, M. U., Saloustros, S., Wang, Q., Shaqfa, M., Ortega, J., & Beyer, K. (2024).
            <b>Database and geometrical characterization of 3D stone masonry wall microstructures (Version 1)</b> [Dataset].
            <a href="https://doi.org/10.5281/zenodo.15044436" target="_blank">
              https://doi.org/10.5281/zenodo.15044436
            </a>.
          </span>
        </div>
      </q-card-section>

      <q-card-section>
        <div>
          <q-icon name="article" class="q-mr-xs" />
          <span>
            Shah M.U., Saloustros S., Wang Q., Shaqfa M., Ortega J., Beyer K.
            <b>Database and geometrical characterization of 3D stone masonry wall microstructures.</b>
            Earthquake Spectra. [Manuscript submitted for publication].
          </span>
        </div>
      </q-card-section>
    </q-card>
  </simple-dialog>

  <simple-dialog v-model="showContact" :title="t('contact')">
    <div>
      {{ t('contact_text') }}
    </div>
    <q-list separator class="q-mt-md">
      <essential-link
        title="Mati Ullah Shah"
        caption="people.epfl.ch/mati.shah"
        link="https://people.epfl.ch/mati.shah?lang=en"
        icon="person"
      />
      <essential-link
        title="Savvas Saloustros"
        caption="people.epfl.ch/savvas.saloustros"
        link="https://people.epfl.ch/savvas.saloustros?lang=en"
        icon="person"
      />
      <essential-link
        title="Katrin Beyer"
        caption="people.epfl.ch/katrin.beyer"
        link="https://people.epfl.ch/katrin.beyer?lang=en"
        icon="person"
      />
    </q-list>
  </simple-dialog>

  <simple-dialog v-model="showUpload" :title="t('upload')">
    <div>
      {{ t('upload_text') }}
    </div>
  </simple-dialog>

  <simple-dialog v-model="showAknowledgements" :title="t('aknowledgements')">
    <q-list separator class="q-mt-md">
      <essential-link
        title="EPFL"
        caption="eplf.ch"
        link="https://www.epfl.ch"
        icon="school"
      />
      <essential-link
        title="EESD"
        caption="epfl.ch/labs/eesd"
        link="https://www.epfl.ch/labs/eesd/"
        icon="engineering"
      />
      <essential-link
        title="ENAC-IT4R"
        caption="go.epfl.ch/it4r"
        link="https://go.epfl.ch/it4r"
        icon="construction"
      />
      <essential-link
        :title="t('source_code')"
        caption="epfl-enac/eesd-mms-db"
        link="https://github.com/EPFL-ENAC/eesd-mms-db"
        icon="code"
      />
    </q-list>
  </simple-dialog>
</template>

<script setup lang="ts">
import SimpleDialog from 'src/components/SimpleDialog.vue';
import EssentialLink from 'src/components/EssentialLink.vue';

const { t } = useI18n();
const showCitation = ref(false);
const showContact = ref(false);
const showUpload = ref(false);
const showAknowledgements = ref(false);
</script>

<style scoped lang="scss">
$header-height: 50px;

.secondary-header {
  min-height: $header-height;
  background-color: black;
  display: flex;
}

.logo {
  height: $header-height;
}

.title {
  color: white;
  font-size: 1.5rem;
  margin-top: 0;
  margin-bottom: 0;
  line-height: $header-height;
}

.icons {
  color: white;
}
</style>
