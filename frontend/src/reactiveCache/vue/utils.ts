// For overhaul stores

import { AsyncResult, type ResultState, type Pipe } from "../core/result";

export function useAsyncResultRef<T, E>(asyncResult: AsyncResult<T, E>) {
  const state = ref<AsyncResult<T, E>>(asyncResult) as Ref<AsyncResult<T, E>>;

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

export function useAsyncResultRefFromPromise<T, E>(promise: Promise<ResultState<T, E>>) {
  return useAsyncResultRef(AsyncResult.fromResultPromise(promise));
}

export function useLazyAction<T, E>(action: () => Promise<ResultState<T, E>>): { resultRef: Ref<AsyncResult<T, E>>, trigger: () => void } {
  const result = new AsyncResult<T, E>();
  const resultRef = useAsyncResultRef(result);

  const trigger = () => {
    result.updateFromResultPromise(action());
  }

  return { resultRef, trigger };
}

export function useReactiveAsyncPipe<I, O, E>(input: I | Ref<I> | (() => I), pipe: Pipe<I, O, E>, options:{ immediate: boolean } = { immediate: true }): Ref<AsyncResult<O, E>> {
  const source = typeof input === 'function' ? computed(input as () => I) : toRef(input)

  const outputRef = ref<AsyncResult<O, E>>(new AsyncResult()) as Ref<AsyncResult<O, E>>;
  let unsub: (() => void) | null = null;

  watch(source, () => {
    console.log("useReactiveAsyncPipe: source changed, updating outputRef")
    unsub?.();
    const newOutput = pipe(source.value);
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