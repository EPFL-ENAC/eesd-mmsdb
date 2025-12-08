import { QSpinner } from "quasar";
import type { LineComputeTrace } from "src/models";
import { makeAsyncResultLoader } from "unwrapped/vue";

const quasarSpinner = () => h('div', { class: 'q-pa-md flex flex-center' }, [
    h(QSpinner, { size: '50px', color: 'primary' })
]);

export const ArrayBufferSpinnerLoader = makeAsyncResultLoader<ArrayBuffer>({
    loading: quasarSpinner
}, 'ArrayBufferSpinnerLoader');

export const LmtComputeTraceSpinnerLoader = makeAsyncResultLoader<LineComputeTrace>({
    loading: quasarSpinner
}, 'LmtComputeTraceSpinnerLoader');

export const test = defineComponent({
    name: 'TestComponent',
    setup() {
        return () => h('div', 'Test');
    }
});