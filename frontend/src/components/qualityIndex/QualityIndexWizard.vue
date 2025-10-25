<template>
  <q-stepper v-model="step" vertical flat animated>
    <q-step :name="1" title="Masonry Typology">
      <q-select v-model="masonryType" :options="masonryTypologiesSelectOptions" label="Select the basic masonry typology" filled />

      <q-stepper-navigation>
        <q-btn @click="step++" color="primary" label="Continue" />
      </q-stepper-navigation>
    </q-step>

    <q-step :name="2" title="Text Parameters">
      <div v-for="param in textParametersKeys" :key="param" class="q-mb-md">
        <div :class="{ 'with-explainer': param === 'HJ' }">
          <q-select v-model="selections[param]" :options="parametersTextSelectOptions[param]" :label="textParameterLabel[param]" filled />
          <img src="/Bed_joints_classification.webp" alt="Bed Joints classification" v-if="param === 'HJ'" />
        </div>
      </div>

      <div class="q-mb-md">
        <q-toggle v-model="wcQuantitative" label="Vertical section accessible for quantitative analysis?" />
        <div v-if="wcQuantitative" class="q-mt-md">
          <q-select v-model="wcLeafType" :options="['single', 'double']" label="Single-leaf or Double-leaf wall?"
            filled />
          <div v-if="wcLeafType === 'single'" class="q-mt-md">
            <q-input v-model.number="wcSingleMl" label="Enter Ml value" type="number" filled />
          </div>
          <div v-else-if="wcLeafType === 'double'" class="q-mt-md">
            <q-input v-model.number="wcDoubleMl1" label="Enter Ml for leaf 1" type="number" filled />
            <q-input v-model.number="wcDoubleMl2" label="Enter Ml for leaf 2" type="number" filled class="q-mt-sm" />
          </div>
        </div>
        <div v-else class="q-mt-md">
          <q-select v-model="selections['WC_qual']" :options="parametersTextSelectOptions['WC_qual']" label="Qualitative description"
            filled />
        </div>
      </div>

      <div class="q-mb-md">
        <q-toggle v-model="vjQuantitative" label="Vertical section accessible for quantitative analysis?" />
        <div v-if="vjQuantitative" class="q-mt-md">
          <q-select v-model="vjLeafType" :options="['single', 'double']" label="Single-leaf or Double-leaf wall?"
            filled />
          <div v-if="vjLeafType === 'single'" class="q-mt-md">
            <q-input v-model.number="vjSingleMl" label="Enter Ml value" type="number" filled />
          </div>
          <div v-else-if="vjLeafType === 'double'" class="q-mt-md">
            <q-input v-model.number="vjDoubleMl1" label="Enter Ml for leaf 1" type="number" filled />
            <q-input v-model.number="vjDoubleMl2" label="Enter Ml for leaf 2" type="number" filled class="q-mt-sm" />
          </div>
        </div>
        <div v-else class="q-mt-md">
          <q-select v-model="selections['VJ_qual']" :options="parametersTextSelectOptions['VJ_qual']" label="Qualitative description"
            filled />
        </div>
      </div>

      <q-stepper-navigation>
        <q-btn @click="step++" color="primary" label="Continue" />
        <q-btn flat @click="step--" color="primary" label="Back" class="q-ml-sm" />
      </q-stepper-navigation>
    </q-step>

    <q-step :name="3" title="Thick Bed Joints & Mortar properties">
      <div v-if="masonryType?.value === 'squared-hardstone-masonry' || masonryType?.value === 'brickwork-lime-based-mortar'">
        <q-toggle v-model="thickBedJoints" label="Are mortar bed joints thick (>13 mm)?" />
      </div>
      <div v-if="isMortarNF">
        <q-toggle v-model="compressiveStrengthSmall" label="Mortar is NF. Is compressive strength < 0.7 MPa?" />
      </div>

      <q-stepper-navigation>
        <q-btn @click="step++" color="primary" label="Compute MQI" />
        <q-btn flat @click="step--" color="primary" label="Back" class="q-ml-sm" />
      </q-stepper-navigation>
    </q-step>

    <q-step :name="4" title="MQI Results">
      <quality-index-calculator
        :masonryType="masonryType"
        :selections="selections"
        :wcQuantitative="wcQuantitative"
        :wcLeafType="wcLeafType"
        :wcSingleMl="wcSingleMl"
        :wcDoubleMl1="wcDoubleMl1"
        :wcDoubleMl2="wcDoubleMl2"
        :vjQuantitative="vjQuantitative"
        :vjLeafType="vjLeafType"
        :vjSingleMl="vjSingleMl"
        :vjDoubleMl1="vjDoubleMl1"
        :vjDoubleMl2="vjDoubleMl2"
        :thickBedJoints="thickBedJoints"
        :compressive-strength-small="compressiveStrengthSmall"
      />


      <q-stepper-navigation>
        <q-btn flat @click="step--" color="primary" label="Back" class="q-ml-sm" />
      </q-stepper-navigation>
    </q-step>
  </q-stepper>
</template>

<script setup lang="ts">
import { classifyMM, masonryTypologiesSelectOptions, parametersTextSelectOptions, textParameterLabel, type TextParameterSelection } from 'src/components/qualityIndex/qualityIndexConstants';
import QualityIndexCalculator from './QualityIndexCalculator.vue';
import { ref } from 'vue'

// Stepper
const step = ref(1);

// Masonry Typologies
const masonryType = ref<{ label: string, value: string } | null>(null);

const textParametersKeys = ["SM", "MM", "SS", "SD", "HJ"] as const;
const selections = ref<Partial<TextParameterSelection>>({});

// WC step
const wcQuantitative = ref(false);
const wcLeafType = ref<"single" | "double" | null>(null);
const wcSingleMl = ref(null);
const wcDoubleMl1 = ref(null);
const wcDoubleMl2 = ref(null);

// VJ step
const vjQuantitative = ref(false);
const vjLeafType = ref(null);
const vjSingleMl = ref(null);
const vjDoubleMl1 = ref(null);
const vjDoubleMl2 = ref(null);

// Thick bed joints
const thickBedJoints = ref(false);
const compressiveStrengthSmall = ref(false);

const isMortarNF = computed(() => {
  if (!selections.value.MM) return false;
  return classifyMM(selections.value.MM?.value) === "NF";
});

</script>

<style scoped>

.with-explainer {
  display: grid;
  grid-template-areas: "selector explainer-image";
  grid-template-columns: 1fr 1fr;
  align-items: start;
  gap: 1rem;
}

@media screen and (max-width: 960px) {
  .with-explainer {
    grid-template-areas:
      "selector"
      "explainer-image";
    grid-template-columns: 1fr;
  }
}

.with-explainer .q-select {
  grid-area: selector;
}

.with-explainer img {
  display: block;
  width: 100%;
  object-fit: contain;
  grid-area: explainer-image;
}

</style>