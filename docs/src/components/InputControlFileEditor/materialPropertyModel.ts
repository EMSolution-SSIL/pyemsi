import {deepClone, isEmSolutionInput, isPlainRecord, type JsonRecord} from './emSolutionModel';

export {deepClone, isPlainRecord};

const DOC_ROOT = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl';

export const MATERIAL_DOCUMENTATION = {
  overview: `${DOC_ROOT}/16_Material_Properties.html`,
  volume: `${DOC_ROOT}/16_1_3D_Element_Properties.html`,
  electrostatic: `${DOC_ROOT}/16_1_2_ES_3D_Element_Properties.html`,
  surface: `${DOC_ROOT}/16_2_2D_Element_Properties.html`,
} as const;

export const SURFACE_MATERIAL_TYPES = [
  'SURFACE_IMPEDANCE', 'GAP_ELEMENT', 'THIN_CONDUCTOR', 'SHELL_COIL',
] as const;

export type SurfaceMaterialType = typeof SURFACE_MATERIAL_TYPES[number];
export type MaterialSection = 'general' | 'volume' | 'surface';
export type MaterialFieldKind = 'integer' | 'number' | 'string' | 'enum' | 'vector3' | 'integer-array' | 'number-array';

export interface MaterialFieldOption {
  value: number;
  label: string;
}

export interface MaterialFieldDefinition {
  key: string;
  label: string;
  kind: MaterialFieldKind;
  help: string;
  unit?: string;
  options?: MaterialFieldOption[];
  required?: boolean;
  exactItems?: number;
  min?: number;
  max?: number;
  exclusiveMin?: number;
  exclusiveMax?: number;
}

export interface MaterialFieldGroupDefinition {
  key: string;
  label: string;
  description: string;
  documentationUrl: string;
  fields: MaterialFieldDefinition[];
}

export interface MaterialPropertyValidationIssue {
  severity: 'error' | 'warning';
  path: string;
  message: string;
  section?: MaterialSection;
  entryIndex?: number;
}

export interface KnownSurfaceMaterialEntry {
  kind: 'known';
  type: SurfaceMaterialType;
  definition: unknown;
  wrapper: JsonRecord;
}

export interface RawSurfaceMaterialEntry {
  kind: 'raw';
  reason: 'malformed' | 'unknown' | 'multiple';
  wrapper: unknown;
}

export type InspectedSurfaceMaterialEntry = KnownSurfaceMaterialEntry | RawSurfaceMaterialEntry;

const required = true;
const integer = (key: string, label: string, help: string, extra: Partial<MaterialFieldDefinition> = {}): MaterialFieldDefinition => (
  {key, label, kind: 'integer', help, required, ...extra}
);
const number = (key: string, label: string, help: string, unit?: string, extra: Partial<MaterialFieldDefinition> = {}): MaterialFieldDefinition => (
  {key, label, kind: 'number', help, unit, required, ...extra}
);
const string = (key: string, label: string, help: string, extra: Partial<MaterialFieldDefinition> = {}): MaterialFieldDefinition => (
  {key, label, kind: 'string', help, required, ...extra}
);
const vector3 = (key: string, label: string, help: string, unit?: string, extra: Partial<MaterialFieldDefinition> = {}): MaterialFieldDefinition => (
  {key, label, kind: 'vector3', help, unit, required, exactItems: 3, ...extra}
);
const integerArray = (key: string, label: string, help: string, exactItems: number): MaterialFieldDefinition => (
  {key, label, kind: 'integer-array', help, required, exactItems}
);
const numberArray = (key: string, label: string, help: string, exactItems: number, unit?: string): MaterialFieldDefinition => (
  {key, label, kind: 'number-array', help, unit, required, exactItems}
);
const enumField = (key: string, label: string, help: string, options: MaterialFieldOption[], extra: Partial<MaterialFieldDefinition> = {}): MaterialFieldDefinition => (
  {key, label, kind: 'enum', help, options, required, ...extra}
);

const BINARY: MaterialFieldOption[] = [
  {value: 0, label: '0 — Disabled'},
  {value: 1, label: '1 — Enabled'},
];

export const VOLUME_BASE_FIELDS: MaterialFieldDefinition[] = [
  integer('MAT_ID', 'Material ID', 'Volume-element material identifier.'),
  string('MAT_NAME', 'Material name', 'Optional human-readable material name used by EMSolution input files.', {required: false}),
  integer('POTENTIAL', 'Potential region', '0 selects the total-potential region; positive values identify modified-potential regions.', {required: false, min: 0}),
];

export const VOLUME_FLAG_FIELDS: MaterialFieldDefinition[] = [
  enumField('is_THIN_ELEMENT', 'Thin element', 'Apply THIN_ELEMENT behavior to this material.', BINARY, {required: false}),
  enumField('add_FORCE_for_DYNAMIC_MOTION', 'Dynamic-motion force region', 'Include the material in dynamic-motion electromagnetic-force integration.', BINARY, {required: false}),
  enumField('is_RIGID', 'Rigid moving region', 'Mark the material as a non-deforming moving-mesh region.', BINARY, {required: false}),
  enumField('is_DEFORM', 'Deforming moving region', 'Mark the material as a deforming moving-mesh region.', BINARY, {required: false}),
  enumField('is_DESIGN_DOMAIN', 'Design domain', 'Mark the material as a pyemsol design-domain material.', BINARY, {required: false}),
];

export const MATERIAL_FIELD_GROUPS: Record<string, MaterialFieldGroupDefinition> = {
  conductivity: {
    key: 'ElectricProperty.conductivity', label: 'Conductivity', description: 'Isotropic or local-coordinate anisotropic electrical conductivity.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [number('SIGMA', 'Conductivity', 'Isotropic electrical conductivity.', 'S/m')],
  },
  sigmaXyz: {
    key: 'ElectricProperty.conductivity.SIGMA_XYZ', label: 'Anisotropic conductivity', description: 'Local-coordinate conductivity factors.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'), numberArray('FACTOR_XYZ', 'XYZ factors', 'X, Y, and Z conductivity factors from 0 through 1.', 3)],
  },
  permittivity: {
    key: 'ElectricProperty.permittivity', label: 'Permittivity', description: 'Isotropic or local-coordinate anisotropic relative permittivity.',
    documentationUrl: MATERIAL_DOCUMENTATION.electrostatic, fields: [number('EPS', 'Relative permittivity', 'Isotropic relative permittivity.')],
  },
  epsXyz: {
    key: 'ElectricProperty.permittivity.EPS_XYZ', label: 'Anisotropic permittivity', description: 'Local-coordinate relative-permittivity factors.',
    documentationUrl: MATERIAL_DOCUMENTATION.electrostatic, fields: [integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'), numberArray('FACTOR_XYZ', 'XYZ factors', 'X, Y, and Z relative-permittivity factors from 0 through 1.', 3)],
  },
  magnetic: {
    key: 'MagneticProperty', label: 'Magnetic property', description: 'Base isotropic magnetic material values.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      number('MU', 'Relative permeability', 'Linear relative permeability.', undefined, {required: false}),
      integer('BH_CURVE_ID', 'B-H curve', 'B-H curve identifier; 0 selects linear permeability.', {required: false, min: 0}),
    ],
  },
  muXyz: {
    key: 'MagneticProperty.MU_XYZ', label: 'Anisotropic permeability', description: 'Local-coordinate linear-permeability factors.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'), numberArray('FACTOR_XYZ', 'XYZ factors', 'X, Y, and Z permeability factors from 0 through 1.', 3)],
  },
  packing: {
    key: 'MagneticProperty.PACKING', label: 'Lamination packing', description: 'Homogenized laminated-core packing definition.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      number('PACKING_FACTOR', 'Packing factor', 'Steel packing fraction, strictly between 0 and 1.', undefined, {exclusiveMin: 0, exclusiveMax: 1}),
      integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'),
      vector3('PACKING_DIRECTION', 'Packing direction', 'Unit vector normal to the laminations.'),
    ],
  },
  bhCurveXyz: {
    key: 'MagneticProperty.BH_CURVE_XYZ', label: 'XYZ B-H curves', description: 'Independent nonlinear magnetic characteristics along three local axes.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'),
      integerArray('BH_XYZ_ID', 'XYZ B-H curve IDs', 'B-H curve identifiers along X, Y, and Z.', 3),
      numberArray('MU_XYZ', 'XYZ permeability', 'Linear relative permeability used where the corresponding curve ID is 0.', 3),
    ],
  },
  anisotropy2d: {
    key: 'MagneticProperty.ANISOTROPY2D', label: '2D magnetic anisotropy', description: 'Nonlinear in-plane characteristic with an independent Z characteristic.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'),
      integer('BH_XY', 'XY B-H curve', 'Two-dimensional in-plane B-H curve identifier.'),
      integer('BH_Z', 'Z B-H curve', 'Optional Z-direction B-H curve identifier.', {required: false}),
      number('MU_Z', 'Z permeability', 'Optional linear Z-direction relative permeability.', undefined, {required: false}),
    ],
  },
  hysteresis: {
    key: 'MagneticProperty.HYSTERESIS', label: 'Hysteresis', description: 'Shared Jiles–Atherton or Play-model settings.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'),
      number('MU_Z', 'Z permeability', 'Linear Z-direction relative permeability.'),
      number('DB_CAL', 'Flux-density step', 'Magnetic-flux-density calculation step.', 'T'),
    ],
  },
  jaModel: {
    key: 'MagneticProperty.HYSTERESIS.J_A_Model', label: 'Jiles–Atherton model', description: 'Two-axis Jiles–Atherton hysteresis parameters.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      numberArray('MS', 'Saturation magnetization', 'X/Y saturation magnetization.', 2, 'A/m'),
      numberArray('K', 'Coercive field', 'X/Y coercive field magnitude.', 2, 'A/m'),
      numberArray('C', 'Weighting factor', 'X/Y magnetization weighting factor.', 2),
      numberArray('A', 'Anhysteretic factor', 'X/Y anhysteretic form factor.', 2, 'A/m'),
      numberArray('ALPHA', 'Coupling coefficient', 'X/Y interdomain coupling coefficient.', 2),
    ],
  },
  playModel: {
    key: 'MagneticProperty.HYSTERESIS.Play_Model', label: 'Play model', description: 'Play-model hysteresis parameters.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      integer('PLAY_ID', 'Play model ID', 'Identifier of the external Play-model shape data.'),
      number('DB_FACTOR', 'DB factor', 'Convergence multiplier applied to DB_CAL.'),
      number('B_MIN_LOSS_CORRECTION', 'Minimum loss-correction flux density', 'Lower flux-density threshold for rotational-loss correction.', 'T'),
    ],
  },
  muComplex: {
    key: 'MagneticProperty.MU_COMPLEX', label: 'Complex permeability', description: 'Scalar or three-axis complex relative permeability for AC analysis.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      number('MU_Re', 'Real permeability', 'Scalar real component.', undefined, {required: false}),
      number('MU_Im', 'Imaginary permeability', 'Scalar imaginary component.', undefined, {required: false}),
      integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier for XYZ values.', {required: false}),
      {...numberArray('MU_Re_XYZ', 'XYZ real permeability', 'Real components along X, Y, and Z.', 3), required: false},
      {...numberArray('MU_Im_XYZ', 'XYZ imaginary permeability', 'Imaginary components along X, Y, and Z.', 3), required: false},
    ],
  },
  ironLoss: {
    key: 'MagneticProperty.IRON_LOSS', label: 'Iron loss', description: 'Isotropic or anisotropic iron-loss coefficients.',
    documentationUrl: MATERIAL_DOCUMENTATION.volume, fields: [
      integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.'),
      number('MASS_DENSITY', 'Mass density', 'Electrical-steel density.', 'kg/m³'),
      number('KE', 'Eddy-current coefficient', 'Isotropic eddy-current loss coefficient.', undefined, {required: false}),
      number('KH', 'Hysteresis coefficient', 'Isotropic hysteresis loss coefficient.', undefined, {required: false}),
      {...numberArray('KE_XY', 'XY eddy-current coefficients', 'X/Y eddy-current loss coefficients.', 2), required: false},
      {...numberArray('KH_XYZ', 'XYZ hysteresis coefficients', 'X/Y/Z hysteresis loss coefficients.', 3), required: false},
    ],
  },
};

export const SURFACE_MATERIAL_SCHEMAS: Record<SurfaceMaterialType, MaterialFieldGroupDefinition> = {
  SURFACE_IMPEDANCE: {
    key: 'SURFACE_IMPEDANCE', label: 'Surface impedance', description: 'Linear, nonlinear, or mixed surface impedance.',
    documentationUrl: MATERIAL_DOCUMENTATION.surface, fields: [
      number('SIGMA', 'Conductivity', 'Surface material conductivity.', 'S/m'),
      number('MU', 'Relative permeability', 'Surface material relative permeability.'),
      enumField('IMP_TYPE', 'Impedance type', 'Linear or nonlinear impedance formulation.', [
        {value: 0, label: '0 — Linear'}, {value: 1, label: '1 — Nonlinear, sinusoidal H'},
        {value: 2, label: '2 — Nonlinear, sinusoidal E'}, {value: 3, label: '3 — Mixed, sinusoidal H'},
        {value: 4, label: '4 — Mixed, sinusoidal E'},
      ]),
    ],
  },
  GAP_ELEMENT: {
    key: 'GAP_ELEMENT', label: 'Gap element', description: 'Thin magnetic or insulating gap element.',
    documentationUrl: MATERIAL_DOCUMENTATION.surface, fields: [number('THICKNESS', 'Thickness', 'Gap thickness.', 'm', {exclusiveMin: 0})],
  },
  THIN_CONDUCTOR: {
    key: 'THIN_CONDUCTOR', label: 'Thin conductor', description: 'Nonmagnetic thin conducting sheet.',
    documentationUrl: MATERIAL_DOCUMENTATION.surface, fields: [
      number('THICKNESS', 'Thickness', 'Conductor thickness.', 'm', {exclusiveMin: 0}),
      number('SIGMA', 'Conductivity', 'Sheet conductivity.', 'S/m'),
    ],
  },
  SHELL_COIL: {
    key: 'SHELL_COIL', label: 'Shell coil', description: 'Surface-element coil thickness.',
    documentationUrl: MATERIAL_DOCUMENTATION.surface, fields: [number('THICKNESS', 'Thickness', 'Shell-coil thickness.', 'm', {exclusiveMin: 0})],
  },
};

export const NONLINEAR_IMPEDANCE_FIELDS: MaterialFieldDefinition[] = [
  integer('BH_CURVE_ID', 'B-H curve', 'Nonlinear B-H curve identifier.'),
  number('AGRWALL', 'Agarwal factor', 'Agarwal nonlinear surface-impedance factor.'),
  number('K', 'K value', 'Nonlinear surface-impedance K parameter.'),
  number('HK', 'Knee-point field', 'Magnetic field strength at the B-H curve knee point.', 'A/m'),
];

export function getMaterialField(value: unknown, path: string): unknown {
  return path.split('.').reduce<unknown>((current, part) => isPlainRecord(current) ? current[part] : undefined, value);
}

export function setMaterialField(value: JsonRecord, path: string, nextValue: unknown): void {
  const parts = path.split('.');
  let current = value;
  for (const part of parts.slice(0, -1)) {
    if (!isPlainRecord(current[part])) current[part] = {};
    current = current[part] as JsonRecord;
  }
  current[parts.at(-1)!] = nextValue;
}

export function removeMaterialField(value: JsonRecord, path: string): void {
  const parts = path.split('.');
  let current: unknown = value;
  for (const part of parts.slice(0, -1)) current = isPlainRecord(current) ? current[part] : undefined;
  if (isPlainRecord(current)) delete current[parts.at(-1)!];
}

export function findMaterialProperties(rootValue: unknown): JsonRecord {
  if (!isEmSolutionInput(rootValue) || !isPlainRecord(rootValue)) return {};
  return isPlainRecord(rootValue['16_Material_Properties']) ? rootValue['16_Material_Properties'] : {};
}

export function hasMalformedMaterialPropertyRoot(rootValue: unknown): boolean {
  if (!isPlainRecord(rootValue) || !Object.hasOwn(rootValue, '16_Material_Properties')) return false;
  const properties = rootValue['16_Material_Properties'];
  if (!isPlainRecord(properties)) return true;
  return ['16_1_3D_Element_Properties', '16_2_2D_Element_Properties'].some((key) => (
    Object.hasOwn(properties, key) && !Array.isArray(properties[key])
  ));
}

export function replaceMaterialProperties(rootValue: unknown, properties: unknown): unknown {
  const result = deepClone(rootValue);
  if (!isPlainRecord(result)) return result;
  result['16_Material_Properties'] = deepClone(properties);
  return result;
}

export function createMaterialProperties(rootValue?: unknown): JsonRecord {
  const existing = findMaterialProperties(rootValue);
  return {
    ...deepClone(existing),
    EXTEND_TOTAL_for_COIL: existing.EXTEND_TOTAL_for_COIL ?? 0,
    '16_1_3D_Element_Properties': Array.isArray(existing['16_1_3D_Element_Properties'])
      ? deepClone(existing['16_1_3D_Element_Properties']) : [],
    '16_2_2D_Element_Properties': Array.isArray(existing['16_2_2D_Element_Properties'])
      ? deepClone(existing['16_2_2D_Element_Properties']) : [],
  };
}

export function volumeMaterials(properties: unknown): unknown[] {
  return isPlainRecord(properties) && Array.isArray(properties['16_1_3D_Element_Properties'])
    ? properties['16_1_3D_Element_Properties'] : [];
}

export function surfaceMaterials(properties: unknown): unknown[] {
  return isPlainRecord(properties) && Array.isArray(properties['16_2_2D_Element_Properties'])
    ? properties['16_2_2D_Element_Properties'] : [];
}

export function replaceVolumeMaterials(properties: unknown, entries: unknown[]): JsonRecord {
  const result = isPlainRecord(properties) ? deepClone(properties) : {};
  result['16_1_3D_Element_Properties'] = deepClone(entries);
  return result;
}

export function replaceSurfaceMaterials(properties: unknown, entries: unknown[]): JsonRecord {
  const result = isPlainRecord(properties) ? deepClone(properties) : {};
  result['16_2_2D_Element_Properties'] = deepClone(entries);
  return result;
}

function analysisType(rootValue: unknown): JsonRecord {
  return isPlainRecord(rootValue) && isPlainRecord(rootValue['2_Analysis_Type']) ? rootValue['2_Analysis_Type'] : {};
}

export function createVolumeMaterial(rootValue?: unknown): JsonRecord {
  const analysis = analysisType(rootValue);
  if ([2, 3].includes(analysis.STATIC as number)) {
    return {MAT_ID: '', ElectricProperty: {conductivity: {SIGMA: 0}, permittivity: {EPS: 1}}};
  }
  const electric: JsonRecord = {conductivity: {SIGMA: 0}};
  if ([3, 4].includes(analysis.AC as number)) electric.permittivity = {EPS: 1};
  return {MAT_ID: '', POTENTIAL: 0, ElectricProperty: electric, MagneticProperty: {MU: 1}};
}

export function createSurfaceMaterial(type: SurfaceMaterialType): JsonRecord {
  const definitions: Record<SurfaceMaterialType, JsonRecord> = {
    SURFACE_IMPEDANCE: {SIGMA: 0, MU: 1, IMP_TYPE: 0},
    GAP_ELEMENT: {THICKNESS: ''},
    THIN_CONDUCTOR: {THICKNESS: '', SIGMA: 0},
    SHELL_COIL: {THICKNESS: ''},
  };
  return {SMAT_ID: '', [type]: definitions[type]};
}

export function isSurfaceMaterialType(value: string): value is SurfaceMaterialType {
  return (SURFACE_MATERIAL_TYPES as readonly string[]).includes(value);
}

export function inspectSurfaceMaterial(value: unknown): InspectedSurfaceMaterialEntry {
  if (!isPlainRecord(value)) return {kind: 'raw', reason: 'malformed', wrapper: value};
  const keys = Object.keys(value).filter(isSurfaceMaterialType);
  if (keys.length === 0) return {kind: 'raw', reason: 'unknown', wrapper: value};
  if (keys.length > 1) return {kind: 'raw', reason: 'multiple', wrapper: value};
  const type = keys[0] as SurfaceMaterialType;
  return {kind: 'known', type, definition: value[type], wrapper: value};
}

export function nonlinearParametersKey(value: unknown): 'Nonlinear_Parameters' | 'Nonliear_Parameters' {
  return isPlainRecord(value) && Object.hasOwn(value, 'Nonliear_Parameters') && !Object.hasOwn(value, 'Nonlinear_Parameters')
    ? 'Nonliear_Parameters' : 'Nonlinear_Parameters';
}

function finiteProblem(value: unknown, integerOnly = false): string | undefined {
  if (typeof value !== 'number' || !Number.isFinite(value)) return integerOnly ? 'must be an integer' : 'must be a finite number';
  if (integerOnly && !Number.isInteger(value)) return 'must be an integer';
  return undefined;
}

function validateFields(value: unknown, fields: MaterialFieldDefinition[], base: string, issue: (path: string, message: string) => void): void {
  if (!isPlainRecord(value)) return;
  for (const field of fields) {
    const fieldValue = value[field.key];
    if (!field.required && (fieldValue === undefined || fieldValue === '')) continue;
    const path = `${base}.${field.key}`;
    if (field.kind === 'integer' || field.kind === 'number') {
      const problem = finiteProblem(fieldValue, field.kind === 'integer');
      if (problem) { issue(path, `${field.label} ${problem}.`); continue; }
      const numberValue = fieldValue as number;
      if (field.min !== undefined && numberValue < field.min) issue(path, `${field.label} must be at least ${field.min}.`);
      if (field.max !== undefined && numberValue > field.max) issue(path, `${field.label} must be at most ${field.max}.`);
      if (field.exclusiveMin !== undefined && numberValue <= field.exclusiveMin) issue(path, `${field.label} must be greater than ${field.exclusiveMin}.`);
      if (field.exclusiveMax !== undefined && numberValue >= field.exclusiveMax) issue(path, `${field.label} must be less than ${field.exclusiveMax}.`);
    } else if (field.kind === 'string') {
      if (typeof fieldValue !== 'string' || (field.required && fieldValue.trim() === '')) issue(path, `${field.label} must be a string.`);
    } else if (field.kind === 'enum') {
      if (!field.options?.some((option) => option.value === fieldValue)) issue(path, `${field.label} must use a documented option.`);
    } else {
      if (!Array.isArray(fieldValue) || fieldValue.length !== field.exactItems) {
        issue(path, `${field.label} must contain exactly ${field.exactItems} values.`);
        continue;
      }
      const integerOnly = field.kind === 'integer-array';
      fieldValue.forEach((item, index) => {
        if (finiteProblem(item, integerOnly)) issue(`${path}[${index}]`, `${field.label} contains an invalid value.`);
        if (field.key === 'FACTOR_XYZ' && typeof item === 'number' && (item < 0 || item > 1)) issue(`${path}[${index}]`, `${field.label} values must be from 0 through 1.`);
      });
    }
  }
}

function bhCurveIds(rootValue: unknown): number[] {
  if (!isPlainRecord(rootValue)) return [];
  const raw = rootValue['20_BH_Curve'] ?? rootValue['20_B_H_Curve'];
  const rows = Array.isArray(raw) ? raw : raw === undefined ? [] : [raw];
  return rows.flatMap((row) => isPlainRecord(row) && Number.isInteger(row.BH_CURVE_ID) ? [row.BH_CURVE_ID as number] : []);
}

function validateVolume(entry: unknown, index: number, rootValue: unknown): MaterialPropertyValidationIssue[] {
  const issues: MaterialPropertyValidationIssue[] = [];
  const add = (severity: 'error' | 'warning', path: string, message: string) => issues.push({severity, path, message, section: 'volume', entryIndex: index});
  const base = `16_1_3D_Element_Properties[${index}]`;
  if (!isPlainRecord(entry)) { add('error', base, 'Volume material must be a JSON object.'); return issues; }
  validateFields(entry, VOLUME_BASE_FIELDS, base, (path, message) => add('error', path, message));
  validateFields(entry, VOLUME_FLAG_FIELDS, base, (path, message) => add('error', path, message));
  if (['conductivity', 'permittivity', 'permeability'].some((key) => Object.hasOwn(entry, key))) {
    add('warning', base, 'Legacy flat material properties are preserved but are not automatically migrated.');
  }
  const groups = Object.values(MATERIAL_FIELD_GROUPS);
  for (const group of groups) {
    const groupValue = getMaterialField(entry, group.key);
    if (groupValue === undefined) continue;
    if (!isPlainRecord(groupValue)) { add('error', `${base}.${group.key}`, `${group.label} must be an object.`); continue; }
    validateFields(groupValue, group.fields, `${base}.${group.key}`, (path, message) => add('error', path, message));
  }
  const magnetic = isPlainRecord(entry.MagneticProperty) ? entry.MagneticProperty : undefined;
  if (magnetic) {
    if (magnetic.TEMP_DEPEND_BH_CURVE_ID !== undefined && finiteProblem(magnetic.TEMP_DEPEND_BH_CURVE_ID, true)) {
      add('error', `${base}.MagneticProperty.TEMP_DEPEND_BH_CURVE_ID`, 'Temperature-dependent B-H curve ID must be an integer.');
    }
    const alternatives = ['BH_CURVE_XYZ', 'TEMP_DEPEND_BH_CURVE_ID', 'ANISOTROPY2D', 'HYSTERESIS', 'MU_COMPLEX'].filter((key) => magnetic[key] !== undefined);
    if (alternatives.length > 1) add('warning', `${base}.MagneticProperty`, `Several alternative magnetic models are present (${alternatives.join(', ')}); all values are preserved.`);
    const anisotropy = magnetic.ANISOTROPY2D;
    if (isPlainRecord(anisotropy)) {
      if (anisotropy.BH_Z === undefined && anisotropy.MU_Z === undefined) add('error', `${base}.MagneticProperty.ANISOTROPY2D`, 'Specify either BH_Z or MU_Z.');
      if (anisotropy.BH_Z !== undefined && anisotropy.MU_Z !== undefined) add('warning', `${base}.MagneticProperty.ANISOTROPY2D`, 'Both BH_Z and MU_Z are present; EMSolution normally uses one alternative.');
    }
    const hysteresis = magnetic.HYSTERESIS;
    if (isPlainRecord(hysteresis) && hysteresis.J_A_Model !== undefined && hysteresis.Play_Model !== undefined) {
      add('warning', `${base}.MagneticProperty.HYSTERESIS`, 'Both hysteresis models are present; all values are preserved.');
    }
    const complex = magnetic.MU_COMPLEX;
    if (isPlainRecord(complex)) {
      const scalarCount = ['MU_Re', 'MU_Im'].filter((key) => complex[key] !== undefined).length;
      const vectorCount = ['MU_Re_XYZ', 'MU_Im_XYZ'].filter((key) => complex[key] !== undefined).length;
      if (scalarCount === 1) add('error', `${base}.MagneticProperty.MU_COMPLEX`, 'Scalar complex permeability requires both MU_Re and MU_Im.');
      if (vectorCount === 1) add('error', `${base}.MagneticProperty.MU_COMPLEX`, 'XYZ complex permeability requires both MU_Re_XYZ and MU_Im_XYZ.');
    }
    const iron = magnetic.IRON_LOSS;
    if (isPlainRecord(iron)) {
      const scalarCount = ['KE', 'KH'].filter((key) => iron[key] !== undefined).length;
      const vectorCount = ['KE_XY', 'KH_XYZ'].filter((key) => iron[key] !== undefined).length;
      if (scalarCount === 1) add('error', `${base}.MagneticProperty.IRON_LOSS`, 'Isotropic iron loss requires both KE and KH.');
      if (vectorCount === 1) add('error', `${base}.MagneticProperty.IRON_LOSS`, 'Anisotropic iron loss requires both KE_XY and KH_XYZ.');
      if (scalarCount === 0 && vectorCount === 0) add('error', `${base}.MagneticProperty.IRON_LOSS`, 'Specify isotropic or anisotropic iron-loss coefficients.');
    }
    const packing = magnetic.PACKING;
    if (isPlainRecord(packing) && Array.isArray(packing.PACKING_DIRECTION) && packing.PACKING_DIRECTION.every((item) => typeof item === 'number')) {
      const length = Math.sqrt(packing.PACKING_DIRECTION.reduce((sum: number, item) => sum + (item as number) ** 2, 0));
      if (Math.abs(length - 1) > 1e-6) add('warning', `${base}.MagneticProperty.PACKING.PACKING_DIRECTION`, 'Packing direction is documented as a unit vector.');
    }
  }
  const availableCurves = bhCurveIds(rootValue);
  if (availableCurves.length > 0) {
    const referenced = [
      magnetic?.BH_CURVE_ID,
      ...(isPlainRecord(magnetic?.BH_CURVE_XYZ) && Array.isArray(magnetic.BH_CURVE_XYZ.BH_XYZ_ID) ? magnetic.BH_CURVE_XYZ.BH_XYZ_ID : []),
      isPlainRecord(magnetic?.ANISOTROPY2D) ? magnetic.ANISOTROPY2D.BH_Z : undefined,
    ].filter((value): value is number => Number.isInteger(value) && (value as number) > 0);
    for (const curve of referenced) if (!availableCurves.includes(curve)) add('warning', base, `B-H curve ID ${curve} was not found in 20_BH_Curve.`);
  }
  const analysis = analysisType(rootValue);
  if ([2, 3].includes(analysis.STATIC as number) && magnetic) add('warning', `${base}.MagneticProperty`, 'Magnetic properties are retained although STATIC mode 2/3 is documented as electric-field analysis.');
  return issues;
}

function validateSurface(entry: unknown, index: number): MaterialPropertyValidationIssue[] {
  const issues: MaterialPropertyValidationIssue[] = [];
  const add = (severity: 'error' | 'warning', path: string, message: string) => issues.push({severity, path, message, section: 'surface', entryIndex: index});
  const base = `16_2_2D_Element_Properties[${index}]`;
  const inspected = inspectSurfaceMaterial(entry);
  if (inspected.kind === 'raw') {
    add(inspected.reason === 'unknown' ? 'warning' : 'error', base, inspected.reason === 'unknown'
      ? 'Unsupported surface material is preserved as raw JSON.'
      : inspected.reason === 'multiple' ? 'A surface material must contain exactly one supported type.' : 'Surface material must be a JSON object.');
    return issues;
  }
  if (!isPlainRecord(inspected.wrapper)) return issues;
  validateFields(inspected.wrapper, [integer('SMAT_ID', 'Surface material ID', 'Surface-element material identifier.', {min: 1})], base, (path, message) => add('error', path, message));
  if (!isPlainRecord(inspected.definition)) { add('error', `${base}.${inspected.type}`, `${inspected.type} must be an object.`); return issues; }
  validateFields(inspected.definition, SURFACE_MATERIAL_SCHEMAS[inspected.type].fields, `${base}.${inspected.type}`, (path, message) => add('error', path, message));
  if (inspected.type === 'SURFACE_IMPEDANCE') {
    const key = nonlinearParametersKey(inspected.definition);
    const nonlinear = inspected.definition[key];
    if (typeof inspected.definition.IMP_TYPE === 'number' && inspected.definition.IMP_TYPE > 0 && nonlinear === undefined) {
      add('error', `${base}.${inspected.type}.${key}`, 'Nonlinear impedance parameters are required for IMP_TYPE 1 through 4.');
    }
    if (nonlinear !== undefined) {
      if (!isPlainRecord(nonlinear)) add('error', `${base}.${inspected.type}.${key}`, 'Nonlinear impedance parameters must be an object.');
      else validateFields(nonlinear, NONLINEAR_IMPEDANCE_FIELDS, `${base}.${inspected.type}.${key}`, (path, message) => add('error', path, message));
      if (key === 'Nonliear_Parameters') add('warning', `${base}.${inspected.type}.${key}`, 'Legacy Nonliear_Parameters spelling is retained.');
    }
  }
  if (inspected.type === 'THIN_CONDUCTOR' && inspected.definition.SIGMA_XYZ !== undefined) {
    if (!isPlainRecord(inspected.definition.SIGMA_XYZ)) add('error', `${base}.THIN_CONDUCTOR.SIGMA_XYZ`, 'Anisotropic conductivity must be an object.');
    else validateFields(inspected.definition.SIGMA_XYZ, MATERIAL_FIELD_GROUPS.sigmaXyz.fields, `${base}.THIN_CONDUCTOR.SIGMA_XYZ`, (path, message) => add('error', path, message));
  }
  return issues;
}

export function validateMaterialProperties(rootValue: unknown): MaterialPropertyValidationIssue[] {
  if (!isPlainRecord(rootValue)) return [{severity: 'error', path: '$', message: 'EMSolution input must be an object.'}];
  if (hasMalformedMaterialPropertyRoot(rootValue)) return [{severity: 'error', path: '16_Material_Properties', message: 'Material Properties and its collections must use the current object/array JSON format.', section: 'general'}];
  const properties = createMaterialProperties(rootValue);
  const issues: MaterialPropertyValidationIssue[] = [];
  if (![0, 1].includes(properties.EXTEND_TOTAL_for_COIL as number)) issues.push({severity: 'error', path: '16_Material_Properties.EXTEND_TOTAL_for_COIL', message: 'EXTEND_TOTAL_for_COIL must be 0 or 1.', section: 'general'});
  if (properties.THIN_CRITERION !== undefined && finiteProblem(properties.THIN_CRITERION)) issues.push({severity: 'error', path: '16_Material_Properties.THIN_CRITERION', message: 'THIN_CRITERION must be a finite number.', section: 'general'});
  const volumes = volumeMaterials(properties);
  volumes.forEach((entry, index) => issues.push(...validateVolume(entry, index, rootValue)));
  const volumeIds = new Map<number, number>();
  volumes.forEach((entry, index) => {
    if (!isPlainRecord(entry) || !Number.isInteger(entry.MAT_ID)) return;
    const previous = volumeIds.get(entry.MAT_ID as number);
    if (previous !== undefined) issues.push({severity: 'warning', path: `16_1_3D_Element_Properties[${index}].MAT_ID`, message: `MAT_ID duplicates entry ${previous + 1}.`, section: 'volume', entryIndex: index});
    else volumeIds.set(entry.MAT_ID as number, index);
  });
  const surfaces = surfaceMaterials(properties);
  surfaces.forEach((entry, index) => issues.push(...validateSurface(entry, index)));
  const surfaceIds = new Map<number, number>();
  surfaces.forEach((entry, index) => {
    if (!isPlainRecord(entry) || !Number.isInteger(entry.SMAT_ID)) return;
    const previous = surfaceIds.get(entry.SMAT_ID as number);
    if (previous !== undefined) issues.push({severity: 'warning', path: `16_2_2D_Element_Properties[${index}].SMAT_ID`, message: `SMAT_ID duplicates entry ${previous + 1}.`, section: 'surface', entryIndex: index});
    else surfaceIds.set(entry.SMAT_ID as number, index);
  });
  return issues;
}

export function volumeMaterialSummary(value: unknown): string {
  if (!isPlainRecord(value)) return 'Malformed raw entry';
  const name = typeof value.MAT_NAME === 'string' && value.MAT_NAME.trim() ? value.MAT_NAME : `MAT_ID ${String(value.MAT_ID ?? '—')}`;
  const electric = isPlainRecord(value.ElectricProperty) ? Object.keys(value.ElectricProperty).length : 0;
  const magnetic = isPlainRecord(value.MagneticProperty) ? Object.keys(value.MagneticProperty).length : 0;
  return `${name} · ${electric} electric · ${magnetic} magnetic setting(s)`;
}

export function surfaceMaterialSummary(value: unknown): string {
  const inspected = inspectSurfaceMaterial(value);
  if (inspected.kind === 'raw') return inspected.reason === 'unknown' ? 'Unsupported raw definition' : 'Malformed raw entry';
  if (!isPlainRecord(inspected.definition)) return 'Malformed definition';
  const thickness = inspected.definition.THICKNESS;
  return thickness === undefined ? SURFACE_MATERIAL_SCHEMAS[inspected.type].label : `Thickness ${String(thickness)} m`;
}
