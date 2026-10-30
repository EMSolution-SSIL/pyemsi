import {describe, expect, it} from 'vitest';

import {
  findCircuitSections,
  type CircuitDefinition,
  normalizeCircuit,
  readSymmetricMatrix,
  remapCircuitPowerSupplies,
  remapCircuitSeries,
  replaceCircuitSections,
  setCircuitMatrixMode,
  validateCircuit,
} from './circuitModel';

function circuitDefinition(): CircuitDefinition {
  return {
    REGION_FACTOR: 8,
    REGION_PARALLEL: 1,
    SERIES_IDS: [1, 2],
    INDUCTANCE_MATRIX: {comment: 'keep', IN_IND: 0, MATRIX: [[1], [2, 3]]},
    RESISTANCE_MATRIX: {format: 'keep', IN_RES: 1, MATRIX: [4, 5]},
    CONNECTION_MATRIX: {custom: true, IN_CON: 0, MATRIX: [[1, 0], [0, 1]]},
    POWER_SUPPLIES: [
      {PS_ID: 1, TYPE: 1, TIME_ID: 1, INITIAL_CURRENT: 0, vendor: 'keep'},
      {PS_ID: 2, TYPE: 0, TIME_ID: 0, INITIAL_CURRENT: 0},
    ],
    futureSetting: {keep: true},
  };
}

function inputRoot() {
  return {
    metaData: {type: 'EMSolution_Input'},
    '0_Release_Number': {},
    '1_Execution_Control': {},
    '2_Analysis_Type': {TRANSIENT: 1},
    '17_Field_Source': [
      {ELMCUR: {SERIES_ID: 1}},
      {PHICOIL: {SERIES_ID: 2}},
      {CIRCUIT: circuitDefinition()},
    ],
    '18_Time_Function': {TIME_ID: 1},
  };
}

describe('EMSolution CIRCUIT model', () => {
  it('finds and immutably replaces CIRCUIT occurrences only in EMSolution field sources', () => {
    expect(findCircuitSections({CIRCUIT: circuitDefinition()})).toEqual([]);
    const root = inputRoot();
    const sections = findCircuitSections(root);
    expect(sections).toHaveLength(1);
    expect(sections[0].sourceIndex).toBe(2);
    const updated = replaceCircuitSections(root, [{...sections[0], circuit: {...circuitDefinition(), REGION_FACTOR: 4}}]) as ReturnType<typeof inputRoot>;
    expect((updated['17_Field_Source'][2] as any).CIRCUIT.REGION_FACTOR).toBe(4);
    expect((root['17_Field_Source'][2] as any).CIRCUIT.REGION_FACTOR).toBe(8);
  });

  it('loads flat lower-triangle data into a mirrored grid and emits nested canonical rows', () => {
    const circuit = circuitDefinition();
    (circuit.INDUCTANCE_MATRIX as any).MATRIX = [1, 2, 3];
    expect(readSymmetricMatrix((circuit.INDUCTANCE_MATRIX as any).MATRIX, 2, 0)).toEqual([[1, 2], [2, 3]]);
    const normalized = normalizeCircuit(circuit);
    expect((normalized.INDUCTANCE_MATRIX as any).MATRIX).toEqual([[1], [2, 3]]);
    expect((normalized.INDUCTANCE_MATRIX as any).comment).toBe('keep');
    expect(normalized.futureSetting).toEqual({keep: true});
  });

  it('normalizes diagonal, absent, explicit, and identity modes', () => {
    let circuit = circuitDefinition();
    circuit = setCircuitMatrixMode(circuit, 'INDUCTANCE_MATRIX', 1);
    circuit = setCircuitMatrixMode(circuit, 'RESISTANCE_MATRIX', 2);
    circuit = setCircuitMatrixMode(circuit, 'CONNECTION_MATRIX', 1);
    const normalized = normalizeCircuit(circuit);
    expect((normalized.INDUCTANCE_MATRIX as any).MATRIX).toEqual([1, 3]);
    expect((normalized.RESISTANCE_MATRIX as any).MATRIX).toEqual([]);
    expect((normalized.CONNECTION_MATRIX as any).MATRIX).toEqual([]);
  });

  it('permutes series rows and columns together and creates blank cells for additions', () => {
    const circuit = circuitDefinition();
    const reordered = remapCircuitSeries(circuit, [2, 1], [1, 0]);
    expect((reordered.INDUCTANCE_MATRIX as any).MATRIX).toEqual([[3], [2, 1]]);
    expect((reordered.CONNECTION_MATRIX as any).MATRIX).toEqual([[0, 1], [1, 0]]);
    const added = remapCircuitSeries(reordered, [2, 1, ''], [0, 1, undefined]);
    expect((added.INDUCTANCE_MATRIX as any).MATRIX[2]).toEqual(['', '', '']);
    expect((added.CONNECTION_MATRIX as any).MATRIX[2]).toEqual(['', '']);
  });

  it('permutes power supplies and their connection-matrix columns', () => {
    const circuit = circuitDefinition();
    const reordered = remapCircuitPowerSupplies(circuit, [circuit.POWER_SUPPLIES[1], circuit.POWER_SUPPLIES[0]], [1, 0]);
    expect((reordered.CONNECTION_MATRIX as any).MATRIX).toEqual([[0, 1], [1, 0]]);
    expect((reordered.POWER_SUPPLIES as any[]).map((item) => item.PS_ID)).toEqual([2, 1]);
  });

  it('accepts the supplied sample shape and preserves unknown nested properties', () => {
    const issues = validateCircuit(circuitDefinition(), inputRoot());
    expect(issues.filter((issue) => issue.severity === 'error')).toEqual([]);
    const normalized = normalizeCircuit(circuitDefinition());
    expect((normalized.POWER_SUPPLIES as any[])[0].vendor).toBe('keep');
    expect((normalized.CONNECTION_MATRIX as any).custom).toBe(true);
  });

  it('blocks invalid modes, dimensions, identifiers, supplies, and identity connections', () => {
    const circuit = circuitDefinition();
    circuit.SERIES_IDS = [1, 1, 'bad'] as any;
    circuit.INDUCTANCE_MATRIX = {IN_IND: 9, MATRIX: []};
    circuit.RESISTANCE_MATRIX = {IN_RES: 0, MATRIX: [1]};
    circuit.CONNECTION_MATRIX = {IN_CON: 1, MATRIX: []};
    circuit.POWER_SUPPLIES = [{PS_ID: 1, TYPE: 3, TIME_ID: 0, INITIAL_CURRENT: 0}] as any;
    const errors = validateCircuit(circuit, inputRoot()).filter((issue) => issue.severity === 'error');
    expect(errors).toEqual(expect.arrayContaining([
      expect.objectContaining({path: 'SERIES_IDS[1]', message: expect.stringContaining('already used')}),
      expect.objectContaining({path: 'SERIES_IDS[2]'}),
      expect.objectContaining({path: 'INDUCTANCE_MATRIX.IN_IND'}),
      expect.objectContaining({path: 'RESISTANCE_MATRIX.MATRIX'}),
      expect.objectContaining({path: 'POWER_SUPPLIES[0].TYPE'}),
      expect.objectContaining({path: 'CONNECTION_MATRIX.IN_CON', message: expect.stringContaining('equal numbers')}),
    ]));
  });

  it('reports unresolved references and context-sensitive initial-current warnings', () => {
    const circuit = circuitDefinition();
    circuit.SERIES_IDS = [99];
    circuit.INDUCTANCE_MATRIX = {IN_IND: 1, MATRIX: [1]};
    circuit.RESISTANCE_MATRIX = {IN_RES: 1, MATRIX: [1]};
    circuit.CONNECTION_MATRIX = {IN_CON: 0, MATRIX: [[1]]};
    circuit.POWER_SUPPLIES = [{PS_ID: 1, TYPE: 0, TIME_ID: 7, INITIAL_CURRENT: 2}];
    const root = {...inputRoot(), '2_Analysis_Type': {TRANSIENT: 0}};
    const warnings = validateCircuit(circuit, root).filter((issue) => issue.severity === 'warning');
    expect(warnings).toEqual(expect.arrayContaining([
      expect.objectContaining({path: 'SERIES_IDS[0]'}),
      expect.objectContaining({path: 'POWER_SUPPLIES[0].TIME_ID'}),
      expect.objectContaining({path: 'POWER_SUPPLIES[0].INITIAL_CURRENT', message: expect.stringContaining('TYPE 1')}),
      expect.objectContaining({path: 'POWER_SUPPLIES[0].INITIAL_CURRENT', message: expect.stringContaining('transient')}),
    ]));
  });
});
