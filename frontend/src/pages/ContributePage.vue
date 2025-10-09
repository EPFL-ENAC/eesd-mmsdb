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
                />
              </q-item-section>
            </q-item>
          </template>
        </q-list>
        <pre>{{  contributeStore.uploadInfos }}</pre>
      </div>
    </div>
    <contribute-dialog
      v-model="showDialog"
      :info="selectedInfo"
      size="lg"
    >
  </contribute-dialog>
</q-page>
</template>

<script setup lang="ts">
import ContributeDialog from 'src/components/ContributeDialog.vue';
import type { UploadInfo } from 'src/models';

const { t } = useI18n();
const contributeStore = useContributeStore();

const showDialog = ref(false);
const selectedInfo = ref<UploadInfo>();

onMounted(() => {
  contributeStore.initUploadInfos();
});

function onAdd() {
  selectedInfo.value = undefined;
  showDialog.value = true;
}
</script>
