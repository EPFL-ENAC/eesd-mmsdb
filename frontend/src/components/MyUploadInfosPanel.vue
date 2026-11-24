<template>
  <div>
    <div>
      <q-btn :label="t('contribute.add')" color="primary" @click="onAdd" />
      <q-btn flat icon="refresh" :title="t('contribute.refresh')" :loading="loading" class="q-ml-sm" @click="onRefresh" />
    </div>
    <div class="text-caption q-mt-sm">{{ t('contribute.my_uploads_info') }}</div>
    <div v-if="contributeStore.myContributions.length === 0" class="q-mt-md">
      {{ t('contribute.no_files_uploaded') }}
    </div>
    <q-list v-else bordered separator class="q-mt-md" style="max-width: 800px;">
      <q-item v-for="item in contributeStore.myContributions" :key="item.id">
        <q-item-section>
          <q-item-label>
            <q-badge color="accent" :title="item.id" class="q-mr-sm">{{ `${item.id.substring(0, 8)}...` }}</q-badge>
            {{ item.name }}
          </q-item-label>
          <q-item-label caption>{{ t('contribute.uploaded_on', { date: new Date(item.date).toLocaleString() }) }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge :color="stateColor(item.state)">{{ t(`contribute.state.${item.state}`) }}</q-badge>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import { stateColor } from 'src/stores/contribute';

const emit = defineEmits(['add']);

const { t } = useI18n();
const contributeStore = useContributeStore();
const loading = ref(false);

onMounted(onRefresh);

async function onRefresh() {
  loading.value = true;
  try {
    await contributeStore.initMyContributions();
  } finally {
    loading.value = false;
  }
}

function onAdd() {
  emit('add');
}
</script>
