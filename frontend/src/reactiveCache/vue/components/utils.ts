import { type AsyncResult } from "src/reactiveCache/core/result";
import AsyncResultLoader from "./AsyncResultLoader.vue";
import { h, type VNode } from "vue";

interface CustomSlots<E> {
    loading?: () => VNode;
    error?: (props: { error: E }) => VNode;
}

export function buildCustomAsyncResultLoader<T, E>(slots: CustomSlots<E>) {
    const comp = defineComponent({
        name: "CustomAsyncResultLoader",
        props: {
            result: {
                type: Object as () => AsyncResult<T, E>,
                required: true
            }
        },
        setup(props, context) {
            return () => {
                const renderLoading = context.slots.loading ?? slots.loading ?? (() => undefined);
                const renderError = context.slots.error ?? slots.error ?? (() => undefined);
                return h(
                    AsyncResultLoader,
                    { result: props.result },
                    {
                        default: context.slots.default ? (propsDefault: { value: T }) => context.slots.default!(propsDefault) : undefined,

                        loading: () => renderLoading(),
                        error: ((propsError: { error: E }) => renderError(propsError))
                    }
                )
            }
        }
    });

    return comp;
}
