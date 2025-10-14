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
            <upload-info-item :upload-info="uploadInfo" />
          </template>
        </q-list>
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
import UploadInfoItem from 'src/components/UploadInfoItem.vue';
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
