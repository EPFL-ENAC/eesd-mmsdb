<template>
  <div>
    <template v-if="state.status === 'loading'">
      <slot name="loading">
        <div class="loading">Loading…</div>
      </slot>
    </template>

    <template v-else-if="state.status === 'error'">
      <slot name="error" :error="state.error as E">
        <div class="error">Error: {{ state.error }}</div>
      </slot>
    </template>

    <template v-else-if="state.status === 'success'">
      <slot :value="state.value as T" />
    </template>

    <template v-else>
      <slot name="idle">
        <div class="idle">Idle</div>
      </slot>
    </template>
  </div>
</template>

<script setup lang="ts" generic="T, E">
import type { AsyncResult, AsyncResultState } from '../../core/asyncResult';
import { ref, onUnmounted, watch } from 'vue';

interface Props<T, E> {
  result: AsyncResult<T, E>;
}

const props = defineProps<Props<T, E>>();

// Reactive local state reflecting the AsyncResult’s internal state
const state = ref<AsyncResultState<T, E>>(props.result.state);

let unlisten: (() => void) | null = null;

onUnmounted(() => {
  if (unlisten) unlisten();
});

// In case prop changes (rare, but safe to handle)
watch(
  () => props.result,
  (newResult) => {
    if (unlisten) unlisten();
    state.value = newResult.state;
    unlisten = newResult.listen((res) => {
      state.value = res.state;
    });
  }
, { immediate: true }
);
</script>