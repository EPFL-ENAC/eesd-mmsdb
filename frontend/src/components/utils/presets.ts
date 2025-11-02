import { QSpinner } from "quasar";
import { buildCustomAsyncResultLoader } from "src/reactiveCache/vue/components/utils";

export const SpinnerLoader = buildCustomAsyncResultLoader({
    loading: () => h('div', { class: 'q-pa-md flex flex-center' }, [
        h(QSpinner, { size: '50px', color: 'primary' })
    ])
});