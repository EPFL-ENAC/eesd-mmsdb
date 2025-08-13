<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <app-toolbar @toggle-left="toggleLeftDrawer" :has-drawer="hasDrawer" />
    </q-header>

    <q-drawer
      v-model="leftDrawerVisible"
      :mini="!leftDrawerOpen"
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
          :icon="leftDrawerOpen ? 'chevron_left' : 'chevron_right'"
          @click="leftDrawerOpen = !leftDrawerOpen"
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

const hasDrawer = computed(() => {
  return route.meta.hasDrawer === true;
});
const leftDrawerVisible = ref(hasDrawer.value && !$q.screen.lt.md);
const leftDrawerOpen = ref(hasDrawer.value);

watch(hasDrawer, (value) => {
  leftDrawerVisible.value = value && !$q.screen.lt.md;
  leftDrawerOpen.value = value;
});

watch(
  () => $q.screen.lt.md,
  (isLargeScreen) => {
    leftDrawerVisible.value = hasDrawer.value && isLargeScreen;
  }
);

function toggleLeftDrawer() {
  leftDrawerVisible.value = !leftDrawerVisible.value;
}
</script>

<style lang="scss" scoped>
.q-page {
  padding: 0.7rem;
}
</style>
