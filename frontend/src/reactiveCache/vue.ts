// For overhaul stores

import { AsyncResult, type PipeFunction } from "./result";

export function useAsyncResultRef<T, E>(asyncResult: AsyncResult<T, E>) {
  const state = ref<AsyncResult<T, E>>(asyncResult);

  const unsub = asyncResult.listen(() => {
    triggerRef(state);
  });

  try {
    onUnmounted(() => {
      unsub();
    });
  } catch {
    // ignore if onUnmounted is not available
  }

  return state;
}

export function useReactiveAsyncPipe<I, O, E>(input: Ref<I>, fn: PipeFunction<I, O, E>) {
  const outputRef = ref<AsyncResult<O, E>>(new AsyncResult());
  let unsub: (() => void) | null = null;

  watch(input, () => {
    unsub?.();
    const newOutput = AsyncResult.fromValue(input.value).pipe(fn);
    unsub = newOutput.listen((newState) => {
      outputRef.value.setState(newState.state);
      triggerRef(outputRef);
    });
  }, { immediate: true });

  try {
    onUnmounted(() => {
      unsub?.();
    });
  } catch {
    // ignore if onUnmounted is not available
  }

  return outputRef;
}