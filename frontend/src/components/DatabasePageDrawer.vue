<template>
  <div class="database-drawer-content">
    <div class="text-h6 q-mb-md">Filters</div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-sm">Material Properties</div>
      <q-select
        v-model="selectedProperty"
        :options="propertyOptions"
        label="Select Property"
        outlined
        dense
        class="q-mb-md"
      />
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-sm">Wall ID Range</div>
      <q-input
        v-model="wallIdFilter"
        label="Filter by Wall ID"
        outlined
        dense
        class="q-mb-md"
      />
    </div>

    <div class="filter-section">
      <q-btn
        label="Clear Filters"
        color="grey"
        outline
        size="sm"
        class="full-width q-mb-sm"
        @click="clearFilters"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePropertiesStore } from 'stores/properties'

const propertiesStore = usePropertiesStore()

const selectedProperty = ref(null)
const wallIdFilter = ref('')

// Get available property options
const propertyOptions = computed(() => {
  if (!Array.isArray(propertiesStore.properties)) return []

  const allProperties = propertiesStore.properties.flatMap(entry =>
    entry.properties.map(p => p.name)
  )

  return [...new Set(allProperties)].map(name => ({
    label: name,
    value: name
  }))
})

function clearFilters() {
  selectedProperty.value = null
  wallIdFilter.value = ''
}

</script>

<style scoped>
.database-drawer-content {
  height: 100%;
}

.filter-section {
  margin-bottom: 1.5rem;
}

.text-subtitle2 {
  font-weight: 500;
  color: #424242;
}
</style>

