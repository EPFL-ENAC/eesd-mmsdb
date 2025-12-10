<template>
  <div>
    <q-table
      title="Masonry Quality Index (MQI) per location"
      :columns="[
        { name: 'location', label: 'Location', field: 'location', align: 'left' },
        { name: 'value', label: 'MQI Value', field: 'value', align: 'right' },
        { name: 'category', label: 'Masonry Category', field: 'category', align: 'right' }
      ]"
      :rows="[
        { location: 'Vertical (V)', value: VMQI !== null ? VMQI.toFixed(2) : 'N/A', category: VMQI !== null ? getMasonryCategory('V') : 'N/A' },
        { location: 'In-plane (I)', value: IMQI !== null ? IMQI.toFixed(2) : 'N/A', category: IMQI !== null ? getMasonryCategory('I') : 'N/A' },
        { location: 'Out-of-plane (O)', value: OMQI !== null ? OMQI.toFixed(2) : 'N/A', category: OMQI !== null ? getMasonryCategory('O') : 'N/A' }
      ]"
      row-key="location"
      flat
      bordered
      hide-bottom
    />

    <div class="explanation q-pt-md">
      <div>Results given by the {{ squaredOrBrickwork ? 'special squared or brickwork' : 'base' }} formula :</div>
      <img :src="squaredOrBrickwork ? '/MQI_computation_brickwork.webp' : '/MQI_computation.webp'" alt="MQI computation formula">
    </div>
    
    <div class="explanation">
      <div>And the categories are given by this table :</div>
      <img src="/MQI_categories.webp" alt="MQI categories table">

      <div class="q-mt-md">
        The categories can be understood as follow :
        <ul class="q-mt-xs">
          <li>A masonry wall in category A is very unlikely to fail;</li>
          <li>A masonry wall in category B may crack, but its collapse is rare;</li>
          <li>A masonry wall in category C will likely crack under the eﬀect of vertical loading.</li>
        </ul>
      </div>
    </div>

    <q-table
      class="q-mt-xl"
      title="Masonry Mechanical Properties estimation"
      :columns="[
        { name: 'property', label: 'Property', field: 'property', align: 'left' },
        { name: 'min', label: 'min', field: 'min', align: 'right' },
        { name: 'r_min', label: 'R² min', field: 'r_min', align: 'right' },
        { name: 'mean', label: 'mean', field: 'mean', align: 'right' },
        { name: 'r_mean', label: 'R² mean', field: 'r_mean', align: 'right' },
        { name: 'max', label: 'max', field: 'max', align: 'right' },
        { name: 'r_max', label: 'R² max', field: 'r_max', align: 'right' },
      ]"
      :rows="[
        { property: 'Shear strength τ₀, failure mode I', min: (0.0004 * ((IMQI ?? 0) ** 2) + 0.0055 * (IMQI ?? 0) + 0.0173).toFixed(4), r_min: '0.825', mean: (0.0006 * ((IMQI ?? 0) ** 2) + 0.0075 * (IMQI ?? 0) + 0.0224).toFixed(4), r_mean: '0.913', max: (0.0008 * ((IMQI ?? 0) ** 2) + 0.0094 * (IMQI ?? 0) + 0.0275).toFixed(4), r_max: '0.843' },
        { property: 'Young\'s modulus E', min: (608 * Math.exp(0.154 * (VMQI ?? 0))).toFixed(4), r_min: '0.709', mean: (742.1 * Math.exp(0.153 * (VMQI ?? 0))).toFixed(4), r_mean: '0.720', max: (876 * Math.exp(0.151 * (VMQI ?? 0))).toFixed(4), r_max:' 0.724' },
        { property: 'Compressive strength f', min: (1.055 * Math.exp(0.193 * (VMQI ?? 0))).toFixed(4), r_min: '0.803', mean: (1.444 * Math.exp(0.182 * (VMQI ?? 0))).toFixed(4), r_mean: '0.824', max: (1.892 * Math.exp(0.175 * (VMQI ?? 0))).toFixed(4), r_max:' 0.828' },
        { property: 'Shear modulus G', min: (201.4 * Math.exp(0.142 * (IMQI ?? 0))).toFixed(4), r_min: '0.652', mean: (254.6 * Math.exp(0.141 * (IMQI ?? 0))).toFixed(4), r_mean: '0.680', max: (298.7 * Math.exp(0.141 * (IMQI ?? 0))).toFixed(4), r_max:' 0.695' },
        { property: 'Shear strength fᵥ₀, failure mode II (stepped or zig-zag failure mode)', min: (0.03 * Math.pow((IMQI ?? 0), 0.909)).toFixed(4), r_min: '0.893', mean: (0.0475 * Math.pow((IMQI ?? 0), 0.854)).toFixed(4), r_mean: '0.928', max: (0.0654 * Math.pow((IMQI ?? 0), 0.822)).toFixed(4), r_max:' 0.918' },
      ]"
      row-key="property"
      :pagination="{ rowsPerPage: 10 }"
      flat
      bordered
      hide-bottom
    />

    <div class="explanation q-pt-md">
      <div>Formula for the estimation of the masonry shear strength τ₀, failure mode I:</div>
      <img src="/MQI_shear_strength.webp" alt="MQI shear strength estimation (failure mode I)">

      <div>Formula for the estimation of the masonry Young’s modulus E:</div>
      <img src="/MQI_youngs_modulus.webp" alt="MQI Young's modulus estimation">

      <div>Formula for the estimation of the masonry compressive strength f:</div>
      <img src="/MQI_compressive_strength.webp" alt="MQI compressive strength estimation">

      <div>Formula for the estimation of the masonry shear modulus G:</div>
      <img src="/MQI_shear_modulus.webp" alt="MQI shear modulus estimation">

      <div>Formula for the estimation of shear strength fᵥ₀, failure mode II (stepped or zig-zag failure mode):</div>
      <img src="/MQI_shear_strength_2.webp" alt="MQI shear strength estimation (failure mode II)">
    </div>

    <hr />
    
    <h4>Computation summary</h4>
    
    <q-table
      class="q-mt-md"
      title="Base classifications"
      :columns="[
        { name: 'parameter', label: 'Parameter', field: 'parameter', align: 'left' },
        { name: 'classification', label: 'Classification', field: 'classification', align: 'right' },
        { name: 'analysisType', label: 'Analysis type', field: 'analysisType', align: 'right' },
        { name: 'v_v', label: 'Picked Value (V)', field: 'v_v', align: 'right' },
        { name: 'v_i', label: 'Picked Value (I)', field: 'v_i', align: 'right' },
        { name: 'v_o', label: 'Picked Value (O)', field: 'v_o', align: 'right' }
      ]"
      :rows="[
        { parameter: 'Stone/brick mechanical properties and conservation state (SM)', classification: smClassification || 'N/A', analysisType: 'Qualitative', v_v: getMQIValue('SM', 'V', smClassification) ?? 'N/A', v_i: getMQIValue('SM', 'I', smClassification) ?? 'N/A', v_o: getMQIValue('SM', 'O', smClassification) ?? 'N/A' },
        { parameter: 'Mortar Properties (MM)', classification: mmClassification || 'N/A', analysisType: 'Qualitative', v_v: getMQIValue('MM', 'V', mmClassification) ?? 'N/A', v_i: getMQIValue('MM', 'I', mmClassification) ?? 'N/A', v_o: getMQIValue('MM', 'O', mmClassification) ?? 'N/A' },
        { parameter: 'Stone/brick Shape (SS)', classification: ssClassification || 'N/A', analysisType: 'Qualitative', v_v: getMQIValue('SS', 'V', ssClassification) ?? 'N/A', v_i: getMQIValue('SS', 'I', ssClassification) ?? 'N/A', v_o: getMQIValue('SS', 'O', ssClassification) ?? 'N/A' },
        { parameter: 'Stone/brick Dimension (SD)', classification: sdClassification || 'N/A', analysisType: 'Qualitative', v_v: getMQIValue('SD', 'V', sdClassification) ?? 'N/A', v_i: getMQIValue('SD', 'I', sdClassification) ?? 'N/A', v_o: getMQIValue('SD', 'O', sdClassification) ?? 'N/A' },
        { parameter: 'Horizontality of Mortar Bed Joints (HJ)', classification: hjClassification || 'N/A', analysisType: 'Qualitative', v_v: getMQIValue('HJ', 'V', hjClassification) ?? 'N/A', v_i: getMQIValue('HJ', 'I', hjClassification) ?? 'N/A', v_o: getMQIValue('HJ', 'O', hjClassification) ?? 'N/A' },
        { parameter: 'Wall Leaf Connections (WC)', classification: props.wcQuantitative ? (wcQuantitativeClassification || 'N/A') : (wcQualitativeClassification || 'N/A'), analysisType: props.wcQuantitative ? 'Quantitative' : 'Qualitative', v_v: getMQIValue('WC', 'V', props.wcQuantitative ? wcQuantitativeClassification : wcQualitativeClassification) ?? 'N/A', v_i: getMQIValue('WC', 'I', props.wcQuantitative ? wcQuantitativeClassification : wcQualitativeClassification) ?? 'N/A', v_o: getMQIValue('WC', 'O', props.wcQuantitative ? wcQuantitativeClassification : wcQualitativeClassification) ?? 'N/A' },
        { parameter: 'Staggering of Vertical Mortar Joints (VJ)', classification: props.vjQuantitative ? (vjQuantitativeClassification || 'N/A') : (vjQualitativeClassification || 'N/A'), analysisType: props.vjQuantitative ? 'Quantitative' : 'Qualitative', v_v: getMQIValue('VJ', 'V', props.vjQuantitative ? vjQuantitativeClassification : vjQualitativeClassification) ?? 'N/A', v_i: getMQIValue('VJ', 'I', props.vjQuantitative ? vjQuantitativeClassification : vjQualitativeClassification) ?? 'N/A', v_o: getMQIValue('VJ', 'O', props.vjQuantitative ? vjQuantitativeClassification : vjQualitativeClassification) ?? 'N/A' }
      ]"
      row-key="parameter"
      :pagination="{ rowsPerPage: 10 }"
      flat
      bordered
      hide-bottom
    />
    <q-table
      class="q-mt-md"
      title="Factors"
      :columns="[
        { name: 'name', label: 'Name', field: 'name', align: 'left' },
        { name: 'value', label: '', field: 'value', align: 'right' }
      ]"
      :rows="[
        { name: 'm (0.7 for small compressive strengths, otherwise 1)', value: mFactor.toFixed(2) },
        { name: 'Compressive strength small', value: compressiveStrengthSmall.toString() },
        { name: 'g (0.7 if squared or brickwork, otherwise 1)', value: gFactor.toFixed(2) },
        { name: 'Squared or brickwork', value: squaredOrBrickwork.toString() }
      ]"
      row-key="name"
      flat
      bordered
      hide-bottom
    />
    <q-table
      v-if="squaredOrBrickwork"
      class="q-mt-md"
      title="R values"
      :columns="[
        { name: 'location', label: 'Location', field: 'location', align: 'left' },
        { name: 'value', label: 'MQI Value', field: 'value', align: 'right' }
      ]"
      :rows="[
        { location: 'Vertical (V)', value: rValues?.V ? rValues.V.toFixed(2) : 'N/A' },
        { location: 'In-plane (I)', value: rValues?.I ? rValues.I.toFixed(2) : 'N/A' },
        { location: 'Out-of-plane (O)', value: rValues?.O ? rValues.O.toFixed(2) : 'N/A' }
      ]"
      row-key="location"
      flat
      bordered
      hide-bottom
    />
  </div>

</template>

<script setup lang="ts">
import {
  classify_VJ_qualitative,
  classifyDoubleLeafVJ_quantitative,
  classifyDoubleLeafWC_quantitative,
  classifyHJ,
  classifyMM, classifySD, classifySingleLeafVJ_quantitative, classifySingleLeafWC_quantitative, classifySM, classifySS,
  classifyWC_qualitative,
  r_table,
  MQI_table,
  type MQILocation,
  type TextParameterSelection,
  type ClassificationParameter,
  type MQIClassification
} from 'src/components/qualityIndex/qualityIndexConstants';
import { computed } from 'vue'

const props = defineProps<{
  masonryType: { label: string; value: string } | null,
  selections: Partial<TextParameterSelection>,
  wcQuantitative: boolean,
  wcLeafType: "single" | "double" | null,
  wcSingleMl: number | null,
  wcDoubleMl1: number | null,
  wcDoubleMl2: number | null,
  vjQuantitative: boolean,
  vjLeafType: string | null,
  vjSingleMl: number | null,
  vjDoubleMl1: number | null,
  vjDoubleMl2: number | null,
  thickBedJoints: boolean,
  compressiveStrengthSmall: boolean
}>();

// Base classifications
const smClassification = computed(() => props.selections.SM ? classifySM(props.selections.SM.value) : null);
const mmClassification = computed(() => props.selections.MM ? classifyMM(props.selections.MM.value) : null);
const ssClassification = computed(() => props.selections.SS ? classifySS(props.selections.SS.value) : null);
const sdClassification = computed(() => props.selections.SD ? classifySD(props.selections.SD.value) : null);
const hjClassification = computed(() => props.selections.HJ ? classifyHJ(props.selections.HJ.value) : null);

function getMasonryCategory(location: MQILocation): 'A' | 'B' | 'C' {
  if (location === 'V') {
    const v = VMQI.value ?? 0;
    if (v < 2.5) return 'C';
    else if (v < 5) return 'B';
    return 'A';
  } else if (location === 'I') {
    const i = IMQI.value ?? 0;
    if (i < 3) return 'C';
    else if (i < 5) return 'B';
    return 'A';
  }
  
  const o = OMQI.value ?? 0;
  if (o < 4) return 'C';
  else if (o < 7) return 'B';
  return 'A';
}

function getMQIValue(parameter: ClassificationParameter, location: MQILocation, classification: MQIClassification | null): number | null {
  if (!classification) return null;
  return MQI_table[parameter][location][classification] ?? null;
}

const wcQuantitativeClassification = computed(() => {
  if (!props.wcQuantitative) return null;

  if (props.wcLeafType === 'single' && props.wcSingleMl !== null) {
    return classifySingleLeafWC_quantitative(props.wcSingleMl);
  } else if (props.wcLeafType === 'double' && props.wcDoubleMl1 !== null && props.wcDoubleMl2 !== null) {
    return classifyDoubleLeafWC_quantitative([props.wcDoubleMl1, props.wcDoubleMl2]);
  }

  return null;
});
const wcQualitativeClassification = computed(() => {
  if (!props.selections.WC_qual) return null;
  return classifyWC_qualitative(props.selections.WC_qual.value);
});

const vjQuantitativeClassification = computed(() => {
  if (!props.vjQuantitative) return null;

  if (props.vjLeafType === 'single' && props.vjSingleMl !== null) {
    return classifySingleLeafVJ_quantitative(props.vjSingleMl);
  } else if (props.vjLeafType === 'double' && props.vjDoubleMl1 !== null && props.vjDoubleMl2 !== null) {
    return classifyDoubleLeafVJ_quantitative([props.vjDoubleMl1, props.vjDoubleMl2]);
  }

  return null;
});
const vjQualitativeClassification = computed(() => {
  if (!props.selections.VJ_qual) return null;
  return classify_VJ_qualitative(props.selections.VJ_qual.value);
});

const mFactor = computed(() => props.compressiveStrengthSmall ? 0.7 : 1.0);
const gFactor = computed(() => props.thickBedJoints ? 0.7 : 1.0);
const squaredOrBrickwork = computed(() => {
  return props.masonryType?.value === 'squared-hardstone-masonry' || props.masonryType?.value === 'brickwork-lime-based-mortar';
});

const rValues = computed(() => mmClassification.value ? r_table[mmClassification.value] : null)

function computeLoadCondition(location: MQILocation): number | null {
  if (!smClassification.value || !mmClassification.value || !ssClassification.value || !sdClassification.value || !hjClassification.value || !rValues.value) {
    return null;
  }

  const smVal = MQI_table["SM"][location][smClassification.value];

  const sdVal = MQI_table["SD"][location][sdClassification.value];
  const ssVal = MQI_table["SS"][location][ssClassification.value];
  const hjVal = MQI_table["HJ"][location][hjClassification.value];
  const mmVal = MQI_table["MM"][location][mmClassification.value];

  const wcClass = props.wcQuantitative ? wcQuantitativeClassification.value : wcQualitativeClassification.value;
  if (!wcClass) return null;
  const wcVal = MQI_table["WC"][location][wcClass];

  const vjClass = props.vjQuantitative ? vjQuantitativeClassification.value : vjQualitativeClassification.value;
  if (!vjClass) return null;
  const vjVal = MQI_table["VJ"][location][vjClass];

  const sum = sdVal + ssVal + hjVal + mmVal + wcVal + vjVal;

  if (squaredOrBrickwork.value) {
    return mFactor.value * gFactor.value * rValues.value[location] * smVal * sum;
  }

  return mFactor.value * smVal * sum;
}

const VMQI = computed(() => computeLoadCondition("V"));
const IMQI = computed(() => computeLoadCondition("I"));
const OMQI = computed(() => computeLoadCondition("O"));

</script>

<style scoped>

section {
  display: grid;
  grid-template-areas: "result-table explainer-image";
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 1rem;
}

@media screen and (max-width: 960px) {
  section {
    grid-template-areas:
      "result-table"
      "explainer-image";
    grid-template-columns: 1fr;
  }
}

section .q-table {
  grid-area: result-table;
}

section img {
  display: block;
  width: 100%;
  object-fit: contain;
  grid-area: explainer-image;
}

.explanation {
  margin: 1rem 0 1rem 0;
}

.explanation img {
  display: block;
  width: 600px;
  max-width: 100%;
  margin: auto;
}

:deep(.q-table th:first-child) {
  width: 100%;
}

</style>
