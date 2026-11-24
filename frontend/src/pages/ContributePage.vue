<template>
  <q-page>
    <div class="q-pa-md">
      <div class="text-h3 q-mb-md">{{ t('contribute.title') }}</div>
      <q-card v-if="contributeStore.userInfo" flat class="alert-info q-mb-md">
        <q-card-section class="q-pa-md row">
          <span>{{ t('contribute.user_info', { name: contributeStore.userInfo?.full_name, role: t(`contribute.role.${contributeStore.userInfo?.role || 'contributor'}`) }) }}</span>
          <q-btn
            no-caps
            outline
            icon="logout"
            class="on-right text-bold"
            :label="t('contribute.logout')"
            size="sm"
            @click="onLogout"
          />
        </q-card-section>
      </q-card>
      <q-tabs dense inline-label class="q-mt-md" align="left" v-model="tab">
        <q-tab name="my_uploads" :label="t('contribute.my_uploads')" />
        <q-tab name="all_uploads" icon="lock" :label="t('contribute.all_uploads')" />
      </q-tabs>
      <q-separator />
      <q-tab-panels v-model="tab">
        <q-tab-panel name="my_uploads" class="q-pl-none q-pr-none">
          <my-upload-infos-panel @add="onAdd" />
        </q-tab-panel>
        <q-tab-panel name="all_uploads" class="q-pl-none q-pr-none">
          <upload-infos-panel />
        </q-tab-panel>
      </q-tab-panels>
    </div>
    <contribute-dialog
      v-model="showDialog"
      size="lg"
    />
  </q-page>
</template>

<script setup lang="ts">
import ContributeDialog from 'src/components/ContributeDialog.vue';
import MyUploadInfosPanel from 'src/components/MyUploadInfosPanel.vue';
import UploadInfosPanel from 'src/components/UploadInfosPanel.vue';

const { t } = useI18n();
const contributeStore = useContributeStore();

const tab = ref('my_uploads');
const showDialog = ref(false);

onMounted(() => {
  contributeStore.fetchUserInfo().catch((error) => {
    console.error('Error fetching user info:', error);
  });
});

function onAdd() {
  showDialog.value = true;
}

async function onLogout() {
  await contributeStore.logout();
}
</script>
