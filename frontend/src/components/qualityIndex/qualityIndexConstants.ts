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
  SM: "Stone/brick mechanical properties and conservation state (SM)",
  MM: "Mortar Properties (MM)",
  SS: "Stone/brick Shape (SS)",
  SD: "Stone/brick Dimension (SD)",
  HJ: "Horizontality of Mortar Bed Joints (HJ)",
  WC_qual: "Wall Leaf Connections - Qualitative (WC_qual)",
  VJ_qual: "Staggering of Vertical Mortar Joints - Qualitative (VJ_qual)"
};

export const SMSelectOptions = [
  // NF
  { label: "Degraded/damaged elements (>50% of total number of elements) [NF]", value: "degraded-damaged-gt50" },
  { label: "Hollow-core bricks (solid < 30%) [NF]", value: "hollow-core-bricks" },
  { label: "Mud bricks [NF]", value: "mud-bricks" },
  { label: "Unfired bricks [NF]", value: "unfired-bricks" },
  // PF
  { label: "Degraded/damaged elements (≥10%; ≤50%) [PF]", value: "degraded-damaged-10-50" },
  { label: "Hollow bricks (55% ≥ solid ≥ 30%) [PF]", value: "hollow-bricks" },
  { label: "Sandstone or tuff elements [PF]", value: "sandstone-tuff-elements" },
  // F
  { label: "Undamaged elements or degraded/damaged elements < 10% [F]", value: "undamaged-elements" },
  { label: "Solid fired bricks [F]", value: "solid-fired-bricks" },
  { label: "Hollow bricks (55% < solid) [F]", value: "hollow-bricks" },
  { label: "Concrete units [F]", value: "concrete-units" },
  { label: "Hardstones [F]", value: "hardstones" }
];

export const MMSelectOptions = [
  // NF
  { label: "Very weak mortar and dusty mortar with no cohesion [NF]", value: "very-weak-mortar-dusty-no-cohesion" },
  { label: "No mortar (dry rubble or pebble stonework) [NF]", value: "no-mortar-dry-rubble-pebble-stonework" },
  { label: "Thick bed joints made of weak mortar (thickness comparable to stone/brick thickness) [NF]", value: "thick-bed-joints-weak-mortar-thickness-comparable-to-stone-brick" },
  { label: "Porous stones/bricks with weak bond to mortar [NF]", value: "porous-stones-bricks-weak-bond-to-mortar" },
  // PF
  { label: "Medium quality mortar, with bed joints not largely notched [PF]", value: "medium-quality-mortar-bed-joints-not-largely-notched" },
  { label: "Masonry made of irregular (rubble) stones and weak mortar, and pinning stones [PF]", value: "masonry-irregular-rubble-stones-weak-mortar-pinning-stones" },
  // F
  { label: "Good-quality and non-degraded mortar, regular bed joints, or thick bed joints made of very good-quality mortar [F]", value: "good-quality-non-degraded-mortar-regular-bed-joints-thick-bed-joints-good-quality" },
  { label: "Masonry made of large perfectly cut stones with no mortar (dry) or very thin bed mortar joints [F]", value: "masonry-large-perfectly-cut-stones-no-mortar-dry-thin-bed-mortar" }
];

export const SSSelectOptions = [
  // NF
  { label: "Rubble, or rounded or pebble stonework (predominant) on both masonry leaves [NF]", value: "rubble-rounded-pebble-stones-predominant" },
  // PF
  { label: "Copresence of rubble, or rounded or pebble stonework; barely/perfectly cut stones; and bricks on both masonry leaves [PF]", value: "copresence-rubble-rounded-pebble-barely-perfectly-cut-stones-one-leaf" },
  { label: "For double-leaf walls: squared blocks or bricks for one leaf and pebbles or irregular masonry for the adjacent wall leaf [PF]", value: "squared-blocks-bricks" },
  { label: "Masonry made of irregular (rubble, rounded, and pebble) stones, with pinning stones [PF]", value: "irregular-stones-with-pinning-stones" },
  // F
  { label: "Barely cut stones or perfectly cut stones on both masonry leaves (predominant) / Brickwork masonry [F]", value: "barely-perfectly-cut-stones-both-leaves-brickwork" }
];

export const SDSelectOptions = [
  // NF
  { label: "Predominance of blocks with larger dimension < 20 cm [NF]", value: "blocks-lt20cm" },
  { label: "Header bond (no stretchers) [NF]", value: "header-bond-no-stretchers" },
  // PF
  { label: "Predominance of blocks with larger dimension of 20–40 cm [PF]", value: "blocks-20-40cm" },
  { label: "Copresence of elements of different dimensions [PF]", value: "mixed-dimensions" },
  // F
  { label: "Predominance of blocks with larger dimension >40 cm [F]", value: "blocks-gt40cm" }
];

export const HJSelectOptions = [
  // NF
  { label: "Bed joints not continuous [NF]", value: "bed-joints-not-continuous" },
  // PF
  { label: "Bed joints partially continuous [PF]", value: "bed-joints-partially-continuous" },
  { label: "For double-leaf wall: only one leaf with continuous bed joints [PF]", value: "double-leaf-one-leaf-continuous" },
  // F
  { label: "Bed joints continuous [F]", value: "bed-joints-continuous" },
  { label: "Stone masonry wall with brick courses (<60 cm) [F]", value: "stone-masonry-brick-courses-lt60cm" }
];

export const WC_qualSelectOptions = [
  // NF
  { label: "Small stones / No headers [NF]", value: "small-stones-no-headers" },
  // PF
  { label: "Double-leaf walls: limited stone headers [PF]", value: "double-leaf-walls-limited-stone-headers" },
  { label: "Wall thickness larger than stone [PF]", value: "wall-thickness-larger-than-stone" },
  // F
  { label: "Wall thickness similar or larger than stone [F]", value: "wall-thickness-similar-larger-than-stone" }
];

export const VJ_qualSelectOptions = [
  // NF
  { label: "Vertically aligned head joints [NF]", value: "vertically-aligned-head-joints" },
  { label: "Vertically aligned head joints for at least 2 large stones [NF]", value: "vertically-aligned-head-joints-2-large" },
  { label: "Header bond (no stretchers) [NF]", value: "header-bond" },
  { label: "No mechanical interlocking between the stones [NF]", value: "no-interlocking" },
  // PF
  { label: "Partially staggered head joints (head joints in successive courses are not offset by one-half the unit length) [PF]", value: "partially-staggered-head-joints" },
  // F
  { label: "Properly staggered head joints (head joints in successive courses are oﬀset by one-half the unit length) [F]", value: "properly-staggered-head-joints" }
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

export type TextParameter = keyof typeof parametersTextSelectOptions;
export type TextParameterSelection = Record<TextParameter, { label: string; value: string }>;


export type MQIClassification = "NF" | "PF" | "F";
export type MQILocation = "V" | "I" | "O";

const classifier: Record<TextParameter, Record<"NF" | "PF", string[]>> = {
  SM: {
    NF: [
      "degraded-damaged-gt50",
      "hollow-core-bricks",
      "mud-bricks",
      "unfired-bricks"
    ],
    PF: [
      "degraded-damaged-10-50",
      "hollow-bricks",
      "sandstone-tuff-elements"
    ]
  },
  MM: {
    NF: [
      "very-weak-mortar-dusty-no-cohesion",
      "no-mortar-dry-rubble-pebble-stonework",
      "thick-bed-joints-weak-mortar-thickness-comparable-to-stone-brick",
      "porous-stones-bricks-weak-bond-to-mortar"
    ],
    PF: [
      "medium-quality-mortar-bed-joints-not-largely-notched",
      "masonry-irregular-rubble-stones-weak-mortar-pinning-stones"
    ]
  },
  SS: {
    NF: ["rubble-rounded-pebble-stones-predominant"],
    PF: [
      "copresence-rubble-rounded-pebble-barely-perfectly-cut-stones-one-leaf",
      "squared-blocks-bricks",
      "irregular-stones-with-pinning-stones"
    ]
  },
  SD: {
    NF: ["blocks-lt20cm", "header-bond-no-stretchers"],
    PF: ["blocks-20-40cm", "mixed-dimensions"]
  },
  HJ: {
    NF: ["bed-joints-not-continuous"],
    PF: ["bed-joints-partially-continuous", "double-leaf-one-leaf-continuous"]
  },
  WC_qual: {
    NF: ["small-stones-no-headers"],
    PF: [
      "double-leaf-walls-limited-stone-headers",
      "wall-thickness-larger-than-stone"
    ]
  },
  VJ_qual: {
    NF: [
      "vertically-aligned-head-joints",
      "vertically-aligned-head-joints-2-large",
      "header-bond",
      "no-interlocking"
    ],
    PF: ["partially-staggered-head-joints"]
  }
};

export function classifyTextParameter(parameter: TextParameter, value: string): MQIClassification {
  if (classifier[parameter].NF.includes(value)) {
    return "NF";
  } else if (classifier[parameter].PF.includes(value)) {
    return "PF";
  }

  return "F";
}

export function classifySM(value: string): MQIClassification {
  return classifyTextParameter("SM", value);
}

// === Mortar Quality (MM) ===
export function classifyMM(value: string): MQIClassification {
  return classifyTextParameter("MM", value);
}

// === Stone Shape (SS) ===
export function classifySS(value: string): MQIClassification {
  return classifyTextParameter("SS", value);
}

// === Stone Dimension (SD) ===
export function classifySD(value: string): MQIClassification {
  return classifyTextParameter("SD", value);
}

// === Horizontal Joints (HJ) ===
export function classifyHJ(value: string): MQIClassification {
  return classifyTextParameter("HJ", value);
}

// === Wall Connections - Qualitative (WC_qual) ===
export function classifyWC_qualitative(value: string): MQIClassification {
  return classifyTextParameter("WC_qual", value);
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
  return classifyTextParameter("VJ_qual", value);
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
