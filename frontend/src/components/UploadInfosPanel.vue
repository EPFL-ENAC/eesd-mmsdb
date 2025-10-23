<template>
  <div>
    <div v-if="!contributeStore.hasApiKey">
      <div>{{ t('contribute.api_key_required') }}</div>
      <div class="q-mt-md">
        <q-input
          v-model="apiKey"
          :label="t('contribute.api_key_label')"
          :type="isPwd ? 'password' : 'text'"
          filled
          style="max-width: 400px;"
          @keyup.enter="setApiKey"
        >
          <template v-slot:append>
            <q-icon
              :name="isPwd ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click="isPwd = !isPwd"
            />
          </template>
        </q-input>
        <q-btn
          class="q-mt-md"
          :label="t('contribute.authenticate')"
          :disable="!apiKey"
          color="primary"
          @click="setApiKey"
        />
      </div>
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
const apiKey = ref('');
const isPwd = ref(true);
const refresh = ref(props.refresh);

onMounted(onShowAll);

watch(() => props.refresh, () => {
  refresh.value = props.refresh;
  onShowAll();
});

function onShowAll() {
  if (contributeStore.hasApiKey === false) {
    return;
  }
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

function setApiKey() {
  if (!apiKey.value || apiKey.value.length === 0) {
    return;
  }
  contributeStore.setApiKey(apiKey.value);
  onShowAll();
}

</script>
