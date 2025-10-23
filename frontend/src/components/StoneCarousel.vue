<template>
    <div class="stone-carousel q-mb-md">
        <div class="q-mb-sm">
            <div class="text-h6">Individual stones</div>
            <div v-if="stones">
                <q-badge class="q-mb-xs">{{ index }}/{{ stones.files.length - 1 }} : {{ stones.files[index] }}</q-badge>
                <q-slider v-model="index" :min="0" :max="stones.files.length - 1" color="primary" />
            </div>
            <div v-else>
                <q-skeleton type="QBadge" />
            </div>
        </div>

        <div class="carousel-wrapper">
            <div class="carousel-controls">
                <q-btn flat round icon="chevron_left" @click="previousStone" />
                <div class="stone-image-container">
                    <div v-if="currentStone">
                        <microstructure-view :ply-data="currentStone" :width="200" :height="200" />
                    </div>

                    <loading-overlay :visible="loading" />
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
import type { Table, WallStonesList } from 'src/models';

const wallsStore = useWallsStore();
const stonePropertiesStore = useStonePropertiesStore();

const props = defineProps<{
    wallId: string;
    preloadNext?: number;
    preloadPrevious?: number;
}>();


const index = ref(0);
const loading = ref(false);
const currentStone = ref<ArrayBuffer | null>(null);
const stones = ref<WallStonesList | null>(null);
const stonesProperties = ref<Table | null>(null);

function nextStone() {
    if (!stones.value) return;
    index.value = (index.value + 1) % stones.value.files.length;
}

function previousStone() {
    if (!stones.value) return;
    index.value = (index.value - 1 + stones.value.files.length) % stones.value.files.length;
}

async function getStoneAtIndex(i: number): Promise<ArrayBuffer | null> {
    if (!stones.value) return null;
    const stonePath = `${stones.value.folder}/${stones.value.files[i] || ""}`;
    return await wallsStore.getWallStoneModel(true, stonePath);
}

async function setCurrentStone(i: number) {
    loading.value = true;

    if (!stones.value) {
        stones.value = await wallsStore.getWallStonesList(props.wallId);
        if (!stones.value) {
            loading.value = false;
            return;
        }
    }

    currentStone.value = await getStoneAtIndex(i);

    // Preload next and previous stones, without awaiting them to not block ! The non-awaited nature is made explicit with the void operator.
    for (let offset = 1; offset <= (props.preloadNext || 0); offset++) {
        const nextIndex = (i + offset) % stones.value.files.length;
        void getStoneAtIndex(nextIndex);
    }
    for (let offset = 1; offset <= (props.preloadPrevious || 0); offset++) {
        const prevIndex = (i - offset + stones.value.files.length) % stones.value.files.length;
        void getStoneAtIndex(prevIndex);
    }

    if (i === index.value) { // Only hide the loading if we are still on the same stone (in case of fast navigation)
        loading.value = false;
    }
}

const currentStoneProperties = computed(() => {
    if (!stonesProperties.value) return null;

    const properties = stonesProperties.value
        .filter(col => !dimensionsColumnsStones.includes(col.name))
        .map(toDisplayedProperties(stonePropertiesStore, index.value));

    const dimensions = getDimensionsColumn(stonePropertiesStore, index.value, key => stonePropertiesStore.getColumnValues(props.wallId, key), true);

    properties.push({
        name: 'Dimensions',
        value: dimensions,
        unit: '',
    });

    return properties;
})

watch(index, async (newIndex) => {
    await setCurrentStone(newIndex);
});

onMounted(async () => {
    void setCurrentStone(index.value);
    stonesProperties.value = await stonePropertiesStore.getProperties(props.wallId);
});

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

.carousel-wrapper > div {
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
