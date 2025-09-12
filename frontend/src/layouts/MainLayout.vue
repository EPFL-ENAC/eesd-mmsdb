<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <app-toolbar @toggle-left="toggleLeftDrawer" :has-drawer="hasDrawer" />
    </q-header>

    <left-drawer v-if="hasDrawer" ref="leftDrawerRef" @drawer-toggled="onDrawerToggled">
      <router-view name="drawer" />
    </left-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import AppToolbar from 'src/components/AppToolbar.vue';
import LeftDrawer from 'src/components/LeftDrawer.vue';

const $q = useQuasar();
const route = useRoute();
const leftDrawerRef = ref<InstanceType<typeof LeftDrawer> | null>(null);

const hasDrawer = computed(() => {
  return route.meta.hasDrawer === true;
});

watch(hasDrawer, async (value) => {
  if (value) {
    await nextTick(() => {
      if (leftDrawerRef.value) {
        if ($q.screen.gt.sm) {
          leftDrawerRef.value.open();
        }
      }
    });
  } else {
    await nextTick(() => {
      if (leftDrawerRef.value) {
        leftDrawerRef.value.close();
      }
    });
  }
}, { immediate: true });

function toggleLeftDrawer() {
  if (leftDrawerRef.value) {
    leftDrawerRef.value.toggle();
  }
}

function onDrawerToggled(isOpen: boolean) {
  setTimeout(() => {
    window.dispatchEvent(new CustomEvent('drawer-toggled', { detail: { isOpen } }))
  }, 200) // Small delay to allow drawer animation to complete
}
</script>

<style lang="scss" scoped>
.q-page {
  padding: 0.7rem;
}
</style>
