<template>
  <q-page>
    <div class="q-pa-md">
      <div class="text-h3 q-mb-md">About</div>
      <div class="q-mt-md">
        <q-list>
          <essential-link
            title="EESD Laboratory"
            caption="epfl.ch/labs/eesd"
            link="https://www.epfl.ch/labs/eesd/"
            icon="engineering"
          />
          <essential-link
            title="ENAC-IT4R Development team"
            caption="go.epfl.ch/it4r"
            link="https://go.epfl.ch/it4r"
            icon="construction"
          />
        </q-list>
      </div>

      <div class="q-mt-lg">
        <h4>Scientific Information</h4>
        <div class="placeholder">
          <q-banner dense class="bg-grey-2 text-grey-7">
            Scientific information will be added here soon.
          </q-banner>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import EssentialLink from 'src/components/EssentialLink.vue';
// const { t } = useI18n();
</script>
