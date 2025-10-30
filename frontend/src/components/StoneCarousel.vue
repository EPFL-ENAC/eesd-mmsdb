<template>
    <div class="stone-carousel q-mb-md">
        <div class="q-mb-sm">
            <div class="text-h6">Individual stones</div>
            <div v-if="stonesList.state.status === 'success'">
                <q-badge class="q-mb-xs">{{ index }}/{{ stonesList.state.value.files.length - 1 }} : {{
                    stonesList.state.value.files[index] }}</q-badge>
                <q-slider v-model="index" :min="0" :max="stonesList.state.value.files.length - 1" color="primary" />
            </div>
            <div v-else>
                <q-skeleton type="QBadge" />
            </div>
        </div>

        <div class="carousel-wrapper">
            <div class="carousel-controls">
                <q-btn flat round icon="chevron_left" @click="previousStone" />
                <div class="stone-image-container">
                    <microstructure-view :ply-data="currentStone.unwrapOrNull()"
                        :orientation="props.orientation || null" :width="200" :height="200" />

                    <loading-overlay :visible="currentStone.state.status === 'loading'" />
                </div>
                <q-btn flat round icon="chevron_right" @click="nextStone" />
            </div>

            <div>
                <div v-if="currentStoneProperties" class="stone-infos">
                    <div v-for="prop in currentStoneProperties" :key="prop.name" class="q-mb-sm">
                        <div class="text-subtitle2 small-line-height">{{ prop.name }}</div>
                        <div class="text-body1">{{ prop.value }} {{ prop.unit }}</div>
                    </div>
                </div>
                <div v-else>
                    <q-skeleton width="100%" height="200px" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useWallsStore } from 'stores/walls'
import { toDisplayedProperties, getDimensionsColumn, dimensionsColumnsStones } from 'src/utils/properties'
import MicrostructureView from 'src/components/MicrostructureView.vue'
import LoadingOverlay from './LoadingOverlay.vue';
import { useReactiveAsyncPipe } from 'src/reactiveCache/vue/utils';

const wallsStore = useWallsStore();
const stonePropertiesStore = useStonePropertiesStore();

const props = defineProps<{
    wallId: string;
    orientation?: string | null;
    preloadNext?: number;
    preloadPrevious?: number;
}>();

const index = ref(0);

const stonesPropertiesTable = useReactiveAsyncPipe(props.wallId, (wallId) => stonePropertiesStore.getProperties(wallId));
const stonesList = useReactiveAsyncPipe(props.wallId, (wallId: string) => wallsStore.getWallStonesList(wallId));
const currentStone = useReactiveAsyncPipe(index, (i: number) => getStoneAtIndex(i));

defineExpose({
    currentStone,
});

function nextStone() {
    const stones = stonesList.value.unwrapOrNull();
    if (!stones) return;
    index.value = (index.value + 1) % stones.files.length;
}

function previousStone() {
    const stones = stonesList.value.unwrapOrNull();
    if (!stones) return;
    index.value = (index.value - 1 + stones.files.length) % stones.files.length;
}

function getStoneAtIndex(i: number) {
    return stonesList.value.flatChain((stones) => {
        return wallsStore.getWallStoneModelFromStoneListAndIndex(true, stones, i, {
            after: props.preloadNext || 0,
            before: props.preloadPrevious || 0,
        })
    });
}

const currentStoneProperties = computed(() => {
    const table = stonesPropertiesTable.value.unwrapOrNull();
    if (!table) return null;

    const i = table.rowIndexInColumn("Stone ID", `${props.wallId}_stone_${index.value}.ply`);
    if (i === undefined) return null;

    const filteredProperties = table
        .filterColumns(col => !dimensionsColumnsStones.includes(col.name))
        .map(toDisplayedProperties(stonePropertiesStore, i));

    const dimensions = getDimensionsColumn(stonePropertiesStore, i, key => table.getColumnValues(key), true);

    filteredProperties.push({
        name: 'Dimensions',
        value: dimensions,
        unit: '',
    });

    return filteredProperties;
})

</script>

<style scoped>
.carousel-controls {
    display: flex;
    align-items: center;
    justify-content: center;
}

.carousel-controls .stone-image-container {
    position: relative;
}

.carousel-wrapper {
    display: flex;
    gap: 16px;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
}

.carousel-wrapper>div {
    flex: 1 1 300px;
}

.stone-infos {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 8px 12px;
}

.small-line-height {
    line-height: 1;
}
</style>
