export type JsonRecord = Record<string, unknown>;

export interface EmSolutionReferences {
  seriesIds: number[];
  timeIds: number[];
}

export function isPlainRecord(value: unknown): value is JsonRecord {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

export function deepClone<T>(value: T): T {
  if (typeof structuredClone === 'function') return structuredClone(value);
  return JSON.parse(JSON.stringify(value)) as T;
}

export function isEmSolutionInput(value: unknown): boolean {
  if (!isPlainRecord(value)) return false;
  if (isPlainRecord(value.metaData) && value.metaData.type === 'EMSolution_Input') return true;
  const signature = ['0_Release_Number', '1_Execution_Control', '2_Analysis_Type'];
  return signature.filter((key) => Object.hasOwn(value, key)).length >= 2;
}

function sortedNumbers(values: Set<number>): number[] {
  return [...values].sort((left, right) => left - right);
}

export function collectEmSolutionReferences(value: unknown): EmSolutionReferences {
  const seriesIds = new Set<number>();
  const timeIds = new Set<number>();
  if (!isPlainRecord(value)) return {seriesIds: [], timeIds: []};
  const sources = value['17_Field_Source'];
  if (Array.isArray(sources)) {
    for (const source of sources) {
      if (!isPlainRecord(source)) continue;
      for (const [key, definition] of Object.entries(source)) {
        if (key === 'NETWORK' || key === 'CIRCUIT' || !isPlainRecord(definition)) continue;
        if (Number.isInteger(definition.SERIES_ID)) seriesIds.add(definition.SERIES_ID as number);
      }
    }
  }
  const functions = value['18_Time_Function'];
  const entries = Array.isArray(functions) ? functions : isPlainRecord(functions) ? [functions] : [];
  for (const entry of entries) {
    if (isPlainRecord(entry) && Number.isInteger(entry.TIME_ID)) timeIds.add(entry.TIME_ID as number);
  }
  return {seriesIds: sortedNumbers(seriesIds), timeIds: sortedNumbers(timeIds)};
}
