<template>
  <q-page>
    <div class="q-pa-md">
      <h3>{{ t('contribute.title') }}</h3>
      <div class="q-mt-md">
        <div><q-btn :label="t('contribute.add')" color="primary" @click="onAdd" /></div>
        <div v-if="contributeStore.uploadInfos.length === 0" class="q-mt-md">
          {{ t('contribute.no_files_uploaded') }}
        </div>
        <q-list v-else bordered separator class="q-mt-md">
          <template v-for="uploadInfo in contributeStore.uploadInfos" :key="uploadInfo.path">
            <upload-info-item :upload-info="uploadInfo" @delete="onConfirmDelete" @comments="onShowComments" />
          </template>
        </q-list>
      </div>
    </div>
    <contribute-dialog
      v-model="showDialog"
      :info="selectedInfo"
      size="lg"
    />
    <q-dialog v-if="selectedInfo" v-model="showConfirmDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-icon name="warning" color="warning" size="2rem" class="q-mr-md" />
          <div>{{ t('contribute.delete_confirm', { name: selectedInfo.path }) }}</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat :label="t('cancel')" v-close-popup />
          <q-btn flat :label="t('delete')" color="negative" @click="onDelete" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <simple-dialog v-model="showCommentsDialog" :title="t('contribute.comments')" size="md">
      <div v-if="selectedInfo?.contribution?.comments">
        <pre class="bg-grey-2 q-pa-md">{{ selectedInfo.contribution.comments }}</pre>
      </div>
      <div v-else>
        {{ t('contribute.no_comments') }}
      </div>
    </simple-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import ContributeDialog from 'src/components/ContributeDialog.vue';
import UploadInfoItem from 'src/components/UploadInfoItem.vue';
import SimpleDialog from 'src/components/SimpleDialog.vue';
import type { UploadInfo } from 'src/models';

const { t } = useI18n();
const $q = useQuasar();
const contributeStore = useContributeStore();

const showDialog = ref(false);
const selectedInfo = ref<UploadInfo>();
const showConfirmDialog = ref(false);
const showCommentsDialog = ref(false);

onMounted(() => {
  contributeStore.initUploadInfos();
});

function onAdd() {
  selectedInfo.value = undefined;
  showDialog.value = true;
}

function onConfirmDelete(info: UploadInfo) {
  selectedInfo.value = info;
  showConfirmDialog.value = true;
}

async function onDelete() {
  try {
    await contributeStore.deleteUpload(selectedInfo.value!);
    $q.notify({ type: 'positive', message: t('contribute.upload_delete_success') });
  } catch (error) {
    console.error('Error deleting upload:', error);
    $q.notify({ type: 'negative', message: t('contribute.upload_delete_error') });
  }
}

function onShowComments(info: UploadInfo) {
  selectedInfo.value = info;
  showCommentsDialog.value = true;
}
</script>
