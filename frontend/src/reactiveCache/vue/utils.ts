// For overhaul stores

import { AsyncResult, type Pipe } from "../core/result";

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

export function useReactiveAsyncPipe<I, O, E>(input: I | Ref<I>, pipe: Pipe<I, O, E>, options:{ immediate: boolean } = { immediate: true }): Ref<AsyncResult<O, E>> {
  const inputRef = toRef(input);
  const outputRef = ref<AsyncResult<O, E>>(new AsyncResult()) as Ref<AsyncResult<O, E>>;
  let unsub: (() => void) | null = null;

  watch(inputRef, () => {
    unsub?.();
    const newOutput = pipe(inputRef.value);
    unsub = newOutput.listen((newState) => {
      outputRef.value.setState(newState.state);
      triggerRef(outputRef);
    });
  }, { immediate: options.immediate });

  try {
    onUnmounted(() => {
      unsub?.();
    });
  } catch {
    // ignore if onUnmounted is not available
  }

  return outputRef;
}