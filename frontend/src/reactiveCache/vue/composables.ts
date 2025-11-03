import { AsyncResult, type FlatChainFunction } from "../core/asyncResult";
import type { Result } from "../core/result";

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

export function useAsyncResultRefFromPromise<T, E>(promise: Promise<Result<T, E>>) {
  return useAsyncResultRef(AsyncResult.fromResultPromise(promise));
}

export type Action<T,E> = () => Promise<Result<T, E>>;
export function useImmediateAction<T, E>(action: Action<T, E>): Ref<AsyncResult<T, E>> {
  return useAsyncResultRefFromPromise(action());
}
export interface LazyActionReturn<T, E> {
  resultRef: Ref<AsyncResult<T, E>>;
  trigger: () => void;
}

export function useLazyAction<T, E>(action: Action<T, E>): LazyActionReturn<T, E> {
  const result = new AsyncResult<T, E>();
  const resultRef = useAsyncResultRef(result);

  const trigger = () => {
    result.updateFromResultPromise(action());
  }

  return { resultRef, trigger };
}

export function useReactiveAction<I, O, E>(input: I | Ref<I> | (() => I), pipe: FlatChainFunction<I, O, E>, options:{ immediate: boolean } = { immediate: true }): Ref<AsyncResult<O, E>> {
  const source = typeof input === 'function' ? computed(input as () => I) : toRef(input)

  const outputRef = ref<AsyncResult<O, E>>(new AsyncResult()) as Ref<AsyncResult<O, E>>;
  let unsub: (() => void) | null = null;

  watch(source, () => {
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