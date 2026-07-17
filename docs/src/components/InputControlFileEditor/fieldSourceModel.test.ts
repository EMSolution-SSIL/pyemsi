import {describe, expect, it} from 'vitest';

import {
  createFieldSourceDefinition,
  createFieldSourceEntry,
  createFieldSourceRow,
  FIELD_SOURCE_SCHEMAS,
  FIELD_SOURCE_TYPES,
  findFieldSourceEntries,
  inspectFieldSourceEntry,
  normalizeFieldSources,
  replaceFieldSourceEntries,
  sourceRowTypes,
  validateFieldSourceEntry,
  validateFieldSources,
} from './fieldSourceModel';

function root(entries: unknown[] = []) {
  return {
    metaData: {type: 'EMSolution_Input'},
    '0_Release_Number': {},
    '1_Execution_Control': {},
    '2_Analysis_Type': {STATIC: 0, AC: 0, TRANSIENT: 1},
    '17_Field_Source': entries,
    '18_Time_Function': [{TIME_ID: 1}],
  };
}

describe('EMSolution Field Source model', () => {
  it('defines every supported source and documented COIL row form', () => {
    const documentationPages: Record<(typeof FIELD_SOURCE_TYPES)[number], string> = {
      COIL: '17_1_COIL', ELMCUR: '17_2_ELMCUR', SDEFCOIL: '17_3_SDEFCOIL', PHICOIL: '17_4_PHICOIL',
      DCCURR: '17_5_DCCURR', SUFCUR: '17_6_SUFCUR', SUFCUR2: '17_6_SUFCUR', MAGNET: '17_7_MAGNET',
      CIRCUIT: '17_8_CIRCUIT', NETWORK: '17_9_NETWORK', EPOTSUF: '17_10_EPOTSUF', POTNODE: '17_11_POTNODE',
    };
    expect(Object.keys(FIELD_SOURCE_SCHEMAS).sort()).toEqual([...FIELD_SOURCE_TYPES].sort());
    expect(sourceRowTypes('COIL').sort()).toEqual([
      'UNIF', 'LOOP', 'GCE', 'ARC', 'FGCE', 'FARC', 'MESH',
      'LOOP-', 'GCE-', 'ARC-', 'MESH-', 'LINE', 'DIPO', 'EXMAG',
    ].sort());
    for (const type of FIELD_SOURCE_TYPES) {
      expect(createFieldSourceEntry(type)).toHaveProperty(type);
      expect(FIELD_SOURCE_SCHEMAS[type].documentationUrl).toContain(documentationPages[type]);
    }
  });

  it('creates nested COIL integration fields and all MAGNET input-mode rows', () => {
    const integrated = createFieldSourceRow('COIL', {}, 'GCE-');
    expect(integrated).toEqual({type: 'GCE-', NDIV: 1, INT_X: 5, INT_Y: 5, INT_Z: 3});
    for (let inputType = 0; inputType <= 5; inputType += 1) {
      const row = createFieldSourceRow('MAGNET', {INPUT_TYPE: inputType});
      expect(row).toEqual(expect.any(Object));
      if (inputType === 1) expect(row).toHaveProperty('ELEM_ID');
      if (inputType === 3) expect(row).not.toHaveProperty('MXYZ');
      if (inputType === 4 || inputType === 5) expect(row).toHaveProperty('BH_MAGNET_CURVE_ID');
    }
  });

  it('marks scalar and array material references with their material collection', () => {
    expect(FIELD_SOURCE_SCHEMAS.SUFCUR.fields.find((field) => field.key === 'SMAT_ID')).toMatchObject({
      kind: 'integer', materialReference: 'surface',
    });
    expect(FIELD_SOURCE_SCHEMAS.PHICOIL.rowSchema?.fields.find((field) => field.key === 'MAT_IDS')).toMatchObject({
      kind: 'integer-array', materialReference: 'volume',
    });
    expect(FIELD_SOURCE_SCHEMAS.PHICOIL.rowSchema?.fields.find((field) => field.key === 'SMAT_ID')).toMatchObject({
      kind: 'integer', materialReference: 'surface',
    });
    expect(FIELD_SOURCE_SCHEMAS.SDEFCOIL.rowSchema?.fields.find((field) => field.key === 'SMAT_IDS')).toMatchObject({
      kind: 'integer-array', exactItems: 4, materialReference: 'surface',
    });
    expect(FIELD_SOURCE_SCHEMAS.MAGNET.fields.find((field) => field.key === 'MAT_ID')).toMatchObject({
      kind: 'integer', materialReference: 'volume',
    });
  });

  it('marks every guided TIME_ID field explicitly as a Time Function reference', () => {
    for (const type of ['COIL', 'SUFCUR', 'MAGNET', 'EPOTSUF', 'POTNODE'] as const) {
      expect(FIELD_SOURCE_SCHEMAS[type].fields.find((field) => field.key === 'TIME_ID')).toMatchObject({
        kind: 'integer', timeReference: true,
      });
    }
  });

  it('creates an absent source array and immutably replaces all entries', () => {
    const input = root();
    delete (input as any)['17_Field_Source'];
    expect(findFieldSourceEntries(input)).toEqual([]);
    const entries = [createFieldSourceEntry('SUFCUR')];
    const updated = replaceFieldSourceEntries(input, entries) as ReturnType<typeof root>;
    expect(updated['17_Field_Source']).toEqual(entries);
    expect((input as any)['17_Field_Source']).toBeUndefined();
    expect((replaceFieldSourceEntries(updated, []) as ReturnType<typeof root>)['17_Field_Source']).toEqual([]);
  });

  it('recognizes legacy EPOTNODE without renaming it during normalization', () => {
    const entry = {EPOTNODE: {SERIES_ID: 1, SMAT_ID: 0, TIME_ID: 1, NODE_IDS: [1], POTENTIALS: [2]}};
    expect(inspectFieldSourceEntry(entry)).toMatchObject({kind: 'known', type: 'POTNODE', key: 'EPOTNODE'});
    const normalized = normalizeFieldSources(root([entry])) as ReturnType<typeof root>;
    expect(normalized['17_Field_Source'][0]).toEqual(entry);
  });

  it('preserves unsupported entries and unknown properties while normalizing special sources', () => {
    const entries = [
      {WGMODE: {future: true}},
      {MAGNET: {SERIES_ID: 10, TIME_ID: 1, INPUT_TYPE: 0, data: [{MAT_ID: 5, COORD_ID: 0, MXYZ: [1, 0, 0], M: 1.2}]}, wrapperMeta: 'keep'},
      {NETWORK: {REGION_FACTOR: 1, REGION_PARALLEL: 1, vendor: 'keep', data: []}},
    ];
    const normalized = normalizeFieldSources(root(entries)) as ReturnType<typeof root>;
    expect(normalized['17_Field_Source'][0]).toEqual(entries[0]);
    expect((normalized['17_Field_Source'][1] as any).MAGNET.data[0].M).toBe(1.2);
    expect((normalized['17_Field_Source'][1] as any).wrapperMeta).toBe('keep');
    expect((normalized['17_Field_Source'][2] as any).NETWORK.vendor).toBe('keep');
  });

  it('separates raw warnings from malformed structural errors', () => {
    expect(validateFieldSourceEntry({FUTURE_SOURCE: {value: 1}})).toContainEqual(expect.objectContaining({severity: 'warning'}));
    expect(validateFieldSourceEntry(3)).toContainEqual(expect.objectContaining({severity: 'error'}));
    expect(validateFieldSourceEntry({COIL: {}, MAGNET: {}})).toContainEqual(expect.objectContaining({severity: 'error'}));
  });

  it('validates arrays, vectors, conditional MAGNET data, and time references', () => {
    const entries = [
      {DCCURR: {SERIES_ID: 1, IN_ROTOR: 0, data: [{MAT_IDS: [1, 2], SMAT_ID: 3, CURRENT: 1, SIGMA: [4], CAL_Je: 0}]}},
      {SDEFCOIL: {SERIES_ID: 4, IN_ROTOR: 0, data: [{MAT_ID: 1, SMAT_IDS: [1, 2, 3], CURRENT: 1, SIGMA: 2, CAL_Je: 0}]}},
      {MAGNET: {SERIES_ID: 2, TIME_ID: 99, INPUT_TYPE: 2, NO_ORDERS: 3, ORDERS: [1, 3], AMPLITUDES: [1], NO_POLES: 2, ANGLE: 0, data: [{MAT_ID: 4, COORD_ID: 0, MXYZ: [1, 0]}]}},
      {POTNODE: {SERIES_ID: 3, SMAT_ID: 0, TIME_ID: 1, NODE_IDS: [1, 2], POTENTIALS: [0]}},
    ];
    const issues = validateFieldSources(root(entries));
    expect(issues).toEqual(expect.arrayContaining([
      expect.objectContaining({path: 'DCCURR.data[0].SIGMA', severity: 'error'}),
      expect.objectContaining({path: 'SDEFCOIL.data[0].SMAT_IDS', severity: 'error'}),
      expect.objectContaining({path: 'MAGNET.AMPLITUDES', severity: 'error'}),
      expect.objectContaining({path: 'MAGNET.NO_ORDERS', severity: 'error'}),
      expect.objectContaining({path: 'MAGNET.data[0].MXYZ', severity: 'error'}),
      expect.objectContaining({path: 'MAGNET.TIME_ID', severity: 'warning'}),
      expect.objectContaining({path: 'POTNODE.POTENTIALS', severity: 'error'}),
    ]));
  });

  it('round-trips the active-file source mix and preserves the extra MAGNET M property', () => {
    const entries = [
      {PHICOIL: {SERIES_ID: 1, IN_ROTOR: 0, data: [{MAT_IDS: [10000], SMAT_ID: 10000, CURRENT: -9, SIGMA: 0, CAL_Je: 0}]}},
      {PHICOIL: {SERIES_ID: 2, IN_ROTOR: 0, data: []}},
      {PHICOIL: {SERIES_ID: 3, IN_ROTOR: 0, data: []}},
      {MAGNET: {SERIES_ID: 100, TIME_ID: 1, INPUT_TYPE: 0, data: [{MAT_ID: 50000, COORD_ID: 0, MXYZ: [0.9, 0.7, 0], M: 1.2}]}},
      {MAGNET: {SERIES_ID: 101, TIME_ID: 1, INPUT_TYPE: 0, data: []}},
      {NETWORK: createFieldSourceDefinition('NETWORK')},
    ];
    expect(validateFieldSources(root(entries)).filter((issue) => issue.severity === 'error')).toEqual([]);
    const normalized = normalizeFieldSources(root(entries)) as ReturnType<typeof root>;
    expect((normalized['17_Field_Source'][3] as any).MAGNET.data[0].M).toBe(1.2);
    expect(normalized['17_Field_Source']).toHaveLength(6);
  });

  it('provides valid empty skeletons for NETWORK and CIRCUIT', () => {
    const entries = [{NETWORK: createFieldSourceDefinition('NETWORK')}, {CIRCUIT: createFieldSourceDefinition('CIRCUIT')}];
    expect(validateFieldSources(root(entries)).filter((issue) => issue.severity === 'error')).toEqual([]);
  });
});
