<template>
  <q-table
    title="Masonry Quality Index (MQI) per location"
    :columns="[
      { name: 'location', label: 'Location', field: 'location', align: 'left' },
      { name: 'value', label: 'MQI Value', field: 'value', align: 'right' }
    ]"
    :rows="[
      { location: 'Vertical (V)', value: VMQI ? VMQI.toFixed(2) : 'N/A' },
      { location: 'In-plane (I)', value: IMQI ? IMQI.toFixed(2) : 'N/A' },
      { location: 'Out-of-plane (O)', value: OMQI ? OMQI.toFixed(2) : 'N/A' }
    ]"
    row-key="location"
    flat
    bordered
    hide-bottom
  />

  <hr />

  <h4>Computation summary</h4>

  <q-table
    class="q-mt-md"
    title="Base classifications"
    :columns="[
      { name: 'parameter', label: 'Parameter', field: 'parameter', align: 'left' },
      { name: 'classification', label: 'Classification', field: 'classification', align: 'right' }
    ]"
    :rows="[
      { parameter: 'SM', classification: smClassification || 'N/A' },
      { parameter: 'MM', classification: mmClassification || 'N/A' },
      { parameter: 'SS', classification: ssClassification || 'N/A' },
      { parameter: 'SD', classification: sdClassification || 'N/A' },
      { parameter: 'HJ', classification: hjClassification || 'N/A' }
    ]"
    row-key="parameter"
    flat
    bordered
    hide-bottom
  />


  <q-table
    class="q-mt-md"
    title="Wall Leaf Connections (WC) classifications"
    :columns="[
      { name: 'parameter', label: 'Parameter', field: 'parameter', align: 'left' },
      { name: 'value', label: 'Value', field: 'value', align: 'right' }
    ]"
    :rows="wcTableRows"
    row-key="parameter"
    flat
    bordered
    hide-bottom
  />

  <q-table
    class="q-mt-md"
    title="Vertical Joint Staggering (VJ) classifications"
    :columns="[
      { name: 'parameter', label: 'Parameter', field: 'parameter', align: 'left' },
      { name: 'value', label: 'Value', field: 'value', align: 'right' }
    ]"
    :rows="vjTableRows"
    row-key="parameter"
    flat
    bordered
    hide-bottom
  />

  <q-table
    class="q-mt-md"
    title="Factors"
    :columns="[
      { name: 'name', label: 'Name', field: 'name', align: 'left' },
      { name: 'value', label: 'MQI Value', field: 'value', align: 'right' }
    ]"
    :rows="[
      { name: 'm', value: mFactor.toFixed(2) },
      { name: 'g', value: gFactor.toFixed(2) },
      { name: 'Squared or brickwork', value: squaredOrBrickwork.toString() }
    ]"
    row-key="name"
    flat
    bordered
    hide-bottom
  />

  <q-table
    class="q-mt-md"
    title="R values per location"
    :columns="[
      { name: 'location', label: 'Location', field: 'location', align: 'left' },
      { name: 'value', label: 'MQI Value', field: 'value', align: 'right' }
    ]"
    :rows="[
      { location: 'Vertical (V)', value: rValues.V ? rValues.V.toFixed(2) : 'N/A' },
      { location: 'In-plane (I)', value: rValues.I ? rValues.I.toFixed(2) : 'N/A' },
      { location: 'Out-of-plane (O)', value: rValues.O ? rValues.O.toFixed(2) : 'N/A' }
    ]"
    row-key="location"
    flat
    bordered
    hide-bottom
  />

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
  type TextParameterSelection
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

const rValues = computed(() => r_table[mmClassification.value!])

function computeLoadCondition(location: MQILocation): number {
  const smVal = MQI_table["SM"][location][smClassification.value!];

  const sdVal = MQI_table["SD"][location][sdClassification.value!];
  const ssVal = MQI_table["SS"][location][ssClassification.value!];
  const hjVal = MQI_table["HJ"][location][hjClassification.value!];
  const mmVal = MQI_table["MM"][location][mmClassification.value!];
  const wcClass = props.wcQuantitative ? wcQuantitativeClassification.value : wcQualitativeClassification.value;
  const wcVal = MQI_table["WC"][location][wcClass!];
  const vjClass = props.vjQuantitative ? vjQuantitativeClassification.value : vjQualitativeClassification.value;
  const vjVal = MQI_table["VJ"][location][vjClass!];

  const sum = sdVal + ssVal + hjVal + mmVal + wcVal + vjVal;

  if (squaredOrBrickwork.value) {
    return mFactor.value * gFactor.value * rValues.value[location] * smVal * sum;
  }

  return mFactor.value * smVal * sum;
}

const VMQI = computed(() => computeLoadCondition("V"));
const IMQI = computed(() => computeLoadCondition("I"));
const OMQI = computed(() => computeLoadCondition("O"));


const wcTableRows = computed(() => {
  if (!props.wcQuantitative) {
    return [
      { parameter: 'Analysis type', value: 'Qualitative' },
      { parameter: 'Classification', value: wcQualitativeClassification.value ?? 'N/A' }
    ];
  }

  if (props.wcLeafType === 'single') {
    return [
      { parameter: 'Analysis type', value: 'Quantitative' },
      { parameter: 'Leaf count', value: 'Single' },
      { parameter: 'Ml', value: props.wcSingleMl ?? 'N/A' },
      { parameter: 'Classification', value: wcQuantitativeClassification.value ?? 'N/A' }
    ];
  } else if (props.wcLeafType === 'double') {
    return [
      { parameter: 'Analysis type', value: 'Quantitative' },
      { parameter: 'Leaf count', value: 'Double' },
      { parameter: 'Leaf 1 Ml', value: props.wcDoubleMl1 ?? 'N/A' },
      { parameter: 'Leaf 2 Ml', value: props.wcDoubleMl2 ?? 'N/A' },
      { parameter: 'Classification', value: wcQuantitativeClassification.value ?? 'N/A' }
    ];
  }

  return [];
});

const vjTableRows = computed(() => {
  if (!props.vjQuantitative) {
    return [
      { parameter: 'Analysis type', value: 'Qualitative' },
      { parameter: 'Classification', value: vjQualitativeClassification.value ?? 'N/A' }
    ];
  }

  if (props.vjLeafType === 'single') {
    return [
      { parameter: 'Analysis type', value: 'Quantitative' },
      { parameter: 'Leaf count', value: 'Single' },
      { parameter: 'Ml', value: props.vjSingleMl ?? 'N/A' },
      { parameter: 'Classification', value: vjQuantitativeClassification.value ?? 'N/A' }
    ];
  } else if (props.vjLeafType === 'double') {
    return [
      { parameter: 'Analysis type', value: 'Quantitative' },
      { parameter: 'Leaf count', value: 'Double' },
      { parameter: 'Leaf 1 Ml', value: props.vjDoubleMl1 ?? 'N/A' },
      { parameter: 'Leaf 2 Ml', value: props.vjDoubleMl2 ?? 'N/A' },
      { parameter: 'Classification', value: vjQuantitativeClassification.value ?? 'N/A' }
    ];
  }

  return [];
});

</script>
