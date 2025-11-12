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
      <q-spinner v-if="loading" size="2rem" class="q-mt-md" />
      <div v-else>
        <div v-if="contributeStore.allUploadInfos.length === 0">
          {{ t('contribute.no_files_uploaded') }}
        </div>
        <q-list v-else bordered separator style="max-width: 800px;">
          <template v-for="uploadInfo in contributeStore.allUploadInfos" :key="uploadInfo.path">
            <upload-info-item :upload-info="uploadInfo" @delete="onConfirmDelete" @comments="onShowComments" />
          </template>
        </q-list>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import UploadInfoItem from 'src/components/UploadInfoItem.vue';
import type { UploadInfo } from 'src/models';

const { t } = useI18n();
const $q = useQuasar();
const contributeStore = useContributeStore();

const props = defineProps<{
  refresh: number;
}>();
const emit = defineEmits(['delete', 'comments']);

const loading = ref(false);

onMounted(onInit);

watch(() => props.refresh, () => {
  onInit();
});

function onInit() {
  if (!contributeStore.userInfo) return;
  onShowAll();
}

function onShowAll() {
  loading.value = true;
  contributeStore.initUploadInfos().catch((error) => {
    console.error('Error fetching all upload infos:', error);
    $q.notify({ type: 'negative', message: t('contribute.upload_info_fetch_error') });
  }).finally(() => {
    loading.value = false;
  });
}

function onConfirmDelete(uploadInfo: UploadInfo) {
  emit('delete', uploadInfo);
}

function onShowComments(uploadInfo: UploadInfo) {
  emit('comments', uploadInfo);
}

async function onLogin() {
  await contributeStore.login();
}

</script>
