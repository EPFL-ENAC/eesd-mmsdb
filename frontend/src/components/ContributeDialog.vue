<template>
  <q-dialog :persistent="uploading" :maximized="$q.screen.lt.sm" v-model="showDialog" @hide="onHide">
    <q-card :style="$q.screen.lt.sm ? '' : `width: ${size === 'lg' ? '900px' : size === 'md' ? '600px' : '500px'}; max-width: 90vw`">
      <q-card-actions v-if="$q.screen.lt.sm" align="right">
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-card-section>
        <div class="text-h6 q-mb-sm">
          {{ t('contribute.title') }}
        </div>
        <div>
          <q-form ref="form">
            <div class="row q-col-gutter-md">
              <div class="col">
                <q-input
                  v-model="contribution.name"
                  :label="t('contribute.name') + ' *'"
                  :hint="t('contribute.name_hint')"
                  type="text"
                  filled
                  :rules="[val => !!val || t('contribute.name_required')]"
                  class="q-mb-md"
                />
                <q-input
                  v-model="contribution.email"
                  :label="t('contribute.email') + ' *'"
                  :hint="t('contribute.email_hint')"
                  type="text"
                  :rules="[(v) => /.+@.+\..+/.test(v) || t('contribute.email_invalid')]"
                  lazy-rules
                  filled
                  class="q-mb-md"
                />
                <q-input
                  v-model="contribution.affiliation"
                  :label="t('contribute.affiliation')"
                  :hint="t('contribute.affiliation_hint')"
                  type="text"
                  filled
                  class="q-mb-md"
                />
              </div>
              <div class="col">
                <q-select
                  v-model="contribution.type"
                  :options="typeOptions"
                  :label="t('contribute.type')"
                  :hint="t('contribute.type_hint')"
                  filled
                  emit-value
                  map-options
                  class="q-mb-md"
                />
                <q-input
                  v-model="contribution.method"
                  :label="t('contribute.method')"
                  :hint="t('contribute.method_hint')"
                  type="text"
                  filled
                  class="q-mb-md"
                />
                <q-input
                  v-model="contribution.reference"
                  :label="t('contribute.reference')"
                  :hint="t('contribute.reference_hint')"
                  type="text"
                  filled
                  class="q-mb-md"
                />
              </div>
            </div>
            <q-input
              v-model="contribution.comments"
              :label="t('contribute.comments')"
              type="textarea"
              autogrow
              filled
              class="q-mb-md"
            />
            <q-file
              v-model="files"
              :label="t('contribute.files') + ' *'"
              :hint="t('contribute.files_hint')"
              filled
              clearable
              counter
              multiple
              :rules="[val => val && val.length > 0 || t('contribute.files_required')]"
              accept=".ply,.obj,.stl,.zip"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
          </q-form>
        </div>
      </q-card-section>
      <q-card-actions v-if="$q.screen.gt.xs" align="right">
        <q-spinner-dots v-if="uploading" color="primary" size="md" class="q-mr-md" />
        <q-btn flat :disable="uploading" :label="t('cancel')" @click="onHide" />
        <q-btn flat :disable="uploading" :label="t('contribute.upload')" color="primary" @click="onUpload" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { QForm, useQuasar } from 'quasar';
import type { UploadInfo, Contribution } from 'src/models';

interface Props {
  modelValue: boolean;
  info?: UploadInfo | undefined;
  size?: string;
}
const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue']);

const $q = useQuasar();
const { t } = useI18n();
const contributeStore = useContributeStore();

const uploading = ref(false);
const form = ref<QForm>();
const showDialog = ref(props.modelValue);
const contribution = ref<Contribution>({} as Contribution);
const files = ref<File[]>([]);

const typeOptions = computed(() => [
  { label: t('contribute.type_options.real'), value: 'real' },
  { label: t('contribute.type_options.virtual'), value: 'virtual' },
]);

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value;
    if (value) {
      // Reset form if needed
      contribution.value = JSON.parse(JSON.stringify(props.info?.contribution || { type: 'real' })) as Contribution;
      files.value = [];
      form.value?.resetValidation();
    }
  },
);

function onHide() {
  emit('update:modelValue', false);
}

async function onUpload() {
  // Validate form
  if (form.value && await form.value.validate() === false) {
    $q.notify({ type: 'negative', message: t('contribute.form_invalid') });
    return;
  }
  // Handle the file upload and form submission
  try {
    uploading.value = true;
    await contributeStore.upload(files.value, contribution.value);
    $q.notify({ type: 'positive', message: t('contribute.upload_success') });
    emit('update:modelValue', false);
  } catch (error) {
    console.error('Upload error:', error);
    $q.notify({ type: 'negative', message: t('contribute.upload_error') });
  } finally {
    uploading.value = false;
  }
}
</script>
