<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <app-toolbar/>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      :mini="!leftDrawerOpen || miniStateLeft"
      show-if-above
      bordered
    >
      <div
        v-if="!$q.screen.lt.md"
        class="absolute"
        style="top: 10px; right: 10px"
      >
        <q-btn
          dense
          round
          unelevated
          :icon="miniStateLeft ? 'chevron_right' : 'chevron_left'"
          @click="miniStateLeft = !miniStateLeft"
        />
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import AppToolbar from 'src/components/AppToolbar.vue';

const $q = useQuasar();
const route = useRoute();

const leftDrawerOpen = ref(false);
const miniStateLeft = ref(false);
watch(() => route.meta.hasDrawer, (newValue) => {
  leftDrawerOpen.value = (newValue === true);
});

</script>
