import {
  collectEmSolutionReferences,
  deepClone,
  isEmSolutionInput,
  isPlainRecord,
  type JsonRecord,
} from './emSolutionModel';

export {deepClone, isEmSolutionInput, isPlainRecord};

export const NETWORK_COMPONENT_TYPES = [
  'FEM', 'R', 'L', 'M', 'C', 'CPS', 'VPS', 'D1', 'D2', 'EQ',
  'TABLE', 'TAB', 'SETV', 'SETI', 'SWITCH', 'VR',
] as const;

export type NetworkComponentType = typeof NETWORK_COMPONENT_TYPES[number];

export interface NetworkComponent extends JsonRecord {
  type: string;
}

export interface NetworkDefinition extends JsonRecord {
  REGION_FACTOR?: unknown;
  REGION_PARALLEL?: unknown;
  data?: unknown;
}

export interface NetworkSection {
  sourceIndex: number;
  network: unknown;
}

export type NetworkReferences = ReturnType<typeof collectEmSolutionReferences>;

export type NetworkFieldKind = 'integer' | 'number' | 'series' | 'time' | 'inductor' | 'table' | 'element';

export interface NetworkFieldDefinition {
  key: string;
  label: string;
  kind: NetworkFieldKind;
  unit?: string;
  help: string;
}

export interface NetworkComponentSchema {
  type: NetworkComponentType;
  label: string;
  description: string;
  fields: NetworkFieldDefinition[];
}

export interface NetworkValidationIssue {
  severity: 'error' | 'warning';
  path: string;
  message: string;
}

const ID: NetworkFieldDefinition = {
  key: 'ID', label: 'Element ID', kind: 'integer', help: 'Unique circuit element identifier.',
};
const START: NetworkFieldDefinition = {
  key: 'START', label: 'Start node', kind: 'integer', help: 'Node where the positive current direction starts.',
};
const END: NetworkFieldDefinition = {
  key: 'END', label: 'End node', kind: 'integer', help: 'Node where the positive current direction ends.',
};

export const NETWORK_COMPONENT_SCHEMAS: Record<NetworkComponentType, NetworkComponentSchema> = {
  FEM: {
    type: 'FEM', label: 'FEM source',
    description: 'Connects a source series defined in the FEM region to the external network.',
    fields: [ID, START, END, {key: 'SERIES_ID', label: 'Series ID', kind: 'series', help: 'Source series identifier from another 17_Field_Source entry.'}],
  },
  R: {
    type: 'R', label: 'Resistor', description: 'A fixed external resistance.',
    fields: [ID, START, END, {key: 'RESISTANCE', label: 'Resistance', kind: 'number', unit: 'Ω', help: 'Resistance value.'}],
  },
  L: {
    type: 'L', label: 'Inductor', description: 'A fixed external inductance.',
    fields: [ID, START, END, {key: 'INDUCTANCE', label: 'Inductance', kind: 'number', unit: 'H', help: 'Inductance value.'}],
  },
  M: {
    type: 'M', label: 'Mutual inductance', description: 'Adds mutual inductance between two previously defined L elements.',
    fields: [ID,
      {key: 'L1', label: 'Inductor 1', kind: 'inductor', help: 'ID of the first previously defined L element.'},
      {key: 'L2', label: 'Inductor 2', kind: 'inductor', help: 'ID of the second previously defined L element.'},
      {key: 'INDUCTANCE', label: 'Mutual inductance', kind: 'number', unit: 'H', help: 'Mutual inductance value.'},
    ],
  },
  C: {
    type: 'C', label: 'Capacitor', description: 'A fixed external capacitance; initial runs normally require a following SETV.',
    fields: [ID, START, END, {key: 'CAPACITANCE', label: 'Capacitance', kind: 'number', unit: 'F', help: 'Capacitance value.'}],
  },
  CPS: {
    type: 'CPS', label: 'Current source', description: 'A current source driven by a time function.',
    fields: [ID, START, END, {key: 'TIME_ID', label: 'Time function', kind: 'time', unit: 'A', help: 'TIME_ID from 18_Time_Function that defines the current.'}],
  },
  VPS: {
    type: 'VPS', label: 'Voltage source', description: 'A voltage source driven by a time function; use SETI for a nonzero initial current.',
    fields: [ID, START, END, {key: 'TIME_ID', label: 'Time function', kind: 'time', unit: 'V', help: 'TIME_ID from 18_Time_Function that defines the voltage.'}],
  },
  D1: {
    type: 'D1', label: 'Diode, type 1', description: 'A piecewise-linear nonlinear element with separate forward and reverse resistance.',
    fields: [ID, START, END,
      {key: 'R1', label: 'Forward resistance', kind: 'number', unit: 'Ω', help: 'Resistance used for forward current.'},
      {key: 'R2', label: 'Reverse resistance', kind: 'number', unit: 'Ω', help: 'Resistance used for reverse current.'},
    ],
  },
  D2: {
    type: 'D2', label: 'Diode, type 2', description: 'A logarithmic nonlinear element parameterized by a voltage and current.',
    fields: [ID, START, END,
      {key: 'V0', label: 'Reference voltage', kind: 'number', unit: 'V', help: 'V0 in the documented logarithmic voltage-drop equation.'},
      {key: 'I0', label: 'Reference current', kind: 'number', unit: 'A', help: 'I0 in the documented logarithmic voltage-drop equation.'},
    ],
  },
  EQ: {
    type: 'EQ', label: 'Equation element', description: 'A nonlinear element whose forward voltage function V(I) is supplied by the EMSolution equation input mechanism.',
    fields: [ID, START, END],
  },
  TABLE: {
    type: 'TABLE', label: 'I–V table definition', description: 'One or more current/voltage datasets used by TAB elements.', fields: [],
  },
  TAB: {
    type: 'TAB', label: 'Table element', description: 'A nonlinear element using an I–V TABLE definition.',
    fields: [ID, START, END, {key: 'TABLE_ID', label: 'Table ID', kind: 'table', help: 'ID of a previously defined TABLE dataset.'}],
  },
  SETV: {
    type: 'SETV', label: 'Initial voltage', description: 'Sets the initial voltage of a previously defined element, normally a capacitor.',
    fields: [
      {key: 'ID', label: 'Target element ID', kind: 'element', help: 'ID of the previously defined capacitor that receives the initial voltage.'},
      {key: 'INITIAL_VOLTAGE', label: 'Initial voltage', kind: 'number', unit: 'V', help: 'Initial applied voltage.'},
    ],
  },
  SETI: {
    type: 'SETI', label: 'Initial current', description: 'Sets the initial current of a previously defined voltage-source element.',
    fields: [
      {key: 'ID', label: 'Target element ID', kind: 'element', help: 'ID of the previously defined voltage source that receives the initial current.'},
      {key: 'INITIAL_CURRENT', label: 'Initial current', kind: 'number', unit: 'A', help: 'Initial voltage-source current.'},
    ],
  },
  SWITCH: {
    type: 'SWITCH', label: 'Switch', description: 'A timed switch with separate closed/open resistance and paired on/off intervals.',
    fields: [ID, START, END,
      {key: 'ON_RES', label: 'On resistance', kind: 'number', unit: 'Ω', help: 'Resistance while the switch is closed.'},
      {key: 'OFF_RES', label: 'Off resistance', kind: 'number', unit: 'Ω', help: 'Resistance while the switch is open.'},
      {key: 'CYCLE', label: 'Cycle', kind: 'number', unit: 's', help: 'Switch period; zero means non-periodic.'},
      {key: 'PHASE_OP', label: 'Time mode', kind: 'integer', help: '0 uses seconds; 1 uses phase angle in degrees.'},
      {key: 'TIME_ID', label: 'Time function', kind: 'time', help: 'Optional time-function identifier used by the switch.'},
    ],
  },
  VR: {
    type: 'VR', label: 'Variable resistor', description: 'A time-dependent variable resistance.',
    fields: [ID, START, END, {key: 'TIME_ID', label: 'Time function', kind: 'time', help: 'TIME_ID from 18_Time_Function that defines resistance over time.'}],
  },
};

const CIRCUIT_ELEMENT_TYPES = new Set<NetworkComponentType>([
  'FEM', 'R', 'L', 'M', 'C', 'CPS', 'VPS', 'D1', 'D2', 'EQ', 'TAB', 'SWITCH', 'VR',
]);

export function isNetworkDefinition(value: unknown): value is NetworkDefinition {
  return isPlainRecord(value);
}

export function isKnownNetworkType(value: string): value is NetworkComponentType {
  return (NETWORK_COMPONENT_TYPES as readonly string[]).includes(value);
}

export function findNetworkSections(value: unknown): NetworkSection[] {
  if (!isEmSolutionInput(value) || !isPlainRecord(value)) return [];
  const sources = value['17_Field_Source'];
  if (!Array.isArray(sources)) return [];
  return sources.flatMap((source, sourceIndex) => (
    isPlainRecord(source) && Object.hasOwn(source, 'NETWORK')
      ? [{sourceIndex, network: source.NETWORK}]
      : []
  ));
}

export function replaceNetworkSections(value: unknown, sections: NetworkSection[]): unknown {
  const result = deepClone(value);
  if (!isPlainRecord(result) || !Array.isArray(result['17_Field_Source'])) return result;
  const sources = result['17_Field_Source'];
  for (const section of sections) {
    const source = sources[section.sourceIndex];
    if (isPlainRecord(source)) source.NETWORK = deepClone(section.network);
  }
  return result;
}

export function collectNetworkReferences(value: unknown): NetworkReferences {
  return collectEmSolutionReferences(value);
}

export function networkComponents(network: NetworkDefinition): NetworkComponent[] {
  if (!Array.isArray(network.data)) return [];
  return network.data.filter((item): item is NetworkComponent => isPlainRecord(item) && typeof item.type === 'string');
}

export function normalizeNetwork(network: NetworkDefinition): NetworkDefinition {
  const result = deepClone(network);
  if (!Array.isArray(result.data)) return result;
  result.data = result.data.map((item) => {
    if (!isPlainRecord(item) || typeof item.type !== 'string') return item;
    if (item.type === 'TABLE') {
      const tables = Array.isArray(item.data) ? item.data : [];
      item.NUMBER = tables.length;
      item.data = tables.map((table) => {
        if (!isPlainRecord(table)) return table;
        const current = Array.isArray(table.CURRENT) ? table.CURRENT : [];
        const voltage = Array.isArray(table.VOLTAGE) ? table.VOLTAGE : [];
        table.NO_DATA = Math.min(current.length, voltage.length);
        return table;
      });
    }
    return item;
  });
  return result;
}

export function nextElementId(components: unknown[]): number {
  const used = new Set<number>();
  for (const component of components) {
    if (isPlainRecord(component) && Number.isInteger(component.ID)) used.add(component.ID as number);
  }
  let candidate = 1;
  while (used.has(candidate)) candidate += 1;
  return candidate;
}

export function createNetworkComponent(type: NetworkComponentType, components: unknown[]): NetworkComponent {
  if (type === 'TABLE') return {type, NUMBER: 0, data: []};
  const result: NetworkComponent = {type};
  for (const field of NETWORK_COMPONENT_SCHEMAS[type].fields) {
    result[field.key] = field.key === 'ID' && !['SETV', 'SETI'].includes(type) ? nextElementId(components) : '';
  }
  if (type === 'SWITCH') {
    result.ON_TIME = [];
    result.OFF_TIME = [];
  }
  return result;
}

function numberIssue(value: unknown, integer: boolean): string | undefined {
  if (typeof value !== 'number' || !Number.isFinite(value)) return integer ? 'must be an integer' : 'must be a finite number';
  if (integer && !Number.isInteger(value)) return 'must be an integer';
  return undefined;
}

function componentAt(data: unknown[], index: number): NetworkComponent | undefined {
  const item = data[index];
  return isPlainRecord(item) && typeof item.type === 'string' ? item as NetworkComponent : undefined;
}

export function validateNetwork(networkValue: unknown, rootValue?: unknown): NetworkValidationIssue[] {
  const issues: NetworkValidationIssue[] = [];
  const error = (path: string, message: string) => issues.push({severity: 'error', path, message});
  const warning = (path: string, message: string) => issues.push({severity: 'warning', path, message});
  if (!isPlainRecord(networkValue)) {
    error('$', 'NETWORK must be an object.');
    return issues;
  }
  for (const key of ['REGION_FACTOR', 'REGION_PARALLEL']) {
    const problem = numberIssue(networkValue[key], false);
    if (problem) error(key, `${key} ${problem}.`);
  }
  if (!Array.isArray(networkValue.data)) {
    error('data', 'NETWORK data must be an array.');
    return issues;
  }

  const data = networkValue.data;
  const seenIds = new Map<number, number>();
  const earlierInductors = new Set<number>();
  const earlierElements = new Map<number, string>();
  const earlierTables = new Set<number>();
  const references = collectNetworkReferences(rootValue);

  for (let index = 0; index < data.length; index += 1) {
    const base = `data[${index}]`;
    const component = componentAt(data, index);
    if (!component) {
      error(base, 'Component must be an object with a string type.');
      continue;
    }
    const type = component.type;
    if (!isKnownNetworkType(type)) {
      warning(`${base}.type`, `Unknown component type ${type}; it will be preserved as raw JSON.`);
      continue;
    }
    const schema = NETWORK_COMPONENT_SCHEMAS[type];
    for (const field of schema.fields) {
      const problem = numberIssue(component[field.key], field.kind !== 'number');
      if (problem) error(`${base}.${field.key}`, `${field.label} ${problem}.`);
    }

    if (CIRCUIT_ELEMENT_TYPES.has(type) && Number.isInteger(component.ID)) {
      const id = component.ID as number;
      const previous = seenIds.get(id);
      if (previous !== undefined) error(`${base}.ID`, `Element ID ${id} is already used by row ${previous + 1}.`);
      else seenIds.set(id, index);
      earlierElements.set(id, type);
      if (type === 'L') earlierInductors.add(id);
    }

    if (type === 'FEM' && Number.isInteger(component.SERIES_ID) && references.seriesIds.length > 0
      && !references.seriesIds.includes(component.SERIES_ID as number)) {
      warning(`${base}.SERIES_ID`, `Series ID ${String(component.SERIES_ID)} was not found in 17_Field_Source.`);
    }
    if (['CPS', 'VPS', 'SWITCH', 'VR'].includes(type) && Number.isInteger(component.TIME_ID)
      && references.timeIds.length > 0 && !references.timeIds.includes(component.TIME_ID as number)) {
      warning(`${base}.TIME_ID`, `Time ID ${String(component.TIME_ID)} was not found in 18_Time_Function.`);
    }
    if (type === 'M') {
      for (const key of ['L1', 'L2']) {
        if (Number.isInteger(component[key]) && !earlierInductors.has(component[key] as number)) {
          warning(`${base}.${key}`, `${key} should reference an L element defined before this row.`);
        }
      }
    }
    if (type === 'TABLE') {
      if (!Array.isArray(component.data)) {
        error(`${base}.data`, 'TABLE data must be an array.');
      } else {
        if (component.NUMBER !== component.data.length) error(`${base}.NUMBER`, 'NUMBER must match the number of table datasets.');
        component.data.forEach((table, tableIndex) => {
          const tableBase = `${base}.data[${tableIndex}]`;
          if (!isPlainRecord(table)) {
            error(tableBase, 'Table dataset must be an object.');
            return;
          }
          const idProblem = numberIssue(table.ID, true);
          if (idProblem) error(`${tableBase}.ID`, `Table ID ${idProblem}.`);
          else if (earlierTables.has(table.ID as number)) error(`${tableBase}.ID`, `Table ID ${String(table.ID)} is duplicated.`);
          else earlierTables.add(table.ID as number);
          if (!Array.isArray(table.CURRENT) || !Array.isArray(table.VOLTAGE)) {
            error(tableBase, 'CURRENT and VOLTAGE must be arrays.');
            return;
          }
          if (table.CURRENT.length !== table.VOLTAGE.length) error(tableBase, 'CURRENT and VOLTAGE must contain the same number of values.');
          if (table.NO_DATA !== table.CURRENT.length) error(`${tableBase}.NO_DATA`, 'NO_DATA must match the number of current/voltage points.');
          table.CURRENT.forEach((entry, pointIndex) => {
            if (numberIssue(entry, false)) error(`${tableBase}.CURRENT[${pointIndex}]`, 'Current must be a finite number.');
          });
          table.VOLTAGE.forEach((entry, pointIndex) => {
            if (numberIssue(entry, false)) error(`${tableBase}.VOLTAGE[${pointIndex}]`, 'Voltage must be a finite number.');
          });
        });
      }
    }
    if (type === 'TAB' && Number.isInteger(component.TABLE_ID) && !earlierTables.has(component.TABLE_ID as number)) {
      warning(`${base}.TABLE_ID`, 'TABLE_ID should reference a TABLE dataset defined before this row.');
    }
    if (type === 'SETV' && Number.isInteger(component.ID) && earlierElements.get(component.ID as number) !== 'C') {
      warning(`${base}.ID`, 'SETV should follow and reference its capacitor element.');
    }
    if (type === 'SETI' && Number.isInteger(component.ID) && earlierElements.get(component.ID as number) !== 'VPS') {
      warning(`${base}.ID`, 'SETI should follow and reference its voltage-source element.');
    }
    if (type === 'SWITCH') {
      if (!Array.isArray(component.ON_TIME) || !Array.isArray(component.OFF_TIME)) {
        error(base, 'ON_TIME and OFF_TIME must be arrays.');
      } else {
        if (component.ON_TIME.length !== component.OFF_TIME.length) error(base, 'ON_TIME and OFF_TIME must contain the same number of entries.');
        [...component.ON_TIME, ...component.OFF_TIME].forEach((entry, timingIndex) => {
          if (numberIssue(entry, false)) error(`${base}.timing[${timingIndex}]`, 'Switch timing must be a finite number.');
        });
      }
      if (![0, 1].includes(component.PHASE_OP as number)) warning(`${base}.PHASE_OP`, 'PHASE_OP is normally 0 (seconds) or 1 (degrees).');
    }
  }

  if (isPlainRecord(rootValue) && isPlainRecord(rootValue['2_Analysis_Type'])) {
    const analysis = rootValue['2_Analysis_Type'];
    for (let index = 0; index < data.length; index += 1) {
      const component = componentAt(data, index);
      if (!component) continue;
      if (analysis.AC === 1 && ['D1', 'D2', 'EQ', 'TAB'].includes(component.type)) {
        warning(`data[${index}].type`, `${component.type} is not available for AC steady-state analysis.`);
      }
      if (analysis.STATIC === 1 && ['L', 'M', 'C'].includes(component.type)) {
        warning(`data[${index}].type`, `${component.type} is not available for static analysis.`);
      }
    }
  }
  return issues;
}

export function componentSummary(component: NetworkComponent): string {
  if (component.type === 'M') return `L${String(component.L1 ?? '?')} ↔ L${String(component.L2 ?? '?')}`;
  if (component.type === 'TABLE') return `${Array.isArray(component.data) ? component.data.length : 0} dataset(s)`;
  if (component.type === 'SETV') return `${String(component.INITIAL_VOLTAGE ?? '?')} V`;
  if (component.type === 'SETI') return `${String(component.INITIAL_CURRENT ?? '?')} A`;
  const connection = component.START !== undefined || component.END !== undefined
    ? `${String(component.START ?? '?')} → ${String(component.END ?? '?')}`
    : '';
  const schema = isKnownNetworkType(component.type) ? NETWORK_COMPONENT_SCHEMAS[component.type] : undefined;
  const parameters = schema?.fields
    .filter((field) => !['ID', 'START', 'END'].includes(field.key))
    .map((field) => `${field.key}=${String(component[field.key] ?? '?')}${field.unit ? ` ${field.unit}` : ''}`)
    .join(', ');
  return [connection, parameters].filter(Boolean).join(' · ') || 'Raw component';
}
