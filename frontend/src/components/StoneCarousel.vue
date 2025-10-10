<template>
    <div class="stone-carousel q-mb-md">
        <div class="q-mb-sm">
            <div class="text-h6">Individual stones</div>
            <div v-if="stones">
                <q-badge class="q-mb-xs">{{ index }}/{{ stones.files.length - 1 }} : {{ stones.files[index] }}</q-badge>
                <q-slider v-model="index" :min="0" :max="stones.files.length - 1" color="primary" />
            </div>
            <div v-else>Loading...</div>
        </div>

        <div class="carousel-controls">
            <q-btn flat round icon="chevron_left" @click="previousStone" />
            <div class="stone-image-container">
                <div v-if="currentStone">
                    <microstructure-view :ply-data="currentStone" :width="200" :height="200" />
                </div>

                <div :class="['spinner-container', loading ? 'shown' : '']">
                    <q-spinner color="primary" size="3em" />
                </div>
            </div>
            <q-btn flat round icon="chevron_right" @click="nextStone" />
        </div>
    </div>

</template>

<script setup lang="ts">
import { useWallsStore } from 'stores/walls'
import MicrostructureView from 'src/components/MicrostructureView.vue'
import type { WallStonesList } from 'src/models';

const wallsStore = useWallsStore();
const props = defineProps<{
    wallId: string;
    // stones: WallStonesList;
    preloadNext?: number;
    preloadPrevious?: number;
}>();

const index = ref(0);
const loading = ref(false);
const currentStone = ref<ArrayBuffer | null>(null);
const stones = ref<WallStonesList | null>(null);

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

watch(index, async (newIndex) => {
    await setCurrentStone(newIndex);
});

onMounted(async () => {
    await setCurrentStone(index.value);
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

.spinner-container {
    position: absolute;
    inset: 0;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(3px);
    opacity: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    pointer-events: none;
    transition: all 0.5s;
}

.spinner-container.shown {
    opacity: 1;
}
</style>
