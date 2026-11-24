<template>
  <div>
    <div v-if="!contributeStore.userInfo">
      <div>{{ t('contribute.authentication_required') }}</div>
      <div class="q-mt-md">
        <q-btn
          :label="t('contribute.login')"
          color="primary"
          @click="onLogin"
        />
      </div>
    </div>
    <div v-else-if="contributeStore.userInfo.role !== 'admin'">
      <div>{{ t('contribute.not_allowed_all_uploads') }}</div>
    </div>
    <div v-else>
      <q-select
        v-model="state"
        :options="stateOptions"
        :label="t('contribute.state_filter')"
        emit-value
        map-options
        filled
        dense
        style="max-width: 300px;"
        @update:model-value="onShowAll"
      />
      <q-spinner v-if="loading" size="2rem" class="q-mt-md" />
      <div v-else class="q-mt-md">
        <div v-if="contributeStore.drafts.length === 0">
          {{ t('contribute.no_files_uploaded') }}
        </div>
        <q-list v-else bordered separator style="max-width: 800px;">
          <draft-item v-for="draft in contributeStore.drafts" :key="draft.id" :draft="draft" />
        </q-list>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import DraftItem from 'src/components/DraftItem.vue';
import type { DraftState } from 'src/models';
import { errorMessages } from 'src/stores/contribute';

const { t } = useI18n();
const $q = useQuasar();
const contributeStore = useContributeStore();

const STATES: DraftState[] = ['submitted', 'accepted', 'rejected', 'published', 'withdrawn'];

const loading = ref(false);
const state = ref<DraftState | null>('submitted');
const stateOptions = computed(() => [
  { label: t('contribute.state_all'), value: null },
  ...STATES.map((s) => ({ label: t(`contribute.state.${s}`), value: s })),
]);

onMounted(onInit);

watch(() => contributeStore.userInfo, () => {
  onInit();
});

function onInit() {
  if (contributeStore.userInfo?.role !== 'admin') return;
  onShowAll();
}

function onShowAll() {
  loading.value = true;
  contributeStore.fetchDrafts(state.value || undefined).catch((error) => {
    console.error('Error fetching drafts:', error);
    $q.notify({ type: 'negative', message: `${t('contribute.upload_info_fetch_error')} ${errorMessages(error).join(' ')}` });
  }).finally(() => {
    loading.value = false;
  });
}

async function onLogin() {
  await contributeStore.login();
}

</script>
