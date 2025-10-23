<template>
  <q-item>
    <q-item-section top>
      <q-item-label>
        <q-badge color="accent" :title="uploadInfo.path" class="q-mr-sm">{{ `${uploadInfo.path.substring(0, 8)}...` }}</q-badge>
      </q-item-label>
      <q-item-label caption>
        {{ t('contribute.uploaded_by', { name: uploadInfo?.contribution?.name, email: uploadInfo?.contribution?.email }) }}
        {{ uploadInfo?.contribution?.affiliation ? ` [${uploadInfo.contribution.affiliation}]` : '' }}
        {{ t('contribute.uploaded_on', { date: new Date(uploadInfo.date).toLocaleString() }) }}
      </q-item-label>
      <q-item-label>
        <q-badge color="info">{{ t(`contribute.type_options.${uploadInfo.contribution?.type}`) }}</q-badge>
        {{ uploadInfo.contribution?.method ? ` - ${uploadInfo.contribution.method}` : '' }}
        {{ uploadInfo.contribution?.reference ? ` - ${uploadInfo.contribution.reference}` : '' }}
        <q-btn v-if="uploadInfo.contribution?.comments" flat dense icon="comment" size="sm" class="q-ml-sm" @click="onComments"/>
      </q-item-label>
      <upload-files-panel :upload-info="uploadInfo" />
    </q-item-section>

    <q-item-section side top>
      <q-btn
        :title="t('delete')"
        icon="delete"
        color="negative"
        flat
        rounded
        @click="onDelete()"
        class="q-mt-lg"
      />
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import type { UploadInfo } from 'src/models';
import UploadFilesPanel from './UploadFilesPanel.vue';

const { t } = useI18n();

const props = defineProps<{
  uploadInfo: UploadInfo;
}>();

const emit = defineEmits(['delete', 'comments']);

function onDelete() {
  emit('delete', props.uploadInfo);
}

function onComments() {
  emit('comments', props.uploadInfo);
}

</script>
