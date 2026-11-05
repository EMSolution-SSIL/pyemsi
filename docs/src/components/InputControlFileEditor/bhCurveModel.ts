import {deepClone, isPlainRecord, type JsonRecord} from './emSolutionModel';

export {deepClone, isPlainRecord};

export const BH_CURVE_DOCUMENTATION = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/20_BH_Curve.html';

export interface BhCurveValidationIssue {
  severity: 'error' | 'warning';
  path: string;
  message: string;
  entryIndex?: number;
}

export interface GuidedBhCurveEntry {
  kind: 'guided';
  value: JsonRecord;
}

export interface RawBhCurveEntry {
  kind: 'raw';
  reason: 'encrypted' | 'malformed' | 'ambiguous' | 'unknown';
  value: unknown;
}

export type InspectedBhCurveEntry = GuidedBhCurveEntry | RawBhCurveEntry;

export interface BhCurveConsumer {
  curveId: number;
  path: string;
  label: string;
}

export interface BhCurvePreviewPoint {
  h: number;
  b: number;
}

export type BhCurveReferenceCatalogState = 'missing' | 'empty' | 'malformed' | 'ready';

export interface BhCurveReferenceChoice {
  key: string;
  entryIndex: number;
  curveId: number | null;
  typeLabel: string;
  summary: string;
  formattedJson: string;
  validationStatus: 'valid' | 'warning' | 'error';
  issues: BhCurveValidationIssue[];
  duplicate: boolean;
  selectable: boolean;
}

export interface BhCurveReferenceCatalog {
  state: BhCurveReferenceCatalogState;
  choices: BhCurveReferenceChoice[];
}

export function inspectBhCurveEntry(value: unknown): InspectedBhCurveEntry {
  if (!isPlainRecord(value)) return {kind: 'raw', reason: 'malformed', value};
  const hasData = Object.hasOwn(value, 'data');
  const hasEncryptedData = Object.hasOwn(value, 'encrypted_data');
  if (hasData && hasEncryptedData) return {kind: 'raw', reason: 'ambiguous', value};
  if (hasEncryptedData) return {kind: 'raw', reason: 'encrypted', value};
  if (hasData && isPlainRecord(value.data) && Array.isArray(value.data.H) && Array.isArray(value.data.B)) {
    return {kind: 'guided', value};
  }
  return {kind: 'raw', reason: 'unknown', value};
}

export function findBhCurves(rootValue: unknown): unknown[] {
  if (!isPlainRecord(rootValue) || !Array.isArray(rootValue['20_BH_Curve'])) return [];
  return rootValue['20_BH_Curve'];
}

export function hasMalformedBhCurveRoot(rootValue: unknown): boolean {
  return isPlainRecord(rootValue)
    && Object.hasOwn(rootValue, '20_BH_Curve')
    && !Array.isArray(rootValue['20_BH_Curve']);
}

export function replaceBhCurves(rootValue: unknown, entries: unknown[]): unknown {
  if (!isPlainRecord(rootValue)) return rootValue;
  const next = deepClone(rootValue);
  next['20_BH_Curve'] = deepClone(entries);
  return next;
}

export function nextBhCurveId(entries: unknown[]): number {
  const used = new Set(entries.flatMap((entry) => (
    isPlainRecord(entry) && Number.isInteger(entry.BH_CURVE_ID) && (entry.BH_CURVE_ID as number) > 0
      ? [entry.BH_CURVE_ID as number] : []
  )));
  let candidate = 1;
  while (used.has(candidate)) candidate += 1;
  return candidate;
}

export function createBhCurve(entries: unknown[] = []): JsonRecord {
  return {BH_CURVE_ID: nextBhCurveId(entries), data: {H: [0, 1], B: [0, 0]}};
}

export function createEncryptedBhCurve(entries: unknown[] = []): JsonRecord {
  return {BH_CURVE_ID: nextBhCurveId(entries), encrypted_data: ''};
}

export function duplicateBhCurve(entry: unknown, entries: unknown[]): unknown {
  const next = deepClone(entry);
  if (isPlainRecord(next)) next.BH_CURVE_ID = nextBhCurveId(entries);
  return next;
}

export function bhCurveSummary(value: unknown): string {
  const inspected = inspectBhCurveEntry(value);
  if (inspected.kind === 'raw') {
    if (inspected.reason === 'encrypted') return 'Encrypted curve; edit as raw JSON';
    if (inspected.reason === 'ambiguous') return 'Contains both table and encrypted data; repair as raw JSON';
    if (inspected.reason === 'unknown') return 'Unsupported curve shape; repair as raw JSON';
    return 'Malformed entry; repair as raw JSON';
  }
  const data = inspected.value.data as JsonRecord;
  const h = data.H as unknown[];
  const b = data.B as unknown[];
  if (h.length === 0) return 'No H/B points';
  return `${Math.max(h.length, b.length)} point(s), H ${String(h[0] ?? '—')} to ${String(h.at(-1) ?? '—')} A/m`;
}

function formattedBhCurveJson(value: unknown): string {
  const formatted = JSON.stringify(value, null, 2);
  return formatted === undefined ? String(value) : formatted;
}

export function createBhCurveReferenceCatalog(rootValue: unknown): BhCurveReferenceCatalog {
  if (!isPlainRecord(rootValue) || !Object.hasOwn(rootValue, '20_BH_Curve')) {
    return {state: 'missing', choices: []};
  }
  const collection = rootValue['20_BH_Curve'];
  if (!Array.isArray(collection)) return {state: 'malformed', choices: []};
  if (collection.length === 0) return {state: 'empty', choices: []};

  const issues = validateBhCurves(rootValue);
  const idCounts = new Map<number, number>();
  collection.forEach((entry) => {
    if (isPlainRecord(entry) && Number.isInteger(entry.BH_CURVE_ID) && (entry.BH_CURVE_ID as number) > 0) {
      const id = entry.BH_CURVE_ID as number;
      idCounts.set(id, (idCounts.get(id) ?? 0) + 1);
    }
  });

  const choices = collection.map((entry, entryIndex): BhCurveReferenceChoice => {
    const inspected = inspectBhCurveEntry(entry);
    const curveId = isPlainRecord(entry) && Number.isInteger(entry.BH_CURVE_ID) && (entry.BH_CURVE_ID as number) > 0
      ? entry.BH_CURVE_ID as number : null;
    const entryIssues = issues.filter((issue) => issue.entryIndex === entryIndex).map((issue) => ({...issue}));
    const duplicate = curveId !== null && (idCounts.get(curveId) ?? 0) > 1;
    const validationStatus = entryIssues.some((issue) => issue.severity === 'error') ? 'error'
      : entryIssues.some((issue) => issue.severity === 'warning') || duplicate ? 'warning' : 'valid';
    const typeLabel = inspected.kind === 'guided' ? 'H/B table'
      : inspected.reason === 'encrypted' ? 'Encrypted / raw JSON'
        : inspected.reason === 'ambiguous' ? 'Ambiguous raw JSON'
          : inspected.reason === 'unknown' ? 'Unsupported raw JSON' : 'Malformed raw JSON';
    return {
      key: `bh-curve-${entryIndex}`,
      entryIndex,
      curveId,
      typeLabel,
      summary: bhCurveSummary(entry),
      formattedJson: formattedBhCurveJson(entry),
      validationStatus,
      issues: entryIssues,
      duplicate,
      selectable: curveId !== null,
    };
  });
  return {state: 'ready', choices};
}

function addConsumer(consumers: BhCurveConsumer[], value: unknown, path: string, label: string): void {
  if (Number.isInteger(value) && (value as number) > 0) {
    consumers.push({curveId: value as number, path, label});
  }
}

export function collectBhCurveConsumers(rootValue: unknown): BhCurveConsumer[] {
  if (!isPlainRecord(rootValue)) return [];
  const consumers: BhCurveConsumer[] = [];
  const materials = rootValue['16_Material_Properties'];
  if (isPlainRecord(materials)) {
    const volumes = materials['16_1_3D_Element_Properties'];
    if (Array.isArray(volumes)) volumes.forEach((entry, index) => {
      if (!isPlainRecord(entry) || !isPlainRecord(entry.MagneticProperty)) return;
      const magnetic = entry.MagneticProperty;
      const base = `16_Material_Properties.16_1_3D_Element_Properties[${index}].MagneticProperty`;
      addConsumer(consumers, magnetic.BH_CURVE_ID, `${base}.BH_CURVE_ID`, `Volume material ${index + 1}`);
      if (isPlainRecord(magnetic.BH_CURVE_XYZ) && Array.isArray(magnetic.BH_CURVE_XYZ.BH_XYZ_ID)) {
        magnetic.BH_CURVE_XYZ.BH_XYZ_ID.forEach((value, curveIndex) => {
          addConsumer(consumers, value, `${base}.BH_CURVE_XYZ.BH_XYZ_ID[${curveIndex}]`, `Volume material ${index + 1} axis ${curveIndex + 1}`);
        });
      }
      if (isPlainRecord(magnetic.ANISOTROPY2D)) {
        addConsumer(consumers, magnetic.ANISOTROPY2D.BH_Z, `${base}.ANISOTROPY2D.BH_Z`, `Volume material ${index + 1} Z curve`);
      }
    });

    const surfaces = materials['16_2_2D_Element_Properties'];
    if (Array.isArray(surfaces)) surfaces.forEach((entry, index) => {
      if (!isPlainRecord(entry) || !isPlainRecord(entry.SURFACE_IMPEDANCE)) return;
      const impedance = entry.SURFACE_IMPEDANCE;
      const key = Object.hasOwn(impedance, 'Nonlinear_Parameters') ? 'Nonlinear_Parameters'
        : Object.hasOwn(impedance, 'Nonliear_Parameters') ? 'Nonliear_Parameters' : undefined;
      if (!key || !isPlainRecord(impedance[key])) return;
      addConsumer(
        consumers,
        impedance[key].BH_CURVE_ID,
        `16_Material_Properties.16_2_2D_Element_Properties[${index}].SURFACE_IMPEDANCE.${key}.BH_CURVE_ID`,
        `Surface material ${index + 1}`,
      );
    });
  }

  const magnetizationCurves = rootValue['20_6_Magnetization_BH_Curve'];
  if (Array.isArray(magnetizationCurves)) magnetizationCurves.forEach((entry, index) => {
    if (isPlainRecord(entry)) addConsumer(
      consumers,
      entry.REF_BH_CURVE_ID,
      `20_6_Magnetization_BH_Curve[${index}].REF_BH_CURVE_ID`,
      `Magnetization curve ${index + 1}`,
    );
  });
  return consumers;
}

function finiteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function validateEntry(value: unknown): BhCurveValidationIssue[] {
  const issues: BhCurveValidationIssue[] = [];
  const inspected = inspectBhCurveEntry(value);
  if (!isPlainRecord(value)) {
    return [{severity: 'error', path: '$', message: 'B-H curve entry must be a JSON object.'}];
  }
  if (!Number.isInteger(value.BH_CURVE_ID) || (value.BH_CURVE_ID as number) <= 0) {
    issues.push({severity: 'error', path: 'BH_CURVE_ID', message: 'BH_CURVE_ID must be a positive integer.'});
  }
  if (inspected.kind === 'raw') {
    if (inspected.reason === 'encrypted') {
      if (typeof value.encrypted_data !== 'string' || value.encrypted_data.trim() === '') {
        issues.push({severity: 'error', path: 'encrypted_data', message: 'encrypted_data must be a non-empty string.'});
      } else {
        issues.push({severity: 'warning', path: 'encrypted_data', message: 'Encrypted curves are preserved and edited as raw JSON.'});
      }
    } else if (inspected.reason === 'ambiguous') {
      issues.push({severity: 'error', path: '$', message: 'Choose either data or encrypted_data; an entry cannot contain both.'});
    } else {
      issues.push({severity: 'error', path: '$', message: 'Curve must contain a paired data.H/data.B table or encrypted_data.'});
    }
    return issues;
  }

  const data = value.data as JsonRecord;
  const hValues = data.H as unknown[];
  const bValues = data.B as unknown[];
  if (hValues.length !== bValues.length) {
    issues.push({severity: 'error', path: 'data', message: 'H and B must contain the same number of points.'});
  }
  if (hValues.length < 2 || bValues.length < 2) {
    issues.push({severity: 'error', path: 'data', message: 'A B-H curve must contain at least two paired points.'});
  }
  hValues.forEach((item, index) => {
    if (!finiteNumber(item)) issues.push({severity: 'error', path: `data.H[${index}]`, message: 'H must be a finite number.'});
  });
  bValues.forEach((item, index) => {
    if (!finiteNumber(item)) issues.push({severity: 'error', path: `data.B[${index}]`, message: 'B must be a finite number.'});
  });
  if (hValues.length > 0 && bValues.length > 0 && (hValues[0] !== 0 || bValues[0] !== 0)) {
    issues.push({severity: 'warning', path: 'data[0]', message: 'The documented first point is H=0 and B=0.'});
  }
  const pairCount = Math.min(hValues.length, bValues.length);
  for (let index = 1; index < pairCount; index += 1) {
    const previousH = hValues[index - 1];
    const currentH = hValues[index];
    const previousB = bValues[index - 1];
    const currentB = bValues[index];
    if (!finiteNumber(previousH) || !finiteNumber(currentH) || !finiteNumber(previousB) || !finiteNumber(currentB)) continue;
    if (currentH <= previousH) {
      issues.push({severity: 'warning', path: `data.H[${index}]`, message: 'H values should increase strictly between consecutive points.'});
    } else if ((currentB - previousB) / (currentH - previousH) < 0) {
      issues.push({severity: 'warning', path: `data.B[${index}]`, message: 'The documented dB/dH slope should be nonnegative.'});
    }
  }
  return issues;
}

export function validateBhCurves(rootValue: unknown): BhCurveValidationIssue[] {
  const entries = findBhCurves(rootValue);
  const issues: BhCurveValidationIssue[] = entries.flatMap((entry, entryIndex) => (
    validateEntry(entry).map((issue) => ({...issue, entryIndex}))
  ));
  const seen = new Map<number, number>();
  entries.forEach((entry, entryIndex) => {
    if (!isPlainRecord(entry) || !Number.isInteger(entry.BH_CURVE_ID) || (entry.BH_CURVE_ID as number) <= 0) return;
    const id = entry.BH_CURVE_ID as number;
    const previous = seen.get(id);
    if (previous !== undefined) issues.push({
      severity: 'error', entryIndex, path: 'BH_CURVE_ID',
      message: `BH_CURVE_ID ${id} is already used by entry ${previous + 1}.`,
    });
    else seen.set(id, entryIndex);
  });
  const defined = new Set(seen.keys());
  for (const consumer of collectBhCurveConsumers(rootValue)) {
    if (!defined.has(consumer.curveId)) issues.push({
      severity: 'warning', path: consumer.path,
      message: `${consumer.label} references BH_CURVE_ID ${consumer.curveId}, which is not defined in 20_BH_Curve.`,
    });
  }
  return issues;
}

export function bhCurveUsage(rootValue: unknown, curveId: unknown): BhCurveConsumer[] {
  if (!Number.isInteger(curveId)) return [];
  return collectBhCurveConsumers(rootValue).filter((consumer) => consumer.curveId === curveId);
}

export function bhCurvePreviewPoints(value: unknown): BhCurvePreviewPoint[] {
  const inspected = inspectBhCurveEntry(value);
  if (inspected.kind !== 'guided') return [];
  const data = inspected.value.data as JsonRecord;
  const hValues = data.H as unknown[];
  const bValues = data.B as unknown[];
  if (hValues.length < 2 || hValues.length !== bValues.length) return [];
  if (!hValues.every(finiteNumber) || !bValues.every(finiteNumber)) return [];
  return hValues.map((h, index) => ({h: h as number, b: bValues[index] as number}));
}
