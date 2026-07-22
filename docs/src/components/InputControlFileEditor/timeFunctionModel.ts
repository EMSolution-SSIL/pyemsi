import {deepClone, isPlainRecord, type JsonRecord} from './emSolutionModel';

export {deepClone, isPlainRecord};

export const TIME_FUNCTION_DOCUMENTATION = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/18_Time_Function.html';
export const TIME_FUNCTION_EXPRESSION_DOCUMENTATION = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/Appendix_1_Equation_Format.html';

export const SUPPORTED_TIME_FUNCTION_OPTIONS = [0, 1, 2, 4, 11] as const;
export type SupportedTimeFunctionOption = typeof SUPPORTED_TIME_FUNCTION_OPTIONS[number];
export type TimeFunctionFieldKind = 'integer' | 'number' | 'string';

export interface TimeFunctionFieldDefinition {
  key: string;
  label: string;
  kind: TimeFunctionFieldKind;
  help: string;
  unit?: string;
  multiline?: boolean;
}

export interface TimeFunctionSchema {
  option: SupportedTimeFunctionOption;
  label: string;
  description: string;
  fields: TimeFunctionFieldDefinition[];
  defaults: JsonRecord;
}

export interface TimeFunctionValidationIssue {
  severity: 'error' | 'warning';
  path: string;
  message: string;
  entryIndex?: number;
}

export interface GuidedTimeFunctionEntry {
  kind: 'guided';
  option: SupportedTimeFunctionOption;
  value: JsonRecord;
}

export interface RawTimeFunctionEntry {
  kind: 'raw';
  reason: 'malformed' | 'missing-option' | 'unsupported';
  option?: number;
  value: unknown;
}

export type InspectedTimeFunctionEntry = GuidedTimeFunctionEntry | RawTimeFunctionEntry;

export interface TimeFunctionConsumer {
  timeId: number;
  path: string;
  label: string;
}

export interface TimeFunctionPreviewPoint {
  time: number;
  value: number;
}

export interface TimeFunctionPreview {
  points: TimeFunctionPreviewPoint[];
  duration: number;
  error?: string;
}

export type TimeFunctionReferenceCatalogState = 'missing' | 'empty' | 'malformed' | 'ready';

export interface TimeFunctionReferenceChoice {
  key: string;
  entryIndex: number;
  timeId: number | null;
  option: number | null;
  optionLabel: string;
  summary: string;
  formattedJson: string;
  validationStatus: 'valid' | 'warning' | 'error';
  issues: TimeFunctionValidationIssue[];
  duplicate: boolean;
  selectable: boolean;
}

export interface TimeFunctionReferenceCatalog {
  state: TimeFunctionReferenceCatalogState;
  choices: TimeFunctionReferenceChoice[];
}

const numberField = (key: string, label: string, help: string, unit?: string): TimeFunctionFieldDefinition => ({
  key, label, kind: 'number', help, unit,
});

const integerField = (key: string, label: string, help: string): TimeFunctionFieldDefinition => ({
  key, label, kind: 'integer', help,
});

export const TIME_FUNCTION_SCHEMAS: Record<SupportedTimeFunctionOption, TimeFunctionSchema> = {
  0: {
    option: 0,
    label: 'Analytic expression',
    description: 'A polynomial, exponential, and sinusoidal time function using documented coefficients.',
    fields: [
      ...Array.from({length: 7}, (_, index) => numberField(`C${index}`, `Coefficient C${index}`, `Coefficient C${index} in the analytic time-function expression.`)),
      numberField('TEXP', 'Exponential time constant', 'Time constant used by the exponential terms; zero is accepted by EMSolution.', 's'),
      numberField('TCYCLE', 'Cycle period', 'Period used by the sinusoidal terms; zero is accepted by EMSolution.', 's'),
      numberField('PHASE4', 'C4 phase', 'Phase offset applied to the C4 cosine term.', 'deg'),
    ],
    defaults: {C0: 0, C1: 0, C2: 0, C3: 0, C4: 0, C5: 0, C6: 0, TEXP: 1, TCYCLE: 1, PHASE4: 0},
  },
  1: {
    option: 1,
    label: 'Time table',
    description: 'Paired time and value points, optionally repeated with a fixed cycle.',
    fields: [numberField('CYCLE', 'Repeat cycle', 'Zero disables repetition; a positive value is the repeated period.', 's')],
    defaults: {CYCLE: 0, TIME: [0, 1], VALUE: [0, 0]},
  },
  2: {
    option: 2,
    label: 'AC waveform',
    description: 'A cosine waveform defined by amplitude, period, and phase.',
    fields: [
      numberField('AMPLITUDE', 'Amplitude', 'Peak amplitude of the cosine waveform.'),
      numberField('TCYCLE', 'Cycle period', 'Period of the cosine waveform; zero is accepted by EMSolution.', 's'),
      numberField('PHASE', 'Phase', 'Cosine phase offset.', 'deg'),
    ],
    defaults: {AMPLITUDE: 1, TCYCLE: 1, PHASE: 0},
  },
  4: {
    option: 4,
    label: 'PSIM / MATLAB coupling',
    description: 'Input and output channel identifiers for a coupled external simulation.',
    fields: [
      integerField('PSIM_IN', 'Input channel', 'Voltage input channel from PSIM or MATLAB/Simulink; zero means not configured.'),
      integerField('PSIM_OUT', 'Output channel', 'Current output channel to PSIM or MATLAB/Simulink.'),
    ],
    defaults: {PSIM_IN: 0, PSIM_OUT: 0},
  },
  11: {
    option: 11,
    label: 'Formula input',
    description: 'A time function written in EMSolution mathematical-expression syntax.',
    fields: [{
      key: 'FUNCTION', label: 'Function', kind: 'string', multiline: true,
      help: 'Define f(t) using EMSolution expression syntax. Time T is measured in seconds.',
    }],
    defaults: {FUNCTION: '0'},
  },
};

const OPTION_FIELDS = new Set(Object.values(TIME_FUNCTION_SCHEMAS).flatMap((schema) => (
  [...schema.fields.map((field) => field.key), ...(schema.option === 1 ? ['TIME', 'VALUE'] : [])]
)));

export function isSupportedTimeFunctionOption(value: unknown): value is SupportedTimeFunctionOption {
  return typeof value === 'number' && SUPPORTED_TIME_FUNCTION_OPTIONS.includes(value as SupportedTimeFunctionOption);
}

export function inspectTimeFunctionEntry(value: unknown): InspectedTimeFunctionEntry {
  if (!isPlainRecord(value)) return {kind: 'raw', reason: 'malformed', value};
  if (!Number.isInteger(value.OPTION)) return {kind: 'raw', reason: 'missing-option', value};
  const option = value.OPTION as number;
  if (!isSupportedTimeFunctionOption(option)) return {kind: 'raw', reason: 'unsupported', option, value};
  return {kind: 'guided', option, value};
}

export function findTimeFunctions(rootValue: unknown): unknown[] {
  if (!isPlainRecord(rootValue) || !Array.isArray(rootValue['18_Time_Function'])) return [];
  return rootValue['18_Time_Function'];
}

export function hasMalformedTimeFunctionRoot(rootValue: unknown): boolean {
  return isPlainRecord(rootValue)
    && Object.hasOwn(rootValue, '18_Time_Function')
    && !Array.isArray(rootValue['18_Time_Function']);
}

export function replaceTimeFunctions(rootValue: unknown, entries: unknown[]): unknown {
  if (!isPlainRecord(rootValue)) return rootValue;
  const next = deepClone(rootValue);
  next['18_Time_Function'] = deepClone(entries);
  return next;
}

export function nextTimeFunctionId(entries: unknown[]): number {
  const used = new Set(entries.flatMap((entry) => (
    isPlainRecord(entry) && Number.isInteger(entry.TIME_ID) && (entry.TIME_ID as number) > 0 ? [entry.TIME_ID as number] : []
  )));
  let candidate = 1;
  while (used.has(candidate)) candidate += 1;
  return candidate;
}

export function createTimeFunction(option: SupportedTimeFunctionOption, entries: unknown[] = []): JsonRecord {
  return {TIME_ID: nextTimeFunctionId(entries), OPTION: option, ...deepClone(TIME_FUNCTION_SCHEMAS[option].defaults)};
}

export function createRawTimeFunction(entries: unknown[] = []): JsonRecord {
  return {TIME_ID: nextTimeFunctionId(entries), OPTION: 3};
}

export function duplicateTimeFunction(entry: unknown, entries: unknown[]): unknown {
  const next = deepClone(entry);
  if (isPlainRecord(next)) next.TIME_ID = nextTimeFunctionId(entries);
  return next;
}

export function changeTimeFunctionOption(entry: JsonRecord, option: SupportedTimeFunctionOption): JsonRecord {
  const preserved: JsonRecord = {};
  for (const [key, value] of Object.entries(entry)) {
    if (key !== 'OPTION' && key !== 'TIME_ID' && !OPTION_FIELDS.has(key)) preserved[key] = deepClone(value);
  }
  return {
    TIME_ID: entry.TIME_ID,
    OPTION: option,
    ...deepClone(TIME_FUNCTION_SCHEMAS[option].defaults),
    ...preserved,
  };
}

export function timeFunctionSummary(value: unknown): string {
  const inspected = inspectTimeFunctionEntry(value);
  if (inspected.kind === 'raw') {
    if (inspected.reason === 'unsupported') return `Unsupported OPTION ${inspected.option}; edit as raw JSON`;
    if (inspected.reason === 'missing-option') return 'Missing or invalid OPTION; repair as raw JSON';
    return 'Malformed entry; repair as raw JSON';
  }
  const entry = inspected.value;
  if (inspected.option === 0) return `C0=${String(entry.C0 ?? '—')}, cycle=${String(entry.TCYCLE ?? '—')} s`;
  if (inspected.option === 1) return `${Array.isArray(entry.TIME) ? entry.TIME.length : 0} point(s), cycle=${String(entry.CYCLE ?? '—')} s`;
  if (inspected.option === 2) return `amplitude=${String(entry.AMPLITUDE ?? '—')}, cycle=${String(entry.TCYCLE ?? '—')} s`;
  if (inspected.option === 4) return `input ${String(entry.PSIM_IN ?? '—')} → output ${String(entry.PSIM_OUT ?? '—')}`;
  const formula = typeof entry.FUNCTION === 'string' ? entry.FUNCTION.trim() : '';
  return formula ? formula.slice(0, 80) : 'Formula not set';
}

function formattedTimeFunctionJson(value: unknown): string {
  const formatted = JSON.stringify(value, null, 2);
  return formatted === undefined ? String(value) : formatted;
}

/**
 * Builds a read-only catalog for TIME_ID reference controls. Catalog entries
 * intentionally retain invalid and duplicate rows so users can inspect the
 * document without the picker silently hiding damaged data.
 */
export function createTimeFunctionReferenceCatalog(rootValue: unknown): TimeFunctionReferenceCatalog {
  if (!isPlainRecord(rootValue) || !Object.hasOwn(rootValue, '18_Time_Function')) {
    return {state: 'missing', choices: []};
  }
  const collection = rootValue['18_Time_Function'];
  if (!Array.isArray(collection)) return {state: 'malformed', choices: []};
  if (collection.length === 0) return {state: 'empty', choices: []};

  const issues = validateTimeFunctions(rootValue);
  const idCounts = new Map<number, number>();
  collection.forEach((entry) => {
    if (isPlainRecord(entry) && Number.isInteger(entry.TIME_ID)) {
      const id = entry.TIME_ID as number;
      idCounts.set(id, (idCounts.get(id) ?? 0) + 1);
    }
  });

  const choices = collection.map((entry, entryIndex): TimeFunctionReferenceChoice => {
    const inspected = inspectTimeFunctionEntry(entry);
    const timeId = isPlainRecord(entry) && Number.isInteger(entry.TIME_ID) ? entry.TIME_ID as number : null;
    const option = isPlainRecord(entry) && Number.isInteger(entry.OPTION) ? entry.OPTION as number : null;
    const entryIssues = issues.filter((issue) => issue.entryIndex === entryIndex).map((issue) => ({...issue}));
    const duplicate = timeId !== null && (idCounts.get(timeId) ?? 0) > 1;
    const validationStatus = entryIssues.some((issue) => issue.severity === 'error') ? 'error'
      : entryIssues.some((issue) => issue.severity === 'warning') || duplicate ? 'warning' : 'valid';
    const optionLabel = inspected.kind === 'guided' ? TIME_FUNCTION_SCHEMAS[inspected.option].label
      : inspected.reason === 'unsupported' ? `Unsupported OPTION ${inspected.option}`
        : inspected.reason === 'missing-option' ? 'Missing or invalid OPTION' : 'Malformed entry';
    return {
      key: `time-function-${entryIndex}`,
      entryIndex,
      timeId,
      option,
      optionLabel,
      summary: timeFunctionSummary(entry),
      formattedJson: formattedTimeFunctionJson(entry),
      validationStatus,
      issues: entryIssues,
      duplicate,
      selectable: timeId !== null,
    };
  });
  return {state: 'ready', choices};
}

function finiteNumberProblem(value: unknown): string | undefined {
  return typeof value !== 'number' || !Number.isFinite(value) ? 'must be a finite number' : undefined;
}

function integerProblem(value: unknown): string | undefined {
  return !Number.isInteger(value) ? 'must be an integer' : undefined;
}

function validateEntry(value: unknown): TimeFunctionValidationIssue[] {
  const issues: TimeFunctionValidationIssue[] = [];
  const inspected = inspectTimeFunctionEntry(value);
  if (!isPlainRecord(value)) {
    return [{severity: 'error', path: '$', message: 'Time Function entry must be a JSON object.'}];
  }
  const timeIdProblem = integerProblem(value.TIME_ID);
  if (timeIdProblem) issues.push({severity: 'error', path: 'TIME_ID', message: `TIME_ID ${timeIdProblem}.`});
  if (inspected.kind === 'raw') {
    if (inspected.reason === 'missing-option') issues.push({severity: 'error', path: 'OPTION', message: 'OPTION must be an integer.'});
    else if (inspected.reason === 'unsupported') issues.push({severity: 'warning', path: 'OPTION', message: `OPTION ${inspected.option} is unsupported and is preserved as raw JSON.`});
    return issues;
  }

  const schema = TIME_FUNCTION_SCHEMAS[inspected.option];
  for (const field of schema.fields) {
    const problem = field.kind === 'integer' ? integerProblem(value[field.key])
      : field.kind === 'number' ? finiteNumberProblem(value[field.key])
        : typeof value[field.key] !== 'string' || !(value[field.key] as string).trim() ? 'must be a non-empty string' : undefined;
    if (problem) issues.push({severity: 'error', path: field.key, message: `${field.label} ${problem}.`});
  }

  if (inspected.option === 0) {
    if (typeof value.TEXP === 'number' && value.TEXP < 0) issues.push({severity: 'error', path: 'TEXP', message: 'TEXP must be zero or greater.'});
    if (typeof value.TCYCLE === 'number' && value.TCYCLE < 0) issues.push({severity: 'error', path: 'TCYCLE', message: 'TCYCLE must be zero or greater.'});
  }
  if (inspected.option === 1) {
    if (typeof value.CYCLE === 'number' && value.CYCLE < 0) issues.push({severity: 'error', path: 'CYCLE', message: 'CYCLE must be zero or greater.'});
    if (!Array.isArray(value.TIME)) issues.push({severity: 'error', path: 'TIME', message: 'TIME must be an array.'});
    if (!Array.isArray(value.VALUE)) issues.push({severity: 'error', path: 'VALUE', message: 'VALUE must be an array.'});
    if (Array.isArray(value.TIME) && Array.isArray(value.VALUE)) {
      if (value.TIME.length === 0) issues.push({severity: 'error', path: 'TIME', message: 'The time table must contain at least one point.'});
      if (value.TIME.length !== value.VALUE.length) issues.push({severity: 'error', path: 'TIME', message: 'TIME and VALUE must contain the same number of points.'});
      value.TIME.forEach((item, index) => {
        if (finiteNumberProblem(item)) issues.push({severity: 'error', path: `TIME[${index}]`, message: 'Time must be a finite number.'});
        if (index > 0 && typeof item === 'number' && typeof value.TIME[index - 1] === 'number' && item < (value.TIME[index - 1] as number)) {
          issues.push({severity: 'error', path: `TIME[${index}]`, message: 'Table times must be non-decreasing; equal consecutive times are allowed.'});
        }
      });
      value.VALUE.forEach((item, index) => {
        if (finiteNumberProblem(item)) issues.push({severity: 'error', path: `VALUE[${index}]`, message: 'Value must be a finite number.'});
      });
      if (typeof value.CYCLE === 'number' && value.CYCLE > 0 && value.TIME.length > 0) {
        if (value.TIME[0] !== 0) issues.push({severity: 'warning', path: 'TIME[0]', message: 'A cyclic table is documented from TIME=0 through TIME=CYCLE.'});
        if (value.TIME.at(-1) !== value.CYCLE) issues.push({severity: 'warning', path: `TIME[${value.TIME.length - 1}]`, message: 'The final time should equal CYCLE for a cyclic table.'});
      }
    }
  }
  if (inspected.option === 2 && typeof value.TCYCLE === 'number' && value.TCYCLE < 0) {
    issues.push({severity: 'error', path: 'TCYCLE', message: 'TCYCLE must be zero or greater.'});
  }
  return issues;
}

export function collectTimeFunctionConsumers(rootValue: unknown): TimeFunctionConsumer[] {
  if (!isPlainRecord(rootValue) || !Array.isArray(rootValue['17_Field_Source'])) return [];
  const consumers: TimeFunctionConsumer[] = [];
  const add = (value: unknown, path: string, label: string) => {
    if (Number.isInteger(value) && value !== 0) consumers.push({timeId: value as number, path, label});
  };
  rootValue['17_Field_Source'].forEach((source, sourceIndex) => {
    if (!isPlainRecord(source)) return;
    for (const [type, definition] of Object.entries(source)) {
      if (!isPlainRecord(definition)) continue;
      const base = `17_Field_Source[${sourceIndex}].${type}`;
      if (type === 'CIRCUIT' && Array.isArray(definition.POWER_SUPPLIES)) {
        definition.POWER_SUPPLIES.forEach((supply, index) => {
          if (isPlainRecord(supply)) add(supply.TIME_ID, `${base}.POWER_SUPPLIES[${index}].TIME_ID`, `CIRCUIT power supply ${index + 1}`);
        });
      } else if (type === 'NETWORK' && Array.isArray(definition.data)) {
        definition.data.forEach((component, index) => {
          if (isPlainRecord(component) && ['CPS', 'VPS', 'SWITCH', 'VR'].includes(String(component.type))) {
            add(component.TIME_ID, `${base}.data[${index}].TIME_ID`, `NETWORK ${String(component.type)} ${index + 1}`);
          }
        });
      } else {
        add(definition.TIME_ID, `${base}.TIME_ID`, `${type} source ${sourceIndex + 1}`);
      }
    }
  });
  return consumers;
}

export function validateTimeFunctions(rootValue: unknown): TimeFunctionValidationIssue[] {
  const entries = findTimeFunctions(rootValue);
  const issues: TimeFunctionValidationIssue[] = entries.flatMap((entry, entryIndex) => validateEntry(entry).map((issue) => ({...issue, entryIndex})));
  const seen = new Map<number, number>();
  entries.forEach((entry, entryIndex) => {
    if (!isPlainRecord(entry) || !Number.isInteger(entry.TIME_ID)) return;
    const id = entry.TIME_ID as number;
    const previous = seen.get(id);
    if (previous !== undefined) issues.push({
      severity: 'error', entryIndex, path: 'TIME_ID',
      message: `TIME_ID ${id} is already used by entry ${previous + 1}.`,
    });
    else seen.set(id, entryIndex);
  });
  const defined = new Set(seen.keys());
  for (const consumer of collectTimeFunctionConsumers(rootValue)) {
    if (!defined.has(consumer.timeId)) issues.push({
      severity: 'warning', path: consumer.path,
      message: `${consumer.label} references TIME_ID ${consumer.timeId}, which is not defined in 18_Time_Function.`,
    });
  }
  return issues;
}

export function timeFunctionUsage(entriesRoot: unknown, timeId: unknown): TimeFunctionConsumer[] {
  if (!Number.isInteger(timeId)) return [];
  return collectTimeFunctionConsumers(entriesRoot).filter((consumer) => consumer.timeId === timeId);
}

export function defaultPreviewDuration(value: unknown): number {
  const inspected = inspectTimeFunctionEntry(value);
  if (inspected.kind !== 'guided') return 1;
  const entry = inspected.value;
  if (inspected.option === 0) {
    const scales = [1];
    if (typeof entry.TCYCLE === 'number' && entry.TCYCLE > 0) scales.push(entry.TCYCLE);
    if (typeof entry.TEXP === 'number' && entry.TEXP > 0) scales.push(entry.TEXP * 5);
    return Math.max(...scales);
  }
  if (inspected.option === 1) {
    if (typeof entry.CYCLE === 'number' && entry.CYCLE > 0) return entry.CYCLE;
    const last = Array.isArray(entry.TIME) ? entry.TIME.at(-1) : undefined;
    return typeof last === 'number' && last > 0 ? last : 1;
  }
  if (inspected.option === 2 && typeof entry.TCYCLE === 'number' && entry.TCYCLE > 0) return entry.TCYCLE;
  return 1;
}

function analyticValue(entry: JsonRecord, time: number): number {
  const coefficients = Array.from({length: 7}, (_, index) => entry[`C${index}`] as number);
  const texp = entry.TEXP as number;
  const cycle = entry.TCYCLE as number;
  const phase = (entry.PHASE4 as number) * Math.PI / 180;
  const decay = Math.exp(-time / texp);
  const angle = 2 * Math.PI * time / cycle;
  return coefficients[0] + coefficients[1] * time + coefficients[2] * decay
    + coefficients[3] * Math.sin(angle) + coefficients[4] * Math.cos(angle + phase)
    + coefficients[5] * decay * Math.sin(angle) + coefficients[6] * decay * Math.cos(angle);
}

export function sampleTimeFunction(value: unknown, requestedDuration?: number, sampleCount = 160): TimeFunctionPreview {
  const inspected = inspectTimeFunctionEntry(value);
  const duration = requestedDuration ?? defaultPreviewDuration(value);
  if (inspected.kind !== 'guided' || ![0, 1, 2].includes(inspected.option)) return {points: [], duration, error: 'Preview is not available for this option.'};
  if (!Number.isFinite(duration) || duration <= 0) return {points: [], duration, error: 'Preview duration must be greater than zero.'};
  const entryIssues = validateEntry(value).filter((issue) => issue.severity === 'error');
  if (entryIssues.length > 0) return {points: [], duration, error: 'Complete the required fields to preview this function.'};
  if (inspected.option === 1) {
    const times = inspected.value.TIME as number[];
    const values = inspected.value.VALUE as number[];
    return {points: times.map((time, index) => ({time, value: values[index]})), duration};
  }
  const count = Math.max(2, Math.min(400, Math.floor(sampleCount)));
  const points = Array.from({length: count}, (_, index) => {
    const time = duration * index / (count - 1);
    const pointValue = inspected.option === 0 ? analyticValue(inspected.value, time)
      : (inspected.value.AMPLITUDE as number) * Math.cos(2 * Math.PI * time / (inspected.value.TCYCLE as number) + (inspected.value.PHASE as number) * Math.PI / 180);
    return {time, value: pointValue};
  });
  if (points.some((point) => !Number.isFinite(point.value))) return {points: [], duration, error: 'The current values do not produce a finite preview.'};
  return {points, duration};
}
