<template>
  <simple-dialog v-model="showWallDialog" title="Compare walls" size="lg">
    <div v-if="wallIds" class="wall-dialog-content">
      <div class="text-caption q-mb-md">{{ wallIds.join(', ') }}</div>
      <q-table
        :columns="tableColumns"
        :rows="tableRows"
        row-key="name"
        :rows-per-page-options="[0]"
        flat
        bordered
        wrap-cells
        class="table"
      >
        <template #body-cell-image="props">
          <q-td :props="props">
            <q-img
              :src="props.row.image"
              ratio="1"
              spinner-color="primary"
              style="width: 48px; height: 48px; border-radius: 6px;"
            />
          </q-td>
        </template>
      </q-table>
    </div>
  </simple-dialog>
</template>

<script setup lang="ts">
import { usePropertiesStore } from 'stores/properties'
import { getDimensionsColumn, toDisplayedProperties } from 'src/utils/properties'
import SimpleDialog from 'src/components/SimpleDialog.vue'

const propertiesStore = usePropertiesStore()
const wallsStore = useWallsStore()

defineExpose({
  open,
})

function open(wallIdsParam: string[]) {
  wallIds.value = wallIdsParam
  showWallDialog.value = true
}

const showWallDialog = ref(false)
const wallIds = ref<string[]>([])
const wallImages = computed(() => wallsStore.wallImages)

const dialogColumns = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Vertical loading_GMQI_class", "In-plane_GMQI_class", "Out-of-plane_GMQI_class", "Average vertical LMT", "Average horizontal LMT", "Average shape factor"]

const tableColumns = computed(() => {
  return [
    {
      name: 'name',
      label: 'Wall ID',
      field: 'name'
    },
    {
      name: 'image',
      label: 'Image',
      field: 'image'
    },
    ...dialogColumns.map(col => {
      const display = toDisplayedProperties(propertiesStore, -1)({ name: col, values: [] })
      return { name: col, label: display.name, field: col }
    }),
    {
      name: 'dimensions',
      label: 'Dimensions',
      field: 'dimensions',
    }
  ]
})

const tableRows = computed(() => {
  const table = propertiesStore.properties.unwrapOrNull();
  if (!wallIds.value || !table) return [];

  const indices = wallIds.value
    .map(id => table.rowIndexInColumn("Wall ID", id))
    .filter((index): index is number => index !== undefined && index !== -1);
  
  return indices.map((index, i) => {
    const id = wallIds.value[i]!;
    const dimensions = getDimensionsColumn(propertiesStore, index, (col) => table.getColumnValues(col));
    return {
      name: id,
      image: wallImages.value[id],
      ...dialogColumns.reduce((acc, col) => {
        const value = table.getColumnValues(col)?.[index];
        acc[col] = value !== undefined ? toDisplayedProperties(propertiesStore, index)({ name: col, values: table.getColumnValues(col) || [] }).value : null;
        return acc;
      }, {} as Record<string, string | null>),
      dimensions: dimensions,
    }
  });
})

</script>

<style scoped>

.wall-dialog-content {
  max-width: 100%;
}

.microstructure-section {
  text-align: center;
}

.microstructure-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.microstructure-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.properties-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.property-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
}

.property-name {
  font-weight: 500;
  color: #424242;
  font-size: 0.875rem;
  margin-bottom: 4px;
}

.property-value {
  font-size: 1rem;
  color: #1976d2;
  font-weight: 600;
}

.table {
  /* constrain width for demo */
  max-width: 100%; 
}

/* Sticky first column cells */
.table:deep(th:first-child),
.table:deep(td:first-child) {
  position: sticky;
  left: 0;
  z-index: 1; /* base above normal cells */
  background-color: red; /* ensure opaque background */
  color: white;
}

.table:deep(th) {
  width: max-content;
  white-space: nowrap;
}

.table:deep(td) {
  width: max-content;
  white-space: nowrap;
  padding-left: 2rem;
  min-width: 5rem;
}

/* Optional: make the very first header cell appear above other sticky cells */
.table:deep(thead tr:first-child th:first-child) {
  z-index: 2; /* keep header above sticky td cells */
}
</style>
