<template>
  <q-layout view="hHh lpR fFf">
    <q-header bordered class="bg-white text-grey-10">
      <app-toolbar @toggle-left="toggleLeftDrawer" @toggle-right="toggleRightDrawer" />
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      :mini="!leftDrawerOpen || miniStateLeft"
      show-if-above
      bordered
    >
      <div v-if="!miniStateLeft">
        <layers-drawer />
      </div>
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

    <q-drawer
      v-if="route.path === '/data-hub'"
      v-model="rightDrawerOpen"
      :mini="!rightDrawerOpen || miniStateRight"
      :width="$q.screen.lt.md ? 300 : (showPlots ? 300 : 500)"
      side="right"
      show-if-above
      bordered
    >
      <div v-show="!miniStateRight" class="q-mt-xl">
        <div v-show="helpStore.show">
          <help-drawer />
          <div class="absolute" style="top: 10px; right: 20px">
            <q-btn dense round unelevated icon="close" @click="toggleShowHelp" />
          </div>
        </div>
        <div v-show="catalogStore.showStudyDetails">
          <study-details-drawer />
          <div class="absolute" style="top: 10px; right: 20px">
            <q-btn dense round unelevated icon="close" @click="toggleShowStudyDetails" />
          </div>
        </div>
        <div v-show="showPlots">
          <plots-drawer />
        </div>
      </div>
      <div
        v-if="!$q.screen.lt.md"
        class="absolute"
        style="top: 10px; left: 10px"
      >
        <q-btn
          dense
          round
          unelevated
          :icon="miniStateRight ? 'chevron_left' : 'chevron_right'"
          @click="miniStateRight = !miniStateRight"
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
import LayersDrawer from 'src/components/LayersDrawer.vue';
import PlotsDrawer from 'src/components/PlotsDrawer.vue';
import HelpDrawer from 'src/components/HelpDrawer.vue';
import StudyDetailsDrawer from 'src/components/StudyDetailsDrawer.vue';

const $q = useQuasar();
const helpStore = useHelpStore();
const catalogStore = useCatalogStore();
const route = useRoute();

const leftDrawerOpen = ref(false);
const rightDrawerOpen = ref(false);
const miniStateLeft = ref(false);
const miniStateRight = ref(false);

const showPlots = computed(() => {
  return !helpStore.show && !catalogStore.showStudyDetails;
});

watch(
  () => helpStore.show,
  (newValue) => {
    if (newValue) {
      rightDrawerOpen.value = true;
      miniStateRight.value = false;
    }
  },
);

watch(
  () => catalogStore.showStudyDetails,
  (newValue) => {
    if (newValue) {
      rightDrawerOpen.value = true;
      miniStateRight.value = false;
    }
  },
);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function toggleRightDrawer() {
  rightDrawerOpen.value = !rightDrawerOpen.value;
}

function toggleShowHelp() {
  helpStore.show = !helpStore.show;
}

function toggleShowStudyDetails() {
  catalogStore.showStudyDetails = !catalogStore.showStudyDetails;
}
</script>
