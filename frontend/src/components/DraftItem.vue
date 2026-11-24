<template>
  <q-expansion-item>
    <template v-slot:header>
      <q-item-section>
        <q-item-label>
          <q-badge color="accent" :title="draft.id" class="q-mr-sm">{{ `${draft.id.substring(0, 8)}...` }}</q-badge>
          {{ t('contribute.uploaded_by', { name: draft.contributor.name, email: draft.contributor.email }) }}
        </q-item-label>
        <q-item-label caption>{{ t('contribute.uploaded_files', { count: draft.files.length }) }}</q-item-label>
      </q-item-section>
      <q-item-section side>
        <q-badge :color="stateColor(draft.state)">{{ t(`contribute.state.${draft.state}`) }}</q-badge>
      </q-item-section>
    </template>
    <div class="q-px-md q-pb-md">
      <div>
        <q-badge color="info">{{ t(`contribute.type_options.${draft.contributor.type}`) }}</q-badge>
        {{ draft.contributor.affiliation ? ` [${draft.contributor.affiliation}]` : '' }}
        {{ draft.contributor.method ? ` - ${draft.contributor.method}` : '' }}
        {{ draft.contributor.reference ? ` - ${draft.contributor.reference}` : '' }}
      </div>
      <pre v-if="draft.contributor.comments" class="bg-grey-2 q-pa-md">{{ draft.contributor.comments }}</pre>
      <upload-files-panel :id="draft.id" :files="draft.files" />
      <div class="text-subtitle2 q-mt-md">{{ t('contribute.history') }}</div>
      <div v-if="draft.history.length === 0" class="text-caption">{{ t('contribute.no_history') }}</div>
      <ul v-else class="q-my-sm">
        <li v-for="(d, idx) in draft.history" :key="idx">
          {{ new Date(d.at).toLocaleString() }} - {{ d.by }}: {{ t(`contribute.state.${d.state}`) }}{{ d.comment ? ` (${d.comment})` : '' }}
        </li>
      </ul>
      <div v-if="actions.length" class="q-mt-md">
        <q-input v-model="comment" :label="t('contribute.decision_comment')" :hint="t('contribute.decision_comment_hint')" type="textarea" autogrow filled dense />
        <div class="q-mt-sm">
          <q-btn
            v-for="action in actions"
            :key="action.state"
            :label="t(`contribute.decision.${action.state}`)"
            :color="stateColor(action.state)"
            :disable="deciding || (action.needsComment && !comment.trim())"
            :loading="deciding"
            class="q-mr-sm"
            @click="onDecide(action.state)"
          />
        </div>
      </div>
    </div>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import type { Draft, DraftState } from 'src/models';
import { errorMessages, stateColor } from 'src/stores/contribute';
import UploadFilesPanel from './UploadFilesPanel.vue';

// The moves the backend allows; reject and withdraw need a comment.
const TRANSITIONS: Record<string, { state: DraftState; needsComment: boolean }[]> = {
  submitted: [{ state: 'accepted', needsComment: false }, { state: 'rejected', needsComment: true }],
  accepted: [{ state: 'published', needsComment: false }, { state: 'rejected', needsComment: true }],
  published: [{ state: 'withdrawn', needsComment: true }],
};

const props = defineProps<{
  draft: Draft;
}>();

const { t } = useI18n();
const $q = useQuasar();
const contributeStore = useContributeStore();

const comment = ref('');
const deciding = ref(false);
const actions = computed(() => TRANSITIONS[props.draft.state] || []);

async function onDecide(state: DraftState) {
  deciding.value = true;
  try {
    await contributeStore.decide(props.draft.id, state, comment.value.trim());
    comment.value = '';
    $q.notify({ type: 'positive', message: t('contribute.decision_success') });
  } catch (error) {
    console.error('Decision error:', error);
    $q.notify({ type: 'negative', message: errorMessages(error).join('\n'), multiLine: true });
  } finally {
    deciding.value = false;
  }
}
</script>
