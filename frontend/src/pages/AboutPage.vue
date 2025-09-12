<template>
  <q-page>
    <div class="q-pa-md">
      <h4>About</h4>
      <div class="q-mt-md">
        <q-list>
          <q-item clickable tag="a" href="https://www.epfl.ch/labs/eesd/" target="_blank">
            <q-item-section avatar>
              <q-icon name="engineering" />
            </q-item-section>
            <q-item-section>
              <q-item-label>EESD Laboratory</q-item-label>
              <q-item-label caption>epfl.ch/labs/eesd</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable tag="a" href="https://go.epfl.ch/it4r" target="_blank">
            <q-item-section avatar>
              <q-icon name="construction" />
            </q-item-section>
            <q-item-section>
              <q-item-label>ENAC-IT4R</q-item-label>
              <q-item-label caption>go.epfl.ch/it4r</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <div class="q-mt-lg">
        <h6>Scientific Information</h6>
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
// const { t } = useI18n();
</script>
