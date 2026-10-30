import {describe, expect, it} from 'vitest';

import {
  changeTimeFunctionOption,
  collectTimeFunctionConsumers,
  createTimeFunction,
  createTimeFunctionReferenceCatalog,
  duplicateTimeFunction,
  findTimeFunctions,
  hasMalformedTimeFunctionRoot,
  inspectTimeFunctionEntry,
  nextTimeFunctionId,
  replaceTimeFunctions,
  sampleTimeFunction,
  SUPPORTED_TIME_FUNCTION_OPTIONS,
  TIME_FUNCTION_SCHEMAS,
  validateTimeFunctions,
} from './timeFunctionModel';

function root(entries: unknown[] = []) {
  return {
    metaData: {type: 'EMSolution_Input'},
    '17_Field_Source': [
      {COIL: {SERIES_ID: 1, TIME_ID: 1}},
      {NETWORK: {data: [{type: 'CPS', ID: 1, TIME_ID: 2}, {type: 'R', ID: 2, TIME_ID: 99}]}},
      {CIRCUIT: {POWER_SUPPLIES: [{PS_ID: 1, TIME_ID: 3}]}},
    ],
    '18_Time_Function': entries,
  };
}

describe('EMSolution Time Function model', () => {
  it('defines exactly the supported guided options and creates documented defaults', () => {
    expect(Object.keys(TIME_FUNCTION_SCHEMAS).map(Number)).toEqual([...SUPPORTED_TIME_FUNCTION_OPTIONS]);
    expect(createTimeFunction(0, [])).toMatchObject({TIME_ID: 1, OPTION: 0, C0: 0, C6: 0, TEXP: 1, TCYCLE: 1, PHASE4: 0});
    expect(createTimeFunction(1, [{TIME_ID: 1}])).toEqual({TIME_ID: 2, OPTION: 1, CYCLE: 0, TIME: [0, 1], VALUE: [0, 0]});
    expect(createTimeFunction(11, [])).toEqual({TIME_ID: 1, OPTION: 11, FUNCTION: '0'});
  });

  it('finds, replaces, and detects malformed roots without mutating input', () => {
    const original = root([{TIME_ID: 1, OPTION: 2, AMPLITUDE: 1, TCYCLE: 1, PHASE: 0}]);
    const replacement = [{TIME_ID: 2, OPTION: 11, FUNCTION: 'sin(T)'}];
    const updated = replaceTimeFunctions(original, replacement) as ReturnType<typeof root>;
    expect(findTimeFunctions(updated)).toEqual(replacement);
    expect(findTimeFunctions(original)[0]).toMatchObject({TIME_ID: 1});
    expect(hasMalformedTimeFunctionRoot({...original, '18_Time_Function': {TIME_ID: 1}})).toBe(true);
    expect(hasMalformedTimeFunctionRoot({metaData: {type: 'EMSolution_Input'}})).toBe(false);
  });

  it('classifies unsupported and malformed values as raw-only', () => {
    expect(inspectTimeFunctionEntry({TIME_ID: 1, OPTION: 3})).toMatchObject({kind: 'raw', reason: 'unsupported', option: 3});
    expect(inspectTimeFunctionEntry({TIME_ID: 1, OPTION: 99})).toMatchObject({kind: 'raw', reason: 'unsupported', option: 99});
    expect(inspectTimeFunctionEntry({TIME_ID: 1})).toMatchObject({kind: 'raw', reason: 'missing-option'});
    expect(inspectTimeFunctionEntry('bad')).toMatchObject({kind: 'raw', reason: 'malformed'});
  });

  it('allocates unique IDs, updates duplicates, and preserves vendor fields during guided mode changes', () => {
    const entries = [{TIME_ID: 1}, {TIME_ID: 3}, {TIME_ID: -1}];
    expect(nextTimeFunctionId(entries)).toBe(2);
    expect(duplicateTimeFunction({TIME_ID: 1, OPTION: 4, vendor: {keep: true}}, entries)).toEqual({TIME_ID: 2, OPTION: 4, vendor: {keep: true}});
    expect(changeTimeFunctionOption({TIME_ID: 7, OPTION: 2, AMPLITUDE: 3, TCYCLE: 4, PHASE: 5, comment: 'keep', vendor: 9}, 11)).toEqual({
      TIME_ID: 7, OPTION: 11, FUNCTION: '0', comment: 'keep', vendor: 9,
    });
  });

  it('validates IDs, guided fields, table alignment and ordering while allowing duplicate times', () => {
    const validTable = {TIME_ID: 1, OPTION: 1, CYCLE: 1, TIME: [0, 0.5, 0.5, 1], VALUE: [0, 1, 2, 0]};
    expect(validateTimeFunctions(root([validTable])).filter((issue) => issue.severity === 'error')).toEqual([]);
    const invalid = validateTimeFunctions(root([
      {...validTable, TIME: [0, 0.8, 0.4], VALUE: [0, 1]},
      {TIME_ID: 1, OPTION: 2, AMPLITUDE: 1, TCYCLE: -1, PHASE: 0},
      {TIME_ID: 3, OPTION: 3, nested: {keep: true}},
    ]));
    expect(invalid.some((issue) => issue.message.includes('same number'))).toBe(true);
    expect(invalid.some((issue) => issue.message.includes('non-decreasing'))).toBe(true);
    expect(invalid.some((issue) => issue.message.includes('already used'))).toBe(true);
    expect(invalid.some((issue) => issue.path === 'TCYCLE' && issue.severity === 'error')).toBe(true);
    expect(invalid.some((issue) => issue.path === 'OPTION' && issue.severity === 'warning')).toBe(true);
    expect(validateTimeFunctions(root([
      {TIME_ID: 1, OPTION: 0, C0: 0, C1: 0, C2: 0, C3: 0, C4: 0, C5: 0, C6: 0, TEXP: 0, TCYCLE: 0, PHASE4: 0},
      {TIME_ID: 2, OPTION: 2, AMPLITUDE: 1, TCYCLE: 0, PHASE: 0},
    ])).filter((issue) => issue.severity === 'error')).toEqual([]);
  });

  it('discovers consumers only in supported source, NETWORK, and CIRCUIT locations', () => {
    expect(collectTimeFunctionConsumers(root()).map((consumer) => [consumer.timeId, consumer.label])).toEqual([
      [1, 'COIL source 1'], [2, 'NETWORK CPS 1'], [3, 'CIRCUIT power supply 1'],
    ]);
  });

  it('builds an immutable picker catalog containing guided, raw, invalid, and duplicate rows', () => {
    const original = root([
      {TIME_ID: 2, OPTION: 2, AMPLITUDE: 3, TCYCLE: 1, PHASE: 0},
      {TIME_ID: 4, OPTION: 99, vendor: {keep: true}},
      {TIME_ID: 2, OPTION: 11, FUNCTION: 'T'},
      {TIME_ID: 'bad', OPTION: 4, PSIM_IN: 1, PSIM_OUT: 2},
      'damaged',
    ]);
    const before = JSON.stringify(original);
    const catalog = createTimeFunctionReferenceCatalog(original);
    expect(catalog.state).toBe('ready');
    expect(catalog.choices).toHaveLength(5);
    expect(catalog.choices[0]).toMatchObject({timeId: 2, option: 2, optionLabel: 'AC waveform', duplicate: true, selectable: true});
    expect(catalog.choices[1]).toMatchObject({timeId: 4, option: 99, optionLabel: 'Unsupported OPTION 99', validationStatus: 'warning', selectable: true});
    expect(catalog.choices[2]).toMatchObject({timeId: 2, duplicate: true});
    expect(catalog.choices[3]).toMatchObject({timeId: null, selectable: false, validationStatus: 'error'});
    expect(catalog.choices[4]).toMatchObject({timeId: null, optionLabel: 'Malformed entry', selectable: false});
    expect(catalog.choices[1].formattedJson).toContain('"vendor"');
    expect(JSON.stringify(original)).toBe(before);
  });

  it('reports missing, empty, and malformed picker catalog states', () => {
    expect(createTimeFunctionReferenceCatalog({metaData: {type: 'EMSolution_Input'}}).state).toBe('missing');
    expect(createTimeFunctionReferenceCatalog(root()).state).toBe('empty');
    expect(createTimeFunctionReferenceCatalog({...root(), '18_Time_Function': {TIME_ID: 1}}).state).toBe('malformed');
  });

  it('samples analytic, table, and AC previews without evaluating formula or raw modes', () => {
    const analytic = sampleTimeFunction({TIME_ID: 1, OPTION: 0, C0: 2, C1: 1, C2: 0, C3: 0, C4: 0, C5: 0, C6: 0, TEXP: 1, TCYCLE: 1, PHASE4: 0}, 2, 3);
    expect(analytic.points).toEqual([{time: 0, value: 2}, {time: 1, value: 3}, {time: 2, value: 4}]);
    expect(sampleTimeFunction({TIME_ID: 2, OPTION: 1, CYCLE: 0, TIME: [0, 0, 1], VALUE: [0, 1, 1]}).points).toEqual([
      {time: 0, value: 0}, {time: 0, value: 1}, {time: 1, value: 1},
    ]);
    const ac = sampleTimeFunction({TIME_ID: 3, OPTION: 2, AMPLITUDE: 2, TCYCLE: 1, PHASE: 0}, undefined, 3);
    expect(ac.points[0].value).toBeCloseTo(2);
    expect(ac.points[1].value).toBeCloseTo(-2);
    expect(sampleTimeFunction({TIME_ID: 4, OPTION: 11, FUNCTION: 'alert(1)'}).error).toMatch(/not available/);
    expect(sampleTimeFunction({TIME_ID: 5, OPTION: 3, arbitrary: true}).error).toMatch(/not available/);
    expect(sampleTimeFunction({TIME_ID: 6, OPTION: 2, AMPLITUDE: 1, TCYCLE: 0, PHASE: 0}).error).toMatch(/finite preview/);
  });
});
