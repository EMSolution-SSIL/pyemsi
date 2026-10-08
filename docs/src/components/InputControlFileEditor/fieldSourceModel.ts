import {
  collectEmSolutionReferences,
  deepClone,
  isEmSolutionInput,
  isPlainRecord,
  type JsonRecord,
} from './emSolutionModel';
import {normalizeCircuit, validateCircuit} from './circuitModel';
import {normalizeNetwork, validateNetwork} from './networkModel';

export {deepClone, isPlainRecord};

const DOC_ROOT = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl';

export const FIELD_SOURCE_TYPES = [
  'COIL', 'ELMCUR', 'SDEFCOIL', 'PHICOIL', 'DCCURR', 'SUFCUR',
  'SUFCUR2', 'MAGNET', 'CIRCUIT', 'NETWORK', 'EPOTSUF', 'POTNODE',
] as const;

export type FieldSourceType = typeof FIELD_SOURCE_TYPES[number];
export type FieldSourceFieldKind =
  | 'integer' | 'number' | 'string' | 'enum' | 'vector3' | 'integer-array' | 'number-array';
export type MaterialReferenceKind = 'volume' | 'surface';

export interface FieldSourceOption {
  value: number;
  label: string;
}

export interface FieldSourceCondition {
  key: string;
  values: number[];
}

export interface FieldSourceFieldDefinition {
  key: string;
  label: string;
  kind: FieldSourceFieldKind;
  help: string;
  unit?: string;
  options?: FieldSourceOption[];
  required?: boolean;
  minItems?: number;
  exactItems?: number;
  visibleWhen?: FieldSourceCondition;
  defaultValue?: unknown;
  materialReference?: MaterialReferenceKind;
  timeReference?: boolean;
}

export interface FieldSourceRowSchema {
  type?: string;
  label: string;
  description: string;
  fields: FieldSourceFieldDefinition[];
}

export interface FieldSourceSchema {
  type: FieldSourceType;
  label: string;
  description: string;
  documentationUrl: string;
  fields: FieldSourceFieldDefinition[];
  rowLabel?: string;
  rowSchema?: FieldSourceRowSchema;
  rowSchemas?: Record<string, FieldSourceRowSchema>;
}

export interface FieldSourceValidationIssue {
  severity: 'error' | 'warning';
  path: string;
  message: string;
  sourceIndex?: number;
}

export interface KnownFieldSourceEntry {
  kind: 'known';
  type: FieldSourceType;
  key: string;
  definition: unknown;
  wrapper: JsonRecord;
}

export interface RawFieldSourceEntry {
  kind: 'raw';
  reason: 'malformed' | 'unknown' | 'multiple';
  wrapper: unknown;
}

export type InspectedFieldSourceEntry = KnownFieldSourceEntry | RawFieldSourceEntry;

const required = true;
const BINARY: FieldSourceOption[] = [
  {value: 0, label: '0 — No / fixed region'},
  {value: 1, label: '1 — Yes / moving region'},
];

const integer = (key: string, label: string, help: string, extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'integer', help, required, ...extra}
);
const number = (key: string, label: string, help: string, unit?: string, extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'number', help, unit, required, ...extra}
);
const string = (key: string, label: string, help: string, extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'string', help, required, ...extra}
);
const vector3 = (key: string, label: string, help: string, unit?: string, extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'vector3', help, unit, required, ...extra}
);
const integerArray = (key: string, label: string, help: string, extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'integer-array', help, required, minItems: 1, ...extra}
);
const numberArray = (key: string, label: string, help: string, unit?: string, extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'number-array', help, unit, required, minItems: 1, ...extra}
);
const enumField = (key: string, label: string, help: string, options: FieldSourceOption[], extra: Partial<FieldSourceFieldDefinition> = {}): FieldSourceFieldDefinition => (
  {key, label, kind: 'enum', help, options, required, ...extra}
);

const SERIES_ID = integer('SERIES_ID', 'Series ID', 'Identifier used when connecting this source to CIRCUIT or NETWORK.');
const TIME_ID = integer('TIME_ID', 'Time function', 'TIME_ID from 18_Time_Function; use 0 where the source is driven by CIRCUIT or NETWORK.', {timeReference: true});
const IN_ROTOR = enumField('IN_ROTOR', 'Region', 'Whether the source belongs to the fixed or moving region.', BINARY);
const MAT_ID = integer('MAT_ID', 'Material ID', 'Volume-element material identifier.', {materialReference: 'volume'});
const SMAT_ID = integer('SMAT_ID', 'Surface material ID', 'Surface-element material identifier.', {materialReference: 'surface'});
const CURRENT = number('CURRENT', 'Current', 'Normalized current value.', 'A');
const SIGMA = number('SIGMA', 'Conductivity', 'Electrical conductivity assigned to the source region.', 'S/m');
const CAL_JE = enumField('CAL_Je', 'Include eddy current', 'Whether eddy current is calculated in the defined region.', BINARY);
const COORD_ID = integer('COORD_ID', 'Coordinate system', 'Local coordinate-system identifier.');
const MXYZ = vector3('MXYZ', 'Magnetization vector', 'Magnetization components in the selected coordinate system.', 'T');

const coilRows: Record<string, FieldSourceRowSchema> = {
  UNIF: {type: 'UNIF', label: 'Uniform field', description: 'Uniform normalized magnetic flux density.', fields: [
    vector3('B_XYZ', 'Flux density', 'Normalized X, Y, and Z magnetic flux-density components.', 'T'),
    integer('A_FORM', 'Vector-potential form', 'Representation used for the uniform magnetic vector potential.'),
  ]},
  LOOP: {type: 'LOOP', label: 'Axisymmetric loop', description: 'Axisymmetric rectangular-section coil.', fields: [
    CURRENT, number('RADIUS', 'Mean radius', 'Mean loop radius.'), number('CENTER_Z', 'Center Z', 'Z coordinate of the loop center.'),
    number('RADIAL_W', 'Radial width', 'Radial section width.'), number('AXIAL_W', 'Axial width', 'Axial section width.'),
  ]},
  GCE: {type: 'GCE', label: 'Rectangular current element', description: 'Straight rectangular-section current element.', fields: [
    CURRENT, vector3('S_XYZ', 'Start point', 'Start coordinates.'), vector3('E_XYZ', 'End point', 'End coordinates.'),
    vector3('W1_XYZ', 'Start width', 'Width vector at the start.'), vector3('W2_XYZ', 'End width', 'Width vector at the end.'),
  ]},
  ARC: {type: 'ARC', label: 'Arc current element', description: 'Rectangular-section circular-arc current element.', fields: [
    CURRENT, vector3('XYZ', 'Reference point', 'Arc reference coordinates.'), number('RADIUS', 'Radius', 'Arc radius.'),
    number('AXIAL_W', 'Axial width', 'Axial section width.'), number('RADIAL_W', 'Radial width', 'Radial section width.'),
    number('ALPHA', 'Alpha', 'Euler angle alpha.', 'deg'), number('BETA', 'Beta', 'Euler angle beta.', 'deg'),
    number('PHI1', 'Start angle', 'Arc start angle.', 'deg'), number('PHI2', 'End angle', 'Arc end angle.', 'deg'),
  ]},
  FGCE: {type: 'FGCE', label: 'Straight line current', description: 'Finite straight line-current element.', fields: [
    CURRENT, vector3('S_XYZ', 'Start point', 'Start coordinates.'), vector3('E_XYZ', 'End point', 'End coordinates.'),
  ]},
  FARC: {type: 'FARC', label: 'Arc line current', description: 'Finite circular-arc line-current element.', fields: [
    CURRENT, vector3('XYZ0', 'Reference point', 'Arc reference coordinates.'), number('RADIUS', 'Radius', 'Arc radius.'),
    number('ALPHA', 'Alpha', 'Euler angle alpha.', 'deg'), number('BETA', 'Beta', 'Euler angle beta.', 'deg'),
    number('PHI1', 'Start angle', 'Arc start angle.', 'deg'), number('PHI2', 'End angle', 'Arc end angle.', 'deg'),
  ]},
  MESH: {type: 'MESH', label: 'Meshed coil', description: 'Current source imported from a meshed-coil definition.', fields: [
    CURRENT, integer('MESH_ID', 'Mesh ID', 'Meshed-coil identifier.'),
  ]},
  LINE: {type: 'LINE', label: 'Infinite line current', description: 'Infinite straight line-current source.', fields: [
    CURRENT, vector3('XYZ0', 'Point on line', 'Coordinates of a point on the line.'), vector3('DXYZ', 'Direction', 'Line direction vector.'),
  ]},
  DIPO: {type: 'DIPO', label: 'Dipole field', description: 'Normalized magnetic dipole-gradient field.', fields: [
    number('DBZDX', 'dBz/dx', 'Normalized Z-field gradient in the X direction.', 'T/m'),
  ]},
  EXMAG: {type: 'EXMAG', label: 'External permanent magnet', description: 'Permanent-magnet field imported from an external mesh.', fields: [
    enumField('READ_OPTION', 'Read option', 'External magnet-data read mode.', [
      {value: 0, label: '0 — EXMAG_magnetization'}, {value: 1, label: '1 — EXMAG_mesh'},
    ]), MAT_ID, COORD_ID, MXYZ,
  ]},
};

for (const base of ['LOOP', 'GCE', 'ARC', 'MESH'] as const) {
  const type = `${base}-`;
  coilRows[type] = {
    type,
    label: `${coilRows[base].label} (integrated)`,
    description: `Integration-region companion for a ${base} element in the same COIL series.`,
    fields: [
      integer('NDIV', 'Integration divisions', 'Number of divisions in the current direction.', {defaultValue: 1}),
      integer('INT_X', 'X Gauss points', 'Gauss integration-point count in the local X direction.', {defaultValue: 5}),
      integer('INT_Y', 'Y Gauss points', 'Gauss integration-point count in the local Y direction.', {defaultValue: 5}),
      integer('INT_Z', 'Z Gauss points', 'Gauss integration-point count in the current direction.', {defaultValue: 3}),
    ],
  };
}

const conductorRow = (label: string, fields: FieldSourceFieldDefinition[]): FieldSourceRowSchema => ({
  label, description: `One ${label.toLowerCase()} definition.`, fields,
});

const MAGNET_INPUT_OPTIONS: FieldSourceOption[] = [
  {value: 0, label: '0 — Uniform by material'},
  {value: 1, label: '1 — Per element'},
  {value: 2, label: '2 — Harmonic distribution'},
  {value: 3, label: '3 — Formula distribution'},
  {value: 4, label: '4 — Nonlinear demagnetization'},
  {value: 5, label: '5 — Temperature-dependent demagnetization'},
];

export const FIELD_SOURCE_SCHEMAS: Record<FieldSourceType, FieldSourceSchema> = {
  COIL: {
    type: 'COIL', label: 'External coil / magnetic field', description: 'External Biot–Savart coil or magnetic-field source independent of the finite-element mesh.',
    documentationUrl: `${DOC_ROOT}/17_1_COIL.html`, fields: [SERIES_ID, TIME_ID, integer('MOTION_ID', 'Motion ID', 'Motion identifier used when the coil moves.', {defaultValue: 0}), IN_ROTOR,
      integer('POTENTIAL', 'Potential region', 'Modified-potential region identifier.', {defaultValue: 1}), enumField('TO_MESHED_COIL', 'Convert to meshed coil', 'Whether to convert this source to a meshed coil.', BINARY)],
    rowLabel: 'COIL element', rowSchemas: coilRows,
  },
  ELMCUR: {
    type: 'ELMCUR', label: 'Internal current', description: 'Current source inside finite elements using element face numbers for inflow and outflow.',
    documentationUrl: `${DOC_ROOT}/17_2_ELMCUR.html`, fields: [SERIES_ID, enumField('OPTION', 'Current option', 'Method used to prescribe current.', [{value: 0, label: '0 — Total current'}, {value: 1, label: '1 — Current density'}]), IN_ROTOR], rowLabel: 'Current region',
    rowSchema: conductorRow('Current region', [MAT_ID, integer('IN_SURFACE', 'Inflow face', 'Element face number where current enters.'), integer('OUT_SURFACE', 'Outflow face', 'Element face number where current leaves.'), CURRENT, SIGMA, CAL_JE]),
  },
  SDEFCOIL: {
    type: 'SDEFCOIL', label: 'Surface-defined coil', description: 'Coil current distribution defined by four surrounding surface materials.',
    documentationUrl: `${DOC_ROOT}/17_3_SDEFCOIL.html`, fields: [SERIES_ID, IN_ROTOR], rowLabel: 'Coil region',
    rowSchema: conductorRow('Coil region', [MAT_ID, integerArray('SMAT_IDS', 'Boundary surfaces', 'Four surface material IDs surrounding the conductor.', {exactItems: 4, materialReference: 'surface'}), CURRENT, SIGMA, CAL_JE]),
  },
  PHICOIL: {
    type: 'PHICOIL', label: 'Potential current source', description: 'Potential-derived current distribution for a single conductor region.',
    documentationUrl: `${DOC_ROOT}/17_4_PHICOIL.html`, fields: [SERIES_ID, IN_ROTOR], rowLabel: 'Conductor',
    rowSchema: conductorRow('Conductor', [integerArray('MAT_IDS', 'Material IDs', 'Volume material IDs forming the conductor.', {materialReference: 'volume'}), SMAT_ID, CURRENT, SIGMA, CAL_JE]),
  },
  DCCURR: {
    type: 'DCCURR', label: 'Multi-conductor potential current', description: 'Potential-derived current distribution spanning multiple conductor materials.',
    documentationUrl: `${DOC_ROOT}/17_5_DCCURR.html`, fields: [SERIES_ID, IN_ROTOR], rowLabel: 'Conductor group',
    rowSchema: conductorRow('Conductor group', [integerArray('MAT_IDS', 'Material IDs', 'Volume material IDs forming the conductor group.', {materialReference: 'volume'}), SMAT_ID, CURRENT, numberArray('SIGMA', 'Conductivities', 'Conductivity for each material ID.', 'S/m'), CAL_JE]),
  },
  SUFCUR: {
    type: 'SUFCUR', label: 'Surface current', description: 'Current entering through a surface while eddy current is solved in the conductor.',
    documentationUrl: `${DOC_ROOT}/17_6_SUFCUR.html`, fields: [SERIES_ID, TIME_ID, SMAT_ID, CURRENT, IN_ROTOR],
  },
  SUFCUR2: {
    type: 'SUFCUR2', label: 'Multi-conductor surface current', description: 'Surface inflow current applied to multiple conductor regions.',
    documentationUrl: `${DOC_ROOT}/17_6_SUFCUR.html`, fields: [SERIES_ID, IN_ROTOR], rowLabel: 'Conductor',
    rowSchema: conductorRow('Conductor', [integerArray('MAT_IDS', 'Material IDs', 'Volume material IDs forming the conductor.', {materialReference: 'volume'}), SMAT_ID, CURRENT, CAL_JE]),
  },
  MAGNET: {
    type: 'MAGNET', label: 'Magnetization vector', description: 'Linear, distributed, nonlinear, or temperature-dependent permanent-magnet source.',
    documentationUrl: `${DOC_ROOT}/17_7_MAGNET.html`, fields: [
      SERIES_ID, TIME_ID, enumField('INPUT_TYPE', 'Input type', 'Magnetization input mode.', MAGNET_INPUT_OPTIONS),
      integer('MAT_ID', 'Material ID', 'Material containing per-element magnetization data.', {materialReference: 'volume', visibleWhen: {key: 'INPUT_TYPE', values: [1]}}),
      integer('COORD_ID', 'Coordinate system', 'Coordinate system for per-element magnetization data.', {visibleWhen: {key: 'INPUT_TYPE', values: [1]}}),
      enumField('READ_OPTION', 'Read option', 'Per-element magnetization read mode.', [{value: 0, label: '0 — Inline data'}, {value: 1, label: '1 — External file'}], {visibleWhen: {key: 'INPUT_TYPE', values: [1]}}),
      string('INITIAL_MAGNETIZATION_FILE_NAME', 'Initial magnetization file', 'External per-element magnetization filename.', {required: false, visibleWhen: {key: 'INPUT_TYPE', values: [1]}}),
      integer('NO_ORDERS', 'Number of harmonics', 'Number of harmonic orders; normally inferred from ORDERS in JSON.', {required: false, visibleWhen: {key: 'INPUT_TYPE', values: [2]}}),
      integerArray('ORDERS', 'Harmonic orders', 'Orders of the sinusoidal magnetization components.', {visibleWhen: {key: 'INPUT_TYPE', values: [2]}}),
      numberArray('AMPLITUDES', 'Harmonic amplitudes', 'Amplitude for each harmonic order.', undefined, {visibleWhen: {key: 'INPUT_TYPE', values: [2]}}),
      integer('NO_POLES', 'Number of poles', 'Pole count for the harmonic distribution.', {visibleWhen: {key: 'INPUT_TYPE', values: [2]}}),
      number('ANGLE', 'Reference angle', 'Reference angle of the harmonic distribution.', 'deg', {visibleWhen: {key: 'INPUT_TYPE', values: [2]}}),
      string('FUNCTION_MX', 'Mx formula', 'Formula defining the X magnetization component.', {visibleWhen: {key: 'INPUT_TYPE', values: [3]}}),
      string('FUNCTION_MY', 'My formula', 'Formula defining the Y magnetization component.', {visibleWhen: {key: 'INPUT_TYPE', values: [3]}}),
      string('FUNCTION_MZ', 'Mz formula', 'Formula defining the Z magnetization component.', {visibleWhen: {key: 'INPUT_TYPE', values: [3]}}),
    ], rowLabel: 'Magnet region',
  },
  CIRCUIT: {
    type: 'CIRCUIT', label: 'Circuit connection', description: 'Series, power-supply, impedance-matrix, and connection-matrix definition.',
    documentationUrl: `${DOC_ROOT}/17_8_CIRCUIT.html`, fields: [],
  },
  NETWORK: {
    type: 'NETWORK', label: 'External network', description: 'External lumped-element circuit network connected to FEM source series.',
    documentationUrl: `${DOC_ROOT}/17_9_NETWORK.html`, fields: [],
  },
  EPOTSUF: {
    type: 'EPOTSUF', label: 'Equipotential surface source', description: 'Electric potential, charge, or current applied to an equipotential surface.',
    documentationUrl: `${DOC_ROOT}/17_10_EPOTSUF.html`, fields: [SERIES_ID, SMAT_ID,
      enumField('POT_OR_CHARGE', 'Prescribed quantity', 'Choose whether potential or total charge/current is prescribed.', [{value: 0, label: '0 — Charge / current'}, {value: 1, label: '1 — Potential'}]),
      TIME_ID, enumField('UNIT_TYPE', 'Charge unit', 'For electrostatic charge input, select total or surface-density units.', [{value: 0, label: '0 — Total'}, {value: 1, label: '1 — Per area'}], {visibleWhen: {key: 'POT_OR_CHARGE', values: [0]}})],
  },
  POTNODE: {
    type: 'POTNODE', label: 'Node potential source', description: 'Normalized electric potential assigned to selected mesh nodes.',
    documentationUrl: `${DOC_ROOT}/17_11_POTNODE.html`, fields: [SERIES_ID, integer('SMAT_ID', 'Surface material ID', 'Optional surface material used to accelerate node lookup; use 0 when omitted.', {defaultValue: 0, materialReference: 'surface'}), TIME_ID,
      integerArray('NODE_IDS', 'Node IDs', 'Mesh node identifiers receiving prescribed potential.'),
      numberArray('POTENTIALS', 'Potential values', 'Normalized potential for each node ID.', 'V')],
  },
};

const magnetRows: Record<number, FieldSourceRowSchema> = {
  0: conductorRow('Uniform magnet region', [MAT_ID, COORD_ID, MXYZ]),
  1: conductorRow('Magnetized element', [integer('ELEM_ID', 'Element ID', 'Mesh element identifier.'), MXYZ]),
  2: conductorRow('Harmonic magnet region', [MAT_ID, COORD_ID, MXYZ]),
  3: conductorRow('Formula magnet region', [MAT_ID, COORD_ID]),
  4: conductorRow('Nonlinear magnet region', [MAT_ID, enumField('TYPE', 'Curve type', 'Nonlinear/demagnetization solution mode.', [{value: 0, label: '0 — Nonlinear'}, {value: 1, label: '1 — Demagnetization'}, {value: 2, label: '2 — Demagnetization with recoil history'}]), integer('BH_MAGNET_CURVE_ID', 'Demagnetization curve', 'Magnet demagnetization-curve identifier.'), number('MU', 'Recoil permeability', 'Relative permeability away from the easy axis.'), COORD_ID, MXYZ]),
  5: conductorRow('Temperature-dependent magnet region', [MAT_ID, enumField('TYPE', 'Curve type', 'Temperature-dependent nonlinear/demagnetization solution mode.', [{value: 0, label: '0 — Nonlinear'}, {value: 1, label: '1 — Demagnetization'}, {value: 2, label: '2 — Demagnetization with recoil history'}]), integer('BH_MAGNET_CURVE_ID', 'Temperature-dependent curve', 'Temperature-dependent magnet demagnetization-curve identifier.'), number('MU', 'Recoil permeability', 'Relative permeability away from the easy axis.'), COORD_ID, MXYZ]),
};

export function isFieldSourceType(value: string): value is FieldSourceType {
  return (FIELD_SOURCE_TYPES as readonly string[]).includes(value);
}

export function fieldSourceRows(value: unknown): unknown[] {
  return isPlainRecord(value) && Array.isArray(value.data) ? value.data : [];
}

export function visibleFieldSourceFields(fields: FieldSourceFieldDefinition[], value: unknown): FieldSourceFieldDefinition[] {
  if (!isPlainRecord(value)) return fields.filter((field) => !field.visibleWhen);
  return fields.filter((field) => !field.visibleWhen || field.visibleWhen.values.includes(value[field.visibleWhen.key] as number));
}

export function rowSchemaForSource(type: FieldSourceType, definition: unknown, row: unknown): FieldSourceRowSchema | undefined {
  const schema = FIELD_SOURCE_SCHEMAS[type];
  if (type === 'COIL') {
    return isPlainRecord(row) && typeof row.type === 'string' ? schema.rowSchemas?.[row.type] : undefined;
  }
  if (type === 'MAGNET') {
    return isPlainRecord(definition) && Number.isInteger(definition.INPUT_TYPE)
      ? magnetRows[definition.INPUT_TYPE as number]
      : undefined;
  }
  return schema.rowSchema;
}

export function sourceRowTypes(type: FieldSourceType): string[] {
  return type === 'COIL' ? Object.keys(coilRows) : [];
}

export function inspectFieldSourceEntry(value: unknown): InspectedFieldSourceEntry {
  if (!isPlainRecord(value)) return {kind: 'raw', reason: 'malformed', wrapper: value};
  const supportedKeys = Object.keys(value).filter((key) => isFieldSourceType(key) || key === 'EPOTNODE');
  if (supportedKeys.length === 0) return {kind: 'raw', reason: 'unknown', wrapper: value};
  if (supportedKeys.length > 1) return {kind: 'raw', reason: 'multiple', wrapper: value};
  const key = supportedKeys[0];
  const type: FieldSourceType = key === 'EPOTNODE' ? 'POTNODE' : key as FieldSourceType;
  return {kind: 'known', type, key, definition: value[key], wrapper: value};
}

export function findFieldSourceEntries(value: unknown): unknown[] {
  if (!isEmSolutionInput(value) || !isPlainRecord(value)) return [];
  const sources = value['17_Field_Source'];
  return Array.isArray(sources) ? sources : [];
}

export function hasMalformedFieldSourceRoot(value: unknown): boolean {
  return isPlainRecord(value) && Object.hasOwn(value, '17_Field_Source') && !Array.isArray(value['17_Field_Source']);
}

export function replaceFieldSourceEntries(value: unknown, entries: unknown[]): unknown {
  const result = deepClone(value);
  if (!isPlainRecord(result)) return result;
  result['17_Field_Source'] = deepClone(entries);
  return result;
}

function defaultFieldValue(field: FieldSourceFieldDefinition): unknown {
  if (field.defaultValue !== undefined) return deepClone(field.defaultValue);
  if (field.kind === 'enum') return field.options?.[0]?.value ?? 0;
  if (field.kind === 'vector3') return ['', '', ''];
  if (field.kind === 'integer-array' || field.kind === 'number-array') return [];
  return '';
}

export function createFieldSourceDefinition(type: FieldSourceType): JsonRecord {
  if (type === 'NETWORK') return {REGION_FACTOR: 1, REGION_PARALLEL: 1, data: []};
  if (type === 'CIRCUIT') return {
    REGION_FACTOR: 1,
    REGION_PARALLEL: 1,
    SERIES_IDS: [],
    POWER_SUPPLIES: [],
    INDUCTANCE_MATRIX: {IN_IND: 2, MATRIX: []},
    RESISTANCE_MATRIX: {IN_RES: 2, MATRIX: []},
    CONNECTION_MATRIX: {IN_CON: 0, MATRIX: []},
  };
  const result: JsonRecord = {};
  const fields = FIELD_SOURCE_SCHEMAS[type].fields;
  for (const field of fields.filter((item) => !item.visibleWhen)) {
    result[field.key] = defaultFieldValue(field);
  }
  for (const field of visibleFieldSourceFields(fields, result).filter((item) => item.visibleWhen)) {
    result[field.key] = defaultFieldValue(field);
  }
  if (FIELD_SOURCE_SCHEMAS[type].rowLabel) result.data = [];
  return result;
}

export function createFieldSourceEntry(type: FieldSourceType): JsonRecord {
  return {[type]: createFieldSourceDefinition(type)};
}

export function createFieldSourceRow(type: FieldSourceType, definition: unknown, rowType?: string): JsonRecord {
  let schema: FieldSourceRowSchema | undefined;
  const result: JsonRecord = {};
  if (type === 'COIL') {
    const selected = rowType && coilRows[rowType] ? rowType : Object.keys(coilRows)[0];
    result.type = selected;
    schema = coilRows[selected];
  } else {
    schema = rowSchemaForSource(type, definition, undefined);
  }
  for (const field of schema?.fields ?? []) setFieldValue(result, field.key, defaultFieldValue(field));
  return result;
}

export function getFieldValue(value: unknown, path: string): unknown {
  if (!isPlainRecord(value)) return undefined;
  return path.split('.').reduce<unknown>((current, key) => isPlainRecord(current) ? current[key] : undefined, value);
}

export function setFieldValue(value: JsonRecord, path: string, nextValue: unknown): void {
  const parts = path.split('.');
  let current = value;
  for (const part of parts.slice(0, -1)) {
    if (!isPlainRecord(current[part])) current[part] = {};
    current = current[part] as JsonRecord;
  }
  current[parts.at(-1)!] = nextValue;
}

function numberProblem(value: unknown, integerOnly: boolean): string | undefined {
  if (typeof value !== 'number' || !Number.isFinite(value)) return integerOnly ? 'must be an integer' : 'must be a finite number';
  if (integerOnly && !Number.isInteger(value)) return 'must be an integer';
  return undefined;
}

function validateFields(
  value: unknown,
  fields: FieldSourceFieldDefinition[],
  base: string,
  references: ReturnType<typeof collectEmSolutionReferences>,
  issues: FieldSourceValidationIssue[],
): void {
  if (!isPlainRecord(value)) return;
  for (const field of visibleFieldSourceFields(fields, value)) {
    const fieldValue = getFieldValue(value, field.key);
    const path = `${base}.${field.key}`;
    if (!field.required && (fieldValue === undefined || fieldValue === '')) continue;
    if (field.kind === 'integer' || field.kind === 'number') {
      const problem = numberProblem(fieldValue, field.kind === 'integer');
      if (problem) issues.push({severity: 'error', path, message: `${field.label} ${problem}.`});
    } else if (field.kind === 'enum') {
      const problem = numberProblem(fieldValue, true);
      if (problem || !field.options?.some((option) => option.value === fieldValue)) {
        issues.push({severity: 'error', path, message: `${field.label} must use a documented option.`});
      }
    } else if (field.kind === 'string') {
      if (typeof fieldValue !== 'string' || (field.required && fieldValue.trim() === '')) {
        issues.push({severity: 'error', path, message: `${field.label} must be a non-empty string.`});
      }
    } else if (field.kind === 'vector3') {
      if (!Array.isArray(fieldValue) || fieldValue.length !== 3) {
        issues.push({severity: 'error', path, message: `${field.label} must contain exactly three values.`});
      } else fieldValue.forEach((item, index) => {
        if (numberProblem(item, false)) issues.push({severity: 'error', path: `${path}[${index}]`, message: `${field.label} values must be finite numbers.`});
      });
    } else {
      const integerOnly = field.kind === 'integer-array';
      if (!Array.isArray(fieldValue)) {
        issues.push({severity: 'error', path, message: `${field.label} must be an array.`});
      } else {
        if (field.exactItems !== undefined && fieldValue.length !== field.exactItems) {
          issues.push({severity: 'error', path, message: `${field.label} must contain exactly ${field.exactItems} value(s).`});
        } else if ((field.minItems ?? 0) > fieldValue.length) issues.push({severity: 'error', path, message: `${field.label} must contain at least ${field.minItems} value(s).`});
        fieldValue.forEach((item, index) => {
          if (numberProblem(item, integerOnly)) issues.push({severity: 'error', path: `${path}[${index}]`, message: `${field.label} contains an invalid value.`});
        });
      }
    }
    if (field.key === 'TIME_ID' && Number.isInteger(fieldValue) && fieldValue !== 0
      && references.timeIds.length > 0 && !references.timeIds.includes(fieldValue as number)) {
      issues.push({severity: 'warning', path, message: `Time ID ${String(fieldValue)} was not found in 18_Time_Function.`});
    }
  }
}

export function validateFieldSourceEntry(value: unknown, rootValue?: unknown): FieldSourceValidationIssue[] {
  const issues: FieldSourceValidationIssue[] = [];
  const inspected = inspectFieldSourceEntry(value);
  if (inspected.kind === 'raw') {
    if (inspected.reason === 'unknown') issues.push({severity: 'warning', path: '$', message: 'Unsupported Field Source definition is preserved as raw JSON.'});
    else issues.push({severity: 'error', path: '$', message: inspected.reason === 'multiple'
      ? 'A Field Source array entry must not contain multiple supported definitions.'
      : 'Field Source entry must be a JSON object.'});
    return issues;
  }
  const {type, definition} = inspected;
  if (!isPlainRecord(definition)) {
    issues.push({severity: 'error', path: type, message: `${type} must be an object.`});
    return issues;
  }
  if (type === 'NETWORK') return validateNetwork(definition, rootValue).map((issue) => ({...issue, path: `${type}.${issue.path}`}));
  if (type === 'CIRCUIT') return validateCircuit(definition, rootValue).map((issue) => ({...issue, path: `${type}.${issue.path}`}));
  const references = collectEmSolutionReferences(rootValue);
  const schema = FIELD_SOURCE_SCHEMAS[type];
  validateFields(definition, schema.fields, type, references, issues);
  if (schema.rowLabel) {
    if (!Array.isArray(definition.data)) {
      issues.push({severity: 'error', path: `${type}.data`, message: `${type} data must be an array.`});
    } else definition.data.forEach((row, index) => {
      const base = `${type}.data[${index}]`;
      if (!isPlainRecord(row)) {
        issues.push({severity: 'error', path: base, message: `${schema.rowLabel} must be an object.`});
        return;
      }
      const rowSchema = rowSchemaForSource(type, definition, row);
      if (!rowSchema) {
        issues.push({severity: 'warning', path: base, message: 'Unknown nested row is preserved as raw JSON.'});
        return;
      }
      validateFields(row, rowSchema.fields, base, references, issues);
      if (type === 'DCCURR' && Array.isArray(row.MAT_IDS) && Array.isArray(row.SIGMA) && row.MAT_IDS.length !== row.SIGMA.length) {
        issues.push({severity: 'error', path: `${base}.SIGMA`, message: 'SIGMA must contain one conductivity per MAT_IDS entry.'});
      }
    });
  }
  if (type === 'POTNODE' && Array.isArray(definition.NODE_IDS) && Array.isArray(definition.POTENTIALS)
    && definition.NODE_IDS.length !== definition.POTENTIALS.length) {
    issues.push({severity: 'error', path: `${type}.POTENTIALS`, message: 'POTENTIALS must contain one potential per NODE_IDS entry.'});
  }
  if (type === 'MAGNET' && definition.INPUT_TYPE === 2 && Array.isArray(definition.ORDERS)
    && Array.isArray(definition.AMPLITUDES) && definition.ORDERS.length !== definition.AMPLITUDES.length) {
    issues.push({severity: 'error', path: `${type}.AMPLITUDES`, message: 'AMPLITUDES must contain one value per harmonic order.'});
  }
  if (type === 'MAGNET' && definition.INPUT_TYPE === 2 && Number.isInteger(definition.NO_ORDERS)
    && Array.isArray(definition.ORDERS) && definition.NO_ORDERS !== definition.ORDERS.length) {
    issues.push({severity: 'error', path: `${type}.NO_ORDERS`, message: 'NO_ORDERS must match the ORDERS array length.'});
  }
  if (type === 'EPOTSUF' || type === 'POTNODE') {
    const analysis = isPlainRecord(rootValue) && isPlainRecord(rootValue['2_Analysis_Type']) ? rootValue['2_Analysis_Type'] : undefined;
    if (analysis && ![2, 3].includes(analysis.STATIC as number)) {
      issues.push({severity: 'warning', path: type, message: `${type} is documented for STATIC modes 2 and 3.`});
    }
  }
  return issues;
}

export function validateFieldSources(rootValue: unknown): FieldSourceValidationIssue[] {
  if (!isPlainRecord(rootValue)) return [{severity: 'error', path: '$', message: 'EMSolution input must be an object.'}];
  if (hasMalformedFieldSourceRoot(rootValue)) return [{severity: 'error', path: '17_Field_Source', message: '17_Field_Source must be an array.'}];
  const entries = Array.isArray(rootValue['17_Field_Source']) ? rootValue['17_Field_Source'] : [];
  return entries.flatMap((entry, sourceIndex) => validateFieldSourceEntry(entry, rootValue).map((issue) => ({...issue, sourceIndex})));
}

export function normalizeFieldSources(rootValue: unknown): unknown {
  const result = deepClone(rootValue);
  if (!isPlainRecord(result)) return result;
  if (!Array.isArray(result['17_Field_Source'])) result['17_Field_Source'] = [];
  result['17_Field_Source'] = (result['17_Field_Source'] as unknown[]).map((entry) => {
    const inspected = inspectFieldSourceEntry(entry);
    if (inspected.kind !== 'known' || !isPlainRecord(inspected.definition)) return entry;
    const wrapper = deepClone(inspected.wrapper);
    if (inspected.type === 'NETWORK') wrapper[inspected.key] = normalizeNetwork(inspected.definition);
    if (inspected.type === 'CIRCUIT') wrapper[inspected.key] = normalizeCircuit(inspected.definition);
    return wrapper;
  });
  return result;
}

export function fieldSourceSummary(value: unknown): string {
  const inspected = inspectFieldSourceEntry(value);
  if (inspected.kind === 'raw') return inspected.reason === 'unknown' ? 'Unsupported raw definition' : 'Malformed raw entry';
  if (!isPlainRecord(inspected.definition)) return 'Malformed definition';
  const definition = inspected.definition;
  if (inspected.type === 'NETWORK') return `${Array.isArray(definition.data) ? definition.data.length : 0} network component(s)`;
  if (inspected.type === 'CIRCUIT') return `${Array.isArray(definition.SERIES_IDS) ? definition.SERIES_IDS.length : 0} series · ${Array.isArray(definition.POWER_SUPPLIES) ? definition.POWER_SUPPLIES.length : 0} supplies`;
  if (inspected.type === 'POTNODE') return `${Array.isArray(definition.NODE_IDS) ? definition.NODE_IDS.length : 0} node(s)`;
  if (Array.isArray(definition.data)) return `${definition.data.length} ${FIELD_SOURCE_SCHEMAS[inspected.type].rowLabel?.toLowerCase() ?? 'row'}(s)`;
  return definition.SERIES_ID === undefined ? FIELD_SOURCE_SCHEMAS[inspected.type].label : `Series ${String(definition.SERIES_ID)}`;
}
