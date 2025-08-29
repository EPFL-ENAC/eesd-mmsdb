<template>
  <q-drawer
    v-model="isOpen"
    side="left"
    bordered
    :width="300"
    :breakpoint="500"
    class="bg-grey-1"
  >
    <div class="drawer-content">
      <slot />
    </div>
  </q-drawer>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'

const $q = useQuasar()
const isOpen = ref(false)

function toggle() {
  isOpen.value = !isOpen.value
}

function open() {
  isOpen.value = true
}

function close() {
  isOpen.value = false
}

onMounted(() => {
  if ($q.screen.gt.sm) {
    isOpen.value = true
  }
})

defineExpose({
  toggle,
  open,
  close,
  isOpen: readonly(isOpen)
})
</script>

<style scoped>
.drawer-content {
  height: 100%;
  padding: 1rem;
}
</style>
