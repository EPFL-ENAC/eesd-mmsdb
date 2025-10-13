<template>
    <q-option-group v-model="group" :options="options" type="toggle" />

    <q-btn class="q-mt-md" color="primary" label="Download Selected Files" @click="downloadSelectedFiles"
        :loading="loading" :disabled="group.length < 1 || loading" />
</template>

<script setup lang="ts">
import { useWallsStore } from 'stores/walls';
import { type DownloadableFile, downloadFilesAsZip } from 'src/utils/download';
import { ref } from 'vue'

const props = defineProps<{
    wallId: string;
}>();

const wallsStore = useWallsStore();

const group = ref<string[]>([])
const options = ref([
    { label: 'Wall microstructure (Full scale .ply)', value: 'wall-microstructure' },
    { label: 'All stones (each stone in a .ply)', value: 'all-stones' },
    { label: 'Stone geometric info (CSV)', value: 'stone-geometric-info' }
])

const loading = ref(false);

async function getWallMicrostructureFile(): Promise<DownloadableFile | null> {
    const wallData = await wallsStore.getWall(false, props.wallId);
    if (!wallData) return null;
    return { data: wallData, filename: `wall_${props.wallId}_fullscale.ply`, mimeType: 'model/ply' };
}

async function getAllStonesFiles(): Promise<DownloadableFile[]> {
    const stones = await wallsStore.getWallStonesList(props.wallId);
    if (!stones) return [];

    const stoneToDownloadableFile = async (stoneId: string): Promise<DownloadableFile> => {
        const ply = await wallsStore.getWallStoneModel(false, `${stones?.folder}/${stoneId}`);
        return { data: ply!, filename: `stones/stone_${stoneId}`, mimeType: 'model/ply' };
    }

    const promises = stones.files.map(stoneId => stoneToDownloadableFile(stoneId));
    return await Promise.all(promises);
}

async function getStoneGeometryInfo(): Promise<DownloadableFile | null> {
    const csv = await wallsStore.getWallPropertiesCSVFile(props.wallId);
    if (!csv) return null;
    return { data: csv, filename: `wall_${props.wallId}_properties.csv`, mimeType: 'text/csv' };
}

async function downloadSelectedFiles() {
    if (group.value.length < 1) {
        return;
    }

    loading.value = true;

    const promises = [];

    if (group.value.includes('wall-microstructure')) {
        promises.push(getWallMicrostructureFile());
    }

    if (group.value.includes('all-stones')) {
        promises.push(getAllStonesFiles());
    }

    if (group.value.includes('stone-geometric-info')) {
        promises.push(getStoneGeometryInfo());
    }

    const values: DownloadableFile[] = (await Promise.all(promises)).filter((v) => v !== null).flat(); // needs to be flattened because of the array of stones

    // Trigger the download
    if (values.length < 1) {
        loading.value = false;
        return;
    }

    await downloadFilesAsZip(values, `wall_${props.wallId}_files.zip`);

    loading.value = false;
}
</script>
