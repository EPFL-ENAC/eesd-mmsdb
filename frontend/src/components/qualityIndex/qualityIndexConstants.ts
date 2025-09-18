export const masonryTypologiesSelectOptions = [
  { label: "Irregular stone masonry (pebbles, erratic and irregular stones)", value: "irregular-stone-masonry" },
  { label: "Roughly cut stone masonry, with non-homogenous wall leaves", value: "roughly-cut-stone-masonry" },
  { label: "Barely cut stone masonry, properly dressed", value: "barely-cut-stone-masonry" },
  { label: "Irregular softstone masonry", value: "irregular-softstone-masonry" },
  { label: "Squared softstone masonry", value: "squared-softstone-masonry" },
  { label: "Squared hardstone masonry", value: "squared-hardstone-masonry" },
  { label: "Brickwork (lime-based mortar)", value: "brickwork-lime-based-mortar" },
  { label: "Hollow bricks masonry (cement mortar)", value: "hollow-bricks-masonry-cement-mortar" }
];

export const textParameterLabel = {
  SM: "Strength of Masonry (SM)",
  MM: "Mortar Quality (MM)",
  SS: "Stone Shape (SS)",
  SD: "Stone Dimension (SD)",
  HJ: "Horizontal Joints (HJ)",
  WC_qual: "Wall Connections - Qualitative (WC_qual)",
  VJ_qual: "Vertical Joints - Qualitative (VJ_qual)"
};

export const SMSelectOptions = [
  { label: "Degraded/damaged >50%", value: "degraded-damaged-gt50" },
  { label: "Degraded/damaged 10-50%", value: "degraded-damaged-10-50" },
  { label: "Undamaged / solid fired / concrete / hardstones / hollow >55% solid", value: "undamaged-solid-fired-concrete-hardstones-hollow-gt55-solid" }
];

export const MMSelectOptions = [
  { label: "Very weak mortar and dusty mortar with no cohesion", value: "very-weak-mortar-dusty-no-cohesion" },
  { label: "No mortar (dry rubble or pebble stonework)", value: "no-mortar-dry-rubble-pebble-stonework" },
  { label: "Thick bed joints made of weak mortar (thickness comparable to stone/brick thickness)", value: "thick-bed-joints-weak-mortar-thickness-comparable-to-stone-brick" },
  { label: "Porous stones/bricks with weak bond to mortar", value: "porous-stones-bricks-weak-bond-to-mortar" },
  { label: "Medium quality mortar, with bed joints not largely notched", value: "medium-quality-mortar-bed-joints-not-largely-notched" },
  { label: "Masonry made of irregular (rubble) stones and weak mortar, and pinning stones", value: "masonry-irregular-rubble-stones-weak-mortar-pinning-stones" },
  { label: "Good-quality and non-degraded mortar, regular bed joints, or thick bed joints made of very good-quality mortar", value: "good-quality-non-degraded-mortar-regular-bed-joints-thick-bed-joints-good-quality" },
  { label: "Masonry made of large perfectly cut stones with no mortar (dry) or very thin bed mortar joints", value: "masonry-large-perfectly-cut-stones-no-mortar-dry-thin-bed-mortar" }
];

export const SSSelectOptions = [
  { label: "Rubble / rounded / pebble stones predominant", value: "rubble-rounded-pebble-stones-predominant" },
  { label: "Copresence of rubble/rounded/pebble / barely/perfectly cut stones on one leaf", value: "copresence-rubble-rounded-pebble-barely-perfectly-cut-stones-one-leaf" },
  { label: "Barely/perfectly cut stones on both leaves / Brickwork", value: "barely-perfectly-cut-stones-both-leaves-brickwork" }
];

export const SDSelectOptions = [
  { label: "Blocks <20cm / header bond no stretchers", value: "blocks-lt20cm-header-bond-no-stretchers" },
  { label: "Blocks 20-40 cm / mixed dimensions", value: "blocks-20-40cm-mixed-dimensions" },
  { label: "Blocks >40 cm", value: "blocks-gt40cm" }
];

export const HJSelectOptions = [
  { label: "Bed joints not continuous", value: "bed-joints-not-continuous" },
  { label: "Bed joints partially continuous / double-leaf: one leaf continuous", value: "bed-joints-partially-continuous-double-leaf-one-leaf-continuous" },
  { label: "Bed joints continuous / stone masonry or brick courses (<60 cm)", value: "bed-joints-continuous-stone-masonry-brick-courses-lt60cm" }
];

export const WC_qualSelectOptions = [
  { label: "Small stones / No headers", value: "small-stones-no-headers" },
  { label: "Double-leaf walls: limited stone headers", value: "double-leaf-walls-limited-stone-headers" },
  { label: "Wall thickness similar or larger than stone larger dimension", value: "wall-thickness-similar-larger-than-stone-larger-dimension" }
];

export const VJ_qualSelectOptions = [
  { label: "Vertically aligned head joints / no interlocking", value: "vertically-aligned-head-joints-no-interlocking" },
  { label: "Partially staggered head joints", value: "partially-staggered-head-joints" },
  { label: "Properly staggered head joints", value: "properly-staggered-head-joints" }
];


// Text parameters
export const parametersTextSelectOptions = {
  SM: SMSelectOptions,
  MM: MMSelectOptions,
  SS: SSSelectOptions,
  SD: SDSelectOptions,
  HJ: HJSelectOptions,
  WC_qual: WC_qualSelectOptions,
  VJ_qual: VJ_qualSelectOptions
};

export type TextParameterSelection = Record<keyof typeof parametersTextSelectOptions, { label: string; value: string }>;


export type MQIClassification = "NF" | "PF" | "F";
export type MQILocation = "V" | "I" | "O";

const SMClassifier_NFValues = [
  "degraded-damaged-gt50",
  "hollow-core-bricks-lt30-solid",
  "mud-bricks",
  "unfired-bricks"
];
const SMClassifier_PFValues = [
  "degraded-damaged-10-50",
  "hollow-bricks-30-55",
  "sandstone-tuff-elements"
];

// === Strength of Masonry (SM) ===
export function classifySM(value: string): MQIClassification {
  console.log("classifySM called with value:", value);
  if (SMClassifier_NFValues.includes(value)) {
    return "NF";
  } else if (SMClassifier_PFValues.includes(value)) {
    return "PF";
  }

  return "F";
}

const MMClassifier_NFValues = [
  "very-weak-mortar-dusty-no-cohesion",
  "no-mortar-dry-rubble-pebble-stonework",
  "thick-bed-joints-weak-mortar-thickness-comparable-to-stone-brick",
  "porous-stones-bricks-weak-bond-to-mortar"
];
const MMClassifier_PFValues = [
  "medium-quality-mortar-bed-joints-not-largely-notched",
  "masonry-irregular-rubble-stones-weak-mortar-pinning-stones"
];

// === Mortar Quality (MM) ===
export function classifyMM(value: string): MQIClassification {
  if (MMClassifier_NFValues.includes(value)) {
    return "NF";
  } else if (MMClassifier_PFValues.includes(value)) {
    return "PF";
  }

  return "F";
}

// === Stone Shape (SS) ===
export function classifySS(value: string): MQIClassification {
  if (value === "rubble-rounded-pebble-stones-predominant") {
    return "NF";
  } else if (value === "copresence-rubble-rounded-pebble-barely-perfectly-cut-stones-one-leaf") {
    return "PF";
  }

  return "F";
}

// === Stone Dimension (SD) ===
export function classifySD(value: string): MQIClassification {
  if (value === "blocks-lt20cm-header-bond-no-stretchers") {
    return "NF";
  } else if (value === "blocks-20-40cm-mixed-dimensions") {
    return "PF";
  }

  return "F";
}

// === Horizontal Joints (HJ) ===
export function classifyHJ(value: string): MQIClassification {
  if (value === "bed-joints-not-continuous") {
    return "NF";
  } else if (value === "bed-joints-partially-continuous-double-leaf-one-leaf-continuous") {
    return "PF";
  }

  return "F";
}

// === Wall Connections - Qualitative (WC_qual) ===
export function classifyWC_qualitative(value: string): MQIClassification {
  if (value === "small-stones-no-headers") {
    return "NF";
  } else if (value === "double-leaf-walls-limited-stone-headers") {
    return "PF";
  }

  return "F";
}

function isPFForDoubleLeaf([leaf1, leaf2]: [number, number]): boolean {
  return (
    (leaf1 >= 1.4 && leaf1 <= 1.6 && leaf2 >= 1.4 && leaf2 <= 1.6) ||
    (leaf1 > 1.6 && leaf2 < 1.4) ||
    (leaf1 < 1.4 && leaf2 > 1.6) ||
    (leaf1 > 1.6 && leaf2 >= 1.4 && leaf2 <= 1.6) ||
    (leaf2 > 1.6 && leaf1 >= 1.4 && leaf1 <= 1.6)
  );
}

// === Wall Connections - Quantitative (WC_quantitative) ===
export function classifySingleLeafWC_quantitative(singleLeafMl: number): MQIClassification {
  if (singleLeafMl < 1.4) return "NF";
  if (singleLeafMl <= 1.6) return "PF";

  return "F";
}

export function classifyDoubleLeafWC_quantitative([leaf1, leaf2]: [number, number]): MQIClassification {
  if (leaf1 < 1.4 || leaf2 < 1.4) {
    return "NF";
  }
  if (isPFForDoubleLeaf([leaf1, leaf2])) {
    return "PF";
  }

  return "F";
}

// === Wall Connections - Quantitative (WC_quantitative) ===
export function classifyWC_quantitative(singleLeafMl?: number | null, doubleLeafMl?: [number, number] | null): MQIClassification {
  if (singleLeafMl) return classifySingleLeafWC_quantitative(singleLeafMl);
  if (doubleLeafMl) return classifyDoubleLeafWC_quantitative(doubleLeafMl);

  return "F";
}

// === Vertical Joints (VJ) ===
export function classify_VJ_qualitative(value: string): MQIClassification {
  if (value === "vertically-aligned-head-joints-no-interlocking") {
    return "NF";
  } else if (value === "partially-staggered-head-joints") {
    return "PF";
  }

  return "F";
}

// === Vertical Joints - Quantitative (VJ_quantitative) ===
export function classifySingleLeafVJ_quantitative(singleLeafMl: number): MQIClassification {
  if (singleLeafMl < 1.4) return "NF";
  if (singleLeafMl <= 1.6) return "PF";

  return "F";
}

export function classifyDoubleLeafVJ_quantitative([leaf1, leaf2]: [number, number]): MQIClassification {
  if (leaf1 < 1.4 || leaf2 < 1.4) {
    return "NF";
  }
  if (isPFForDoubleLeaf([leaf1, leaf2])) {
    return "PF";
  }

  return "F";
}

// Optional wrapper if you want the same API as before
export function classifyVJ_quantitative(singleLeafMl?: number, doubleLeafMl?: [number, number]): MQIClassification {
  if (singleLeafMl !== undefined) return classifySingleLeafVJ_quantitative(singleLeafMl);
  if (doubleLeafMl !== undefined) return classifyDoubleLeafVJ_quantitative(doubleLeafMl);

  return "F";
}

type ClassificationParameter = "SM" | "MM" | "SS" | "SD" | "HJ" | "WC" | "VJ";

export const MQI_table: Record<ClassificationParameter, Record<MQILocation, Record<MQIClassification, number>>> = {
  "HJ": {
    "V": { "NF": 0, "PF": 1, "F": 2 },
    "I": { "NF": 0, "PF": 0.5, "F": 1 },
    "O": { "NF": 0, "PF": 1, "F": 2 }
  },
  "WC": {
    "V": { "NF": 0, "PF": 1, "F": 1 },
    "I": { "NF": 0, "PF": 1, "F": 2 },
    "O": { "NF": 0, "PF": 1.5, "F": 3 }
  },
  "SS": {
    "V": { "NF": 0, "PF": 1.5, "F": 3 },
    "I": { "NF": 0, "PF": 1, "F": 2 },
    "O": { "NF": 0, "PF": 1, "F": 2 }
  },
  "VJ": {
    "V": { "NF": 0, "PF": 0.5, "F": 1 },
    "I": { "NF": 0, "PF": 1, "F": 2 },
    "O": { "NF": 0, "PF": 0.5, "F": 1 }
  },
  "SD": {
    "V": { "NF": 0, "PF": 0.5, "F": 1 },
    "I": { "NF": 0, "PF": 0.5, "F": 1 },
    "O": { "NF": 0, "PF": 0.5, "F": 1 }
  },
  "MM": {
    "V": { "NF": 0, "PF": 0.5, "F": 2 },
    "I": { "NF": 0, "PF": 1, "F": 2 },
    "O": { "NF": 0, "PF": 0.5, "F": 1 }
  },
  "SM": {
    "V": { "NF": 0.3, "PF": 0.7, "F": 1 },
    "I": { "NF": 0.3, "PF": 0.7, "F": 1 },
    "O": { "NF": 0.5, "PF": 0.7, "F": 1 }
  }
} as const;

export const r_table: Record<MQIClassification, Record<MQILocation, number>> = {
  NF: { V: 0.2, I: 1, O: 0.1 },
  PF: { V: 0.6, I: 0.85, O: 1 },
  F: { V: 1, I: 1, O: 1 }
};
