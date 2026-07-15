import {describe, expect, it} from 'vitest';

import {
  collectNetworkReferences,
  createNetworkComponent,
  findNetworkSections,
  isEmSolutionInput,
  NETWORK_COMPONENT_SCHEMAS,
  NETWORK_COMPONENT_TYPES,
  normalizeNetwork,
  replaceNetworkSections,
  validateNetwork,
} from './networkModel';

function inputRoot() {
  return {
    metaData: {type: 'EMSolution_Input', version: '1.0'},
    '0_Release_Number': {RLS_NO: 'r6.6'},
    '1_Execution_Control': {},
    '2_Analysis_Type': {STATIC: 0, AC: 0, TRANSIENT: 1},
    '17_Field_Source': [
      {PHICOIL: {SERIES_ID: 3, data: []}},
      {NETWORK: {
        REGION_FACTOR: 8,
        REGION_PARALLEL: 1,
        data: [
          {type: 'FEM', ID: 1, START: 1, END: 2, SERIES_ID: 3},
          {type: 'CPS', ID: 2, START: 2, END: 9999, TIME_ID: 1},
          {type: 'R', ID: 3, START: 9999, END: 1, RESISTANCE: 1e6},
        ],
      }},
    ],
    '18_Time_Function': [{TIME_ID: 1, OPTION: 2}],
  };
}

describe('EMSolution NETWORK model', () => {
  it('recognizes metadata and loose signature inputs but ignores generic JSON', () => {
    expect(isEmSolutionInput(inputRoot())).toBe(true);
    expect(isEmSolutionInput({'0_Release_Number': {}, '2_Analysis_Type': {}})).toBe(true);
    expect(isEmSolutionInput({metaData: {type: 'something-else'}, NETWORK: {}})).toBe(false);
  });

  it('finds and immutably replaces NETWORK occurrences', () => {
    const root = inputRoot();
    const sections = findNetworkSections(root);
    expect(sections).toHaveLength(1);
    expect(sections[0].sourceIndex).toBe(1);

    const replacement = {...sections[0], network: {...sections[0].network as object, REGION_FACTOR: 4}};
    const updated = replaceNetworkSections(root, [replacement]) as ReturnType<typeof inputRoot>;
    expect((updated['17_Field_Source'][1] as any).NETWORK.REGION_FACTOR).toBe(4);
    expect((root['17_Field_Source'][1] as any).NETWORK.REGION_FACTOR).toBe(8);
  });

  it('defines every documented NETWORK form and suggests only the element ID', () => {
    expect(Object.keys(NETWORK_COMPONENT_SCHEMAS).sort()).toEqual([...NETWORK_COMPONENT_TYPES].sort());
    for (const type of NETWORK_COMPONENT_TYPES) {
      const created = createNetworkComponent(type, [{type: 'R', ID: 1}]);
      expect(created.type).toBe(type);
      if (NETWORK_COMPONENT_SCHEMAS[type].fields.some((field) => field.key === 'ID') && !['SETV', 'SETI'].includes(type)) {
        expect(created.ID).toBe(2);
      }
      for (const field of NETWORK_COMPONENT_SCHEMAS[type].fields.filter((item) => item.key !== 'ID' || ['SETV', 'SETI'].includes(type))) {
        expect(created[field.key]).toBe('');
      }
    }
  });

  it('collects reference suggestions from the surrounding input file', () => {
    expect(collectNetworkReferences(inputRoot())).toEqual({seriesIds: [3], timeIds: [1]});
  });

  it('synchronizes TABLE counts without discarding extra properties', () => {
    const normalized = normalizeNetwork({
      REGION_FACTOR: 1,
      REGION_PARALLEL: 1,
      extraSetting: 'keep',
      data: [{
        type: 'TABLE',
        custom: true,
        NUMBER: 99,
        data: [{ID: 4, NO_DATA: 99, CURRENT: [0, 1], VOLTAGE: [0, 0.7]}],
      }],
    });
    const table = (normalized.data as any[])[0];
    expect(table.NUMBER).toBe(1);
    expect(table.data[0].NO_DATA).toBe(2);
    expect(table.custom).toBe(true);
    expect(normalized.extraSetting).toBe('keep');
  });

  it('separates blocking structural errors from advisory reference warnings', () => {
    const root = inputRoot();
    const issues = validateNetwork({
      REGION_FACTOR: 1,
      REGION_PARALLEL: 1,
      data: [
        {type: 'R', ID: 1, START: 1, END: 2, RESISTANCE: 5},
        {type: 'L', ID: 1, START: 2, END: 3, INDUCTANCE: 'bad'},
        {type: 'FEM', ID: 3, START: 3, END: 1, SERIES_ID: 999},
        {type: 'FUTURE_ELEMENT', ID: 4, payload: {keep: true}},
      ],
    }, root);
    expect(issues).toContainEqual(expect.objectContaining({severity: 'error', message: expect.stringContaining('already used')}));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'error', path: 'data[1].INDUCTANCE'}));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'warning', path: 'data[2].SERIES_ID'}));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'warning', path: 'data[3].type'}));
  });

  it('validates nested TABLE and SWITCH arrays and documented ordering', () => {
    const issues = validateNetwork({
      REGION_FACTOR: 1,
      REGION_PARALLEL: 1,
      data: [
        {type: 'M', ID: 1, L1: 10, L2: 11, INDUCTANCE: 0.1},
        {type: 'TABLE', NUMBER: 1, data: [{ID: 7, NO_DATA: 2, CURRENT: [0], VOLTAGE: [0, 1]}]},
        {type: 'TAB', ID: 2, START: 1, END: 2, TABLE_ID: 8},
        {type: 'SWITCH', ID: 3, START: 1, END: 2, ON_RES: 0.1, OFF_RES: 1e6, CYCLE: 1, PHASE_OP: 0, TIME_ID: 1, ON_TIME: [0], OFF_TIME: []},
      ],
    }, inputRoot());
    expect(issues).toContainEqual(expect.objectContaining({severity: 'warning', path: 'data[0].L1'}));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'error', path: 'data[1].data[0]'}));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'warning', path: 'data[2].TABLE_ID'}));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'error', path: 'data[3]'}));
  });
});
