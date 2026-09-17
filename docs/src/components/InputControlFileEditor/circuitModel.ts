import {
  collectEmSolutionReferences,
  deepClone,
  isEmSolutionInput,
  isPlainRecord,
  type JsonRecord,
} from './emSolutionModel';

export interface CircuitDefinition extends JsonRecord {
  REGION_FACTOR?: unknown;
  REGION_PARALLEL?: unknown;
  SERIES_IDS?: unknown;
  INDUCTANCE_MATRIX?: unknown;
  RESISTANCE_MATRIX?: unknown;
  CONNECTION_MATRIX?: unknown;
  POWER_SUPPLIES?: unknown;
}

export interface CircuitPowerSupply extends JsonRecord {
  PS_ID?: unknown;
  TYPE?: unknown;
  TIME_ID?: unknown;
  INITIAL_CURRENT?: unknown;
}

export interface CircuitSection {
  sourceIndex: number;
  circuit: unknown;
}

export interface CircuitValidationIssue {
  severity: 'error' | 'warning';
  path: string;
  message: string;
}

export type SymmetricMatrixMode = 0 | 1 | 2;
export type ConnectionMatrixMode = 0 | 1;

export function isCircuitDefinition(value: unknown): value is CircuitDefinition {
  return isPlainRecord(value);
}

export function findCircuitSections(value: unknown): CircuitSection[] {
  if (!isEmSolutionInput(value) || !isPlainRecord(value)) return [];
  const sources = value['17_Field_Source'];
  if (!Array.isArray(sources)) return [];
  return sources.flatMap((source, sourceIndex) => (
    isPlainRecord(source) && Object.hasOwn(source, 'CIRCUIT')
      ? [{sourceIndex, circuit: source.CIRCUIT}]
      : []
  ));
}

export function replaceCircuitSections(value: unknown, sections: CircuitSection[]): unknown {
  const result = deepClone(value);
  if (!isPlainRecord(result) || !Array.isArray(result['17_Field_Source'])) return result;
  for (const section of sections) {
    const source = result['17_Field_Source'][section.sourceIndex];
    if (isPlainRecord(source)) source.CIRCUIT = deepClone(section.circuit);
  }
  return result;
}

function modeValue(value: unknown): number | undefined {
  return Number.isInteger(value) ? value as number : undefined;
}

function matrixValues(value: unknown): unknown[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((row) => Array.isArray(row) ? row : [row]);
}

export function readSymmetricMatrix(value: unknown, size: number, mode: unknown): unknown[][] {
  const grid = Array.from({length: size}, () => Array<unknown>(size).fill(''));
  if (!Array.isArray(value) || mode === 2) return grid;
  if (mode === 1) {
    const values = matrixValues(value);
    for (let index = 0; index < size; index += 1) grid[index][index] = values[index] ?? '';
    return grid;
  }
  let flatIndex = 0;
  const nested = value.every(Array.isArray);
  for (let row = 0; row < size; row += 1) {
    for (let column = 0; column <= row; column += 1) {
      const entry = nested
        ? (value[row] as unknown[] | undefined)?.[column]
        : value[flatIndex];
      const cell = entry ?? '';
      grid[row][column] = cell;
      grid[column][row] = cell;
      flatIndex += 1;
    }
  }
  return grid;
}

export function readConnectionMatrix(value: unknown, rows: number, columns: number): unknown[][] {
  const grid = Array.from({length: rows}, () => Array<unknown>(columns).fill(''));
  if (!Array.isArray(value)) return grid;
  const nested = value.every(Array.isArray);
  let flatIndex = 0;
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      grid[row][column] = (nested
        ? (value[row] as unknown[] | undefined)?.[column]
        : value[flatIndex]) ?? '';
      flatIndex += 1;
    }
  }
  return grid;
}

function writeSymmetricMatrix(grid: unknown[][], mode: unknown): unknown[] {
  if (mode === 2) return [];
  if (mode === 1) return grid.map((row, index) => row[index] ?? '');
  return grid.map((row, rowIndex) => row.slice(0, rowIndex + 1));
}

function writeConnectionMatrix(grid: unknown[][], mode: unknown): unknown[] {
  return mode === 1 ? [] : grid.map((row) => [...row]);
}

function matrixObject(value: unknown): JsonRecord {
  return isPlainRecord(value) ? value : {};
}

function seriesIds(circuit: CircuitDefinition): unknown[] {
  return Array.isArray(circuit.SERIES_IDS) ? circuit.SERIES_IDS : [];
}

function powerSupplies(circuit: CircuitDefinition): unknown[] {
  return Array.isArray(circuit.POWER_SUPPLIES) ? circuit.POWER_SUPPLIES : [];
}

export function normalizeCircuit(circuit: CircuitDefinition): CircuitDefinition {
  const result = deepClone(circuit);
  const seriesCount = seriesIds(result).length;
  const supplyCount = powerSupplies(result).length;
  const inductance = matrixObject(result.INDUCTANCE_MATRIX);
  const resistance = matrixObject(result.RESISTANCE_MATRIX);
  const connection = matrixObject(result.CONNECTION_MATRIX);
  inductance.MATRIX = writeSymmetricMatrix(
    readSymmetricMatrix(inductance.MATRIX, seriesCount, inductance.IN_IND),
    inductance.IN_IND,
  );
  resistance.MATRIX = writeSymmetricMatrix(
    readSymmetricMatrix(resistance.MATRIX, seriesCount, resistance.IN_RES),
    resistance.IN_RES,
  );
  connection.MATRIX = writeConnectionMatrix(
    readConnectionMatrix(connection.MATRIX, seriesCount, supplyCount),
    connection.IN_CON,
  );
  result.INDUCTANCE_MATRIX = inductance;
  result.RESISTANCE_MATRIX = resistance;
  result.CONNECTION_MATRIX = connection;
  return result;
}

function remapGrid(
  grid: unknown[][],
  rowIndices: Array<number | undefined>,
  columnIndices: Array<number | undefined>,
): unknown[][] {
  return rowIndices.map((sourceRow) => columnIndices.map((sourceColumn) => (
    sourceRow === undefined || sourceColumn === undefined
      ? ''
      : grid[sourceRow]?.[sourceColumn] ?? ''
  )));
}

export function remapCircuitSeries(
  circuit: CircuitDefinition,
  nextIds: unknown[],
  sourceIndices: Array<number | undefined>,
): CircuitDefinition {
  const result = deepClone(circuit);
  const oldCount = seriesIds(result).length;
  const supplyCount = powerSupplies(result).length;
  const inductance = matrixObject(result.INDUCTANCE_MATRIX);
  const resistance = matrixObject(result.RESISTANCE_MATRIX);
  const connection = matrixObject(result.CONNECTION_MATRIX);
  const oldInductance = readSymmetricMatrix(inductance.MATRIX, oldCount, inductance.IN_IND);
  const oldResistance = readSymmetricMatrix(resistance.MATRIX, oldCount, resistance.IN_RES);
  const oldConnection = readConnectionMatrix(connection.MATRIX, oldCount, supplyCount);
  inductance.MATRIX = writeSymmetricMatrix(remapGrid(oldInductance, sourceIndices, sourceIndices), inductance.IN_IND);
  resistance.MATRIX = writeSymmetricMatrix(remapGrid(oldResistance, sourceIndices, sourceIndices), resistance.IN_RES);
  connection.MATRIX = writeConnectionMatrix(
    remapGrid(oldConnection, sourceIndices, Array.from({length: supplyCount}, (_, index) => index)),
    connection.IN_CON,
  );
  result.SERIES_IDS = [...nextIds];
  result.INDUCTANCE_MATRIX = inductance;
  result.RESISTANCE_MATRIX = resistance;
  result.CONNECTION_MATRIX = connection;
  return result;
}

export function remapCircuitPowerSupplies(
  circuit: CircuitDefinition,
  nextSupplies: unknown[],
  sourceIndices: Array<number | undefined>,
): CircuitDefinition {
  const result = deepClone(circuit);
  const rowCount = seriesIds(result).length;
  const oldSupplies = powerSupplies(result);
  const connection = matrixObject(result.CONNECTION_MATRIX);
  const oldGrid = readConnectionMatrix(connection.MATRIX, rowCount, oldSupplies.length);
  connection.MATRIX = writeConnectionMatrix(
    remapGrid(oldGrid, Array.from({length: rowCount}, (_, index) => index), sourceIndices),
    connection.IN_CON,
  );
  result.POWER_SUPPLIES = deepClone(nextSupplies);
  result.CONNECTION_MATRIX = connection;
  return result;
}

export function updateSymmetricMatrixCell(
  circuit: CircuitDefinition,
  key: 'INDUCTANCE_MATRIX' | 'RESISTANCE_MATRIX',
  row: number,
  column: number,
  value: unknown,
): CircuitDefinition {
  const result = deepClone(circuit);
  const matrix = matrixObject(result[key]);
  const modeKey = key === 'INDUCTANCE_MATRIX' ? 'IN_IND' : 'IN_RES';
  const grid = readSymmetricMatrix(matrix.MATRIX, seriesIds(result).length, matrix[modeKey]);
  grid[row][column] = value;
  grid[column][row] = value;
  matrix.MATRIX = writeSymmetricMatrix(grid, matrix[modeKey]);
  result[key] = matrix;
  return result;
}

export function updateConnectionMatrixCell(
  circuit: CircuitDefinition,
  row: number,
  column: number,
  value: unknown,
): CircuitDefinition {
  const result = deepClone(circuit);
  const connection = matrixObject(result.CONNECTION_MATRIX);
  const grid = readConnectionMatrix(connection.MATRIX, seriesIds(result).length, powerSupplies(result).length);
  grid[row][column] = value;
  connection.MATRIX = writeConnectionMatrix(grid, connection.IN_CON);
  result.CONNECTION_MATRIX = connection;
  return result;
}

export function setCircuitMatrixMode(
  circuit: CircuitDefinition,
  key: 'INDUCTANCE_MATRIX' | 'RESISTANCE_MATRIX' | 'CONNECTION_MATRIX',
  mode: number | string,
): CircuitDefinition {
  const result = deepClone(circuit);
  const matrix = matrixObject(result[key]);
  const seriesCount = seriesIds(result).length;
  const supplyCount = powerSupplies(result).length;
  if (key === 'CONNECTION_MATRIX') {
    const grid = readConnectionMatrix(matrix.MATRIX, seriesCount, supplyCount);
    matrix.IN_CON = mode;
    matrix.MATRIX = writeConnectionMatrix(grid, mode);
  } else {
    const modeKey = key === 'INDUCTANCE_MATRIX' ? 'IN_IND' : 'IN_RES';
    const grid = readSymmetricMatrix(matrix.MATRIX, seriesCount, matrix[modeKey]);
    matrix[modeKey] = mode;
    matrix.MATRIX = writeSymmetricMatrix(grid, mode);
  }
  result[key] = matrix;
  return result;
}

export function nextPowerSupplyId(supplies: unknown[]): number {
  const used = new Set<number>();
  for (const supply of supplies) {
    if (isPlainRecord(supply) && Number.isInteger(supply.PS_ID)) used.add(supply.PS_ID as number);
  }
  let candidate = 1;
  while (used.has(candidate)) candidate += 1;
  return candidate;
}

function numberIssue(value: unknown, integer: boolean): string | undefined {
  if (typeof value !== 'number' || !Number.isFinite(value)) return integer ? 'must be an integer' : 'must be a finite number';
  if (integer && !Number.isInteger(value)) return 'must be an integer';
  return undefined;
}

function validateSymmetricMatrix(
  matrixValue: unknown,
  matrixPath: string,
  modeKey: 'IN_IND' | 'IN_RES',
  size: number,
  error: (path: string, message: string) => void,
): void {
  if (!isPlainRecord(matrixValue)) {
    error(matrixPath, `${matrixPath} must be an object.`);
    return;
  }
  const mode = modeValue(matrixValue[modeKey]);
  if (mode === undefined || ![0, 1, 2].includes(mode)) error(`${matrixPath}.${modeKey}`, `${modeKey} must be 0, 1, or 2.`);
  if (!Array.isArray(matrixValue.MATRIX)) {
    error(`${matrixPath}.MATRIX`, 'MATRIX must be an array.');
    return;
  }
  const nested = matrixValue.MATRIX.length > 0 && matrixValue.MATRIX.every(Array.isArray);
  if (nested && mode === 0) {
    const validShape = matrixValue.MATRIX.length === size
      && matrixValue.MATRIX.every((row, index) => (row as unknown[]).length === index + 1);
    if (!validShape) error(`${matrixPath}.MATRIX`, `Nested lower-triangle rows must have lengths 1 through ${size}.`);
  }
  if (nested && mode === 1) {
    const validShape = matrixValue.MATRIX.length === size
      && matrixValue.MATRIX.every((row) => (row as unknown[]).length === 1);
    if (!validShape) error(`${matrixPath}.MATRIX`, `Nested diagonal data must contain ${size} one-value row${size === 1 ? '' : 's'}.`);
  }
  const values = matrixValues(matrixValue.MATRIX);
  const expected = mode === 0 ? size * (size + 1) / 2 : mode === 1 ? size : 0;
  if (mode !== undefined && values.length !== expected) {
    error(`${matrixPath}.MATRIX`, `MATRIX must contain ${expected} value${expected === 1 ? '' : 's'} for mode ${mode}.`);
  }
  values.forEach((entry, index) => {
    if (numberIssue(entry, false)) error(`${matrixPath}.MATRIX[${index}]`, 'Matrix value must be a finite number.');
  });
}

export function validateCircuit(circuitValue: unknown, rootValue?: unknown): CircuitValidationIssue[] {
  const issues: CircuitValidationIssue[] = [];
  const error = (path: string, message: string) => issues.push({severity: 'error', path, message});
  const warning = (path: string, message: string) => issues.push({severity: 'warning', path, message});
  if (!isPlainRecord(circuitValue)) {
    error('$', 'CIRCUIT must be an object.');
    return issues;
  }
  for (const key of ['REGION_FACTOR', 'REGION_PARALLEL']) {
    const problem = numberIssue(circuitValue[key], false);
    if (problem) error(key, `${key} ${problem}.`);
  }
  if (!Array.isArray(circuitValue.SERIES_IDS)) {
    error('SERIES_IDS', 'SERIES_IDS must be an array.');
  }
  if (!Array.isArray(circuitValue.POWER_SUPPLIES)) {
    error('POWER_SUPPLIES', 'POWER_SUPPLIES must be an array.');
  }
  const ids = Array.isArray(circuitValue.SERIES_IDS) ? circuitValue.SERIES_IDS : [];
  const supplies = Array.isArray(circuitValue.POWER_SUPPLIES) ? circuitValue.POWER_SUPPLIES : [];
  const references = collectEmSolutionReferences(rootValue);
  const seenSeries = new Map<number, number>();
  ids.forEach((id, index) => {
    const problem = numberIssue(id, true);
    if (problem) error(`SERIES_IDS[${index}]`, `Series ID ${problem}.`);
    if (Number.isInteger(id)) {
      const previous = seenSeries.get(id as number);
      if (previous !== undefined) error(`SERIES_IDS[${index}]`, `Series ID ${String(id)} is already used at position ${previous + 1}.`);
      else seenSeries.set(id as number, index);
      if (!references.seriesIds.includes(id as number)) warning(`SERIES_IDS[${index}]`, `Series ID ${String(id)} was not found in another 17_Field_Source entry.`);
    }
  });
  const seenSupplies = new Map<number, number>();
  supplies.forEach((supply, index) => {
    const base = `POWER_SUPPLIES[${index}]`;
    if (!isPlainRecord(supply)) {
      error(base, 'Power supply must be an object.');
      return;
    }
    for (const key of ['PS_ID', 'TYPE', 'TIME_ID']) {
      const problem = numberIssue(supply[key], true);
      if (problem) error(`${base}.${key}`, `${key} ${problem}.`);
    }
    const currentProblem = numberIssue(supply.INITIAL_CURRENT, false);
    if (currentProblem) error(`${base}.INITIAL_CURRENT`, `INITIAL_CURRENT ${currentProblem}.`);
    if (Number.isInteger(supply.PS_ID)) {
      const previous = seenSupplies.get(supply.PS_ID as number);
      if (previous !== undefined) error(`${base}.PS_ID`, `Power-supply ID ${String(supply.PS_ID)} is already used by row ${previous + 1}.`);
      else seenSupplies.set(supply.PS_ID as number, index);
    }
    if (Number.isInteger(supply.TYPE) && ![0, 1].includes(supply.TYPE as number)) {
      error(`${base}.TYPE`, 'TYPE must be 0 (constant current) or 1 (constant voltage).');
    }
    if (Number.isInteger(supply.TIME_ID) && supply.TIME_ID !== 0 && !references.timeIds.includes(supply.TIME_ID as number)) {
      warning(`${base}.TIME_ID`, `Time ID ${String(supply.TIME_ID)} was not found in 18_Time_Function.`);
    }
    if (typeof supply.INITIAL_CURRENT === 'number' && supply.INITIAL_CURRENT !== 0 && supply.TYPE !== 1) {
      warning(`${base}.INITIAL_CURRENT`, 'INITIAL_CURRENT is documented for constant-voltage supplies (TYPE 1).');
    }
    if (typeof supply.INITIAL_CURRENT === 'number' && supply.INITIAL_CURRENT !== 0
      && isPlainRecord(rootValue) && isPlainRecord(rootValue['2_Analysis_Type'])
      && rootValue['2_Analysis_Type'].TRANSIENT !== 1) {
      warning(`${base}.INITIAL_CURRENT`, 'INITIAL_CURRENT is documented for transient analysis.');
    }
  });

  validateSymmetricMatrix(circuitValue.INDUCTANCE_MATRIX, 'INDUCTANCE_MATRIX', 'IN_IND', ids.length, error);
  validateSymmetricMatrix(circuitValue.RESISTANCE_MATRIX, 'RESISTANCE_MATRIX', 'IN_RES', ids.length, error);
  if (!isPlainRecord(circuitValue.CONNECTION_MATRIX)) {
    error('CONNECTION_MATRIX', 'CONNECTION_MATRIX must be an object.');
  } else {
    const connection = circuitValue.CONNECTION_MATRIX;
    const mode = modeValue(connection.IN_CON);
    if (mode === undefined || ![0, 1].includes(mode)) error('CONNECTION_MATRIX.IN_CON', 'IN_CON must be 0 or 1.');
    if (!Array.isArray(connection.MATRIX)) {
      error('CONNECTION_MATRIX.MATRIX', 'MATRIX must be an array.');
    } else {
      const nested = connection.MATRIX.length > 0 && connection.MATRIX.every(Array.isArray);
      if (nested && mode === 0) {
        const validShape = connection.MATRIX.length === ids.length
          && connection.MATRIX.every((row) => (row as unknown[]).length === supplies.length);
        if (!validShape) error('CONNECTION_MATRIX.MATRIX', `Nested connection data must be ${ids.length} × ${supplies.length}.`);
      }
      const values = matrixValues(connection.MATRIX);
      const expected = mode === 0 ? ids.length * supplies.length : 0;
      if (mode !== undefined && values.length !== expected) {
        error('CONNECTION_MATRIX.MATRIX', `MATRIX must contain ${expected} value${expected === 1 ? '' : 's'} for mode ${mode}.`);
      }
      values.forEach((entry, index) => {
        if (numberIssue(entry, false)) error(`CONNECTION_MATRIX.MATRIX[${index}]`, 'Matrix value must be a finite number.');
      });
    }
    if (mode === 1 && ids.length !== supplies.length) {
      error('CONNECTION_MATRIX.IN_CON', 'Identity connection mode requires equal numbers of series and power supplies.');
    }
  }
  return issues;
}
