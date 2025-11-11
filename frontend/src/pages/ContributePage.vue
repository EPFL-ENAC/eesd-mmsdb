<template>
  <q-page>
    <div class="q-pa-md">
      <div class="text-h3">{{ t('contribute.title') }}</div>
      <div v-if="contributeStore.userInfo">
        <q-btn
          class="q-mt-md"
          :label="t('contribute.logout')"
          color="primary"
          size="sm"
          @click="onLogout"
        />
        <pre>{{ contributeStore.userInfo }}</pre>
      </div>
      <div v-else>
        <q-btn
          class="q-mt-md"
          :label="t('contribute.login')"
          color="primary"
          size="sm"
          @click="onLogin"
        />
      </div>
      <q-tabs dense inline-label class="q-mt-md" align="left" v-model="tab">
        <q-tab name="my_uploads" :label="t('contribute.my_uploads')" />
        <q-tab name="all_uploads" icon="lock" :label="t('contribute.all_uploads')" />
      </q-tabs>
      <q-separator />
      <q-tab-panels v-model="tab">
        <q-tab-panel name="my_uploads" class="q-pl-none q-pr-none">
          <my-upload-infos-panel @add="onAdd" @delete="onConfirmDelete" @comments="onShowComments" />
        </q-tab-panel>
        <q-tab-panel name="all_uploads" class="q-pl-none q-pr-none">
          <upload-infos-panel :refresh="refresh" @delete="onConfirmDelete" @comments="onShowComments" />
        </q-tab-panel>
      </q-tab-panels>
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
import MyUploadInfosPanel from 'src/components/MyUploadInfosPanel.vue';
import UploadInfosPanel from 'src/components/UploadInfosPanel.vue';
import SimpleDialog from 'src/components/SimpleDialog.vue';
import type { UploadInfo } from 'src/models';

const { t } = useI18n();
const $q = useQuasar();
const contributeStore = useContributeStore();

const tab = ref('my_uploads');
const showDialog = ref(false);
const selectedInfo = ref<UploadInfo>();
const showConfirmDialog = ref(false);
const showCommentsDialog = ref(false);
const refresh = ref(0);
const fetchingUser = ref(false);

onMounted(() => {
  fetchingUser.value = true;
  contributeStore.fetchUserInfo().catch((error) => {
    console.error('Error fetching user info:', error);
  }).finally(() => fetchingUser.value = false);
})

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
    refresh.value += 1;
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

async function onLogin() {
  await contributeStore.login();
}

async function onLogout() {
  await contributeStore.logout();
}
</script>
