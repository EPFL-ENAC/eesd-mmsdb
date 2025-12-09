<template>
  <div class="correlations-drawer-content">
    <div class="text-h6 q-mb-md">Tools</div>

    <q-tabs vertical inline-label :align="'left'" active-color="primary">
      <q-route-tab
        to="/quality-index/line-of-minimum-trace"
        icon="line_axis"
        label="Line of Minimum Trace"
        exact
      />
      <q-route-tab
        icon="calculate"
        to="/quality-index/mqi-calculator"
        label="MQI Calculator"
        exact
      />
    </q-tabs>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.correlations-drawer-content {
  height: 100%;
}

.text-subtitle2 {
  font-weight: 500;
  color: #424242;
}

.q-tab {
  justify-content: start;
}
</style>
