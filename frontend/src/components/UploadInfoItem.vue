<template>
  <q-item>
    <q-item-section>
      <q-item-label>
        <q-badge color="accent" :title="uploadInfo.path" class="q-mr-sm">{{ `${uploadInfo.path.substring(0, 8)}...` }}</q-badge>
      </q-item-label>
      <q-item-label caption>{{ new Date(uploadInfo.date).toLocaleString() }}</q-item-label>
      <q-item-label caption>{{ t('contribute.uploaded_files', { count: uploadInfo.files.length, size: uploadInfo.total_size }) }}</q-item-label>
      <q-item-label v-if="uploadInfo.contribution" caption>{{ t('contribute.uploaded_by', { name: uploadInfo.contribution.name, email: uploadInfo.contribution.email }) }}</q-item-label>
    </q-item-section>
    <q-item-section side>
      <q-btn
        :label="t('delete')"
        color="negative"
        flat
        rounded
        @click="onDelete(uploadInfo)"
      />
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import type { UploadInfo } from 'src/models';

const { t } = useI18n();
const $q = useQuasar();
const contributeStore = useContributeStore();

defineProps<{
  uploadInfo: UploadInfo;
}>();

async function onDelete(info: UploadInfo) {
  try {
    await contributeStore.deleteUpload(info);
    $q.notify({ type: 'positive', message: t('contribute.upload_delete_success') });
  } catch (error) {
    console.error('Error deleting upload:', error);
    $q.notify({ type: 'negative', message: t('contribute.upload_delete_error') });
  }
}
</script>
