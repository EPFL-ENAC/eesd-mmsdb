<template>
    <div class="stone-carousel q-mb-md">
        <div class="q-mb-sm">
            <div class="q-mb-xs text-h6">Individual stones</div>
            <div class="q-mb-xs">Current file: {{ props.stones.files[index] }} ({{ index }}/{{ props.stones.files.length - 1 }})</div>
            <q-input dense v-model.number="index" label="Stone #" type="number" min="0" :max="props.stones.files.length - 1" filled />
        </div>

        <div class="carousel-controls">
            <q-btn flat round icon="chevron_left" @click="previousStone" />
            <div class="stone-image-container">
                <div v-if="currentStone">
                    <microstructure-view :ply-data="currentStone" :width="300" :height="300" />
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
import { useWallsStore, type WallStonesList } from 'stores/walls'
import MicrostructureView from 'src/components/MicrostructureView.vue'

const wallsStore = useWallsStore();
const props = defineProps<{
    stones: WallStonesList;
    preloadNext?: number;
    preloadPrevious?: number;
}>();

const index = ref(0);
const loading = ref(false);
const currentStone = ref<ArrayBuffer | null>(null);

function nextStone() {
    index.value = (index.value + 1) % props.stones.files.length;
}

function previousStone() {
    index.value = (index.value - 1 + props.stones.files.length) % props.stones.files.length;
}

async function getStoneAtIndex(i: number): Promise<ArrayBuffer | null> {
    const stonePath = `${props.stones.folder}/${props.stones.files[i] || ""}`;
    return await wallsStore.getWallStoneModel(true, stonePath);
}

async function setCurrentStone(i: number) {
    loading.value = true;

    currentStone.value = await getStoneAtIndex(i);

    // Preload next and previous stones, without awaiting them to not block ! The non-awaited nature is made explicit with the void operator.
    for (let offset = 1; offset <= (props.preloadNext || 0); offset++) {
        const nextIndex = (i + offset) % props.stones.files.length;
        void getStoneAtIndex(nextIndex);
    }
    for (let offset = 1; offset <= (props.preloadPrevious || 0); offset++) {
        const prevIndex = (i - offset + props.stones.files.length) % props.stones.files.length;
        void getStoneAtIndex(prevIndex);
    }

    loading.value = false;
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
