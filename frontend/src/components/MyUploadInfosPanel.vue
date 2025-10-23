<template>
  <div>
    <div>
      <q-btn :label="t('contribute.add')" color="primary" @click="onAdd" /></div>
      <div v-if="contributeStore.uploadInfos.length === 0" class="q-mt-md">
        {{ t('contribute.no_files_uploaded') }}
      </div>
      <q-list v-else bordered separator class="q-mt-md" style="max-width: 800px;">
        <template v-for="uploadInfo in contributeStore.uploadInfos" :key="uploadInfo.path">
          <upload-info-item :upload-info="uploadInfo" @delete="onConfirmDelete" @comments="onShowComments" />
        </template>
      </q-list>
  </div>
</template>

<script setup lang="ts">
import UploadInfoItem from 'src/components/UploadInfoItem.vue';
import type { UploadInfo } from 'src/models';

const emit = defineEmits(['add', 'delete', 'comments']);

const { t } = useI18n();
const contributeStore = useContributeStore();

onMounted(async () => {
  await contributeStore.initMyUploadInfos();
});

function onAdd() {
  emit('add');
}

function onConfirmDelete(uploadInfo: UploadInfo) {
  emit('delete', uploadInfo);
}

function onShowComments(uploadInfo: UploadInfo) {
  emit('comments', uploadInfo);
}
</script>
