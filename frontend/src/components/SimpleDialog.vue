<template>
  <q-dialog :maximized="$q.screen.lt.sm" v-model="showDialog" @hide="onHide">
    <q-card :style="$q.screen.lt.sm ? '' : `width: ${size === 'md' ? '600px' : '500px'}; max-width: 80vw`">
      <q-card-actions v-if="$q.screen.lt.sm" align="right">
        <q-btn flat icon="close" color="primary" v-close-popup />
      </q-card-actions>
      <q-card-section>
        <div v-if="title" class="text-h6 q-mb-sm">
          {{ title }}
        </div>
        <div v-if="props.content">
          <q-markdown no-heading-anchor-links :src="props.content" />
        </div>
        <slot></slot>
      </q-card-section>
      <q-card-actions v-if="$q.screen.gt.xs" align="right">
        <q-btn flat :label="t('close')" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';

interface Props {
  modelValue: boolean;
  title?: string;
  size?: string;
  content?: string;
}
const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue']);

const $q = useQuasar();
const { t } = useI18n();

const showDialog = ref(props.modelValue);

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value;
  },
);

function onHide() {
  emit('update:modelValue', false);
}
</script>
