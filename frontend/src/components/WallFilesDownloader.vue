<template>
    <q-option-group
      v-model="group"
      :options="options"
      type="toggle"
    />

    <q-btn
      class="q-mt-md"
      color="primary"
      label="Download Selected Files"
      @click="downloadSelectedFiles"
      :loading="loading"
      :disabled="group.length < 1 || loading"
    />
</template>

<script setup lang="ts">
import { useWallsStore, type WallStonesList } from 'stores/walls';
import { type DownloadableFile, downloadFilesAsZip } from 'src/utils/download';
import { ref } from 'vue'

const props = defineProps<{
    wallId: string;
    stones: WallStonesList | null;
}>();

const wallsStore = useWallsStore();

const group = ref<string[]>([])
const options = ref([
  { label: 'Wall microstructure (Full scale .ply)', value: 'wall-microstructure' },
  { label: 'All stones (each stone in a .ply)', value: 'all-stones' },
  { label: 'Stone geometric info (CSV)', value: 'stone-geometric-info' }
])

const loading = ref(false);

async function stoneToDownloadableFile(stoneId: string): Promise<DownloadableFile> {
    const ply = await wallsStore.getWallStoneModel(false, `${props.stones?.folder}/${stoneId}`);
    return { data: ply!, filename: `stones/stone_${stoneId}.ply`, mimeType: 'model/ply' };
}

async function downloadSelectedFiles() {
    loading.value = true;

    if (group.value.length < 1) {
        return;
    }

    const values: DownloadableFile[] = [];
    if (group.value.includes('wall-microstructure')) {
        const wallData = await wallsStore.getWall(false, props.wallId);
        if (wallData) {
            values.push({ data: wallData, filename: `wall_${props.wallId}_fullscale.ply`, mimeType: 'model/ply' });
        }
    }

    if (group.value.includes('all-stones')) {
        if (props.stones) {
            const stonesPromises = props.stones.files.map(stoneId => stoneToDownloadableFile(stoneId));
            const stones = await Promise.all(stonesPromises);
            values.push(...stones);
        }
    }

    if (group.value.includes('stone-geometric-info')) {
        const csv = await wallsStore.getWallPropertiesCSVFile(props.wallId);
        if (csv) {
            values.push({ data: csv, filename: `wall_${props.wallId}_properties.csv`, mimeType: 'text/csv' });
        }
    }

    // Trigger the download
    if (values.length < 1) {
        return;
    }

    await downloadFilesAsZip(values, `wall_${props.wallId}_files.zip`);

    loading.value = false;
}
</script>