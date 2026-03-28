<template>
  <q-dialog v-model="showDataProtectionNotice">
    <q-card>
      <q-card-section>
        <div class="text-h6">Masonry Microstructure Database</div>
      </q-card-section>
  
      <q-card-section>
        <p>
          Welcome to this web-based platform providing open access to realistic 3D microstructures of irregular stone masonry walls.
        </p>
        <p>
          Explore, visualize, and download curated masonry microstructure data and associated geometric descriptors.
        </p>
        <p>
          Welcome aboard!
        </p>
      </q-card-section>
  
      <q-card-actions>
        <q-toggle v-model="dontShowAgain" label="Do not show again" />
      </q-card-actions>
  
      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" v-close-popup @click="onClose()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">

const settings = useSettingsStore();

const showDataProtectionNotice = ref(!!settings.settings?.intro_shown);
const dontShowAgain = ref(false);

function onClose() {
  if (dontShowAgain.value) {
    settings.saveSettings({ intro_shown: false })
  }
}

</script>