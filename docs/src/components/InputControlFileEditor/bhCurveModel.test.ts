import {describe, expect, it} from 'vitest';

import {
  bhCurvePreviewPoints,
  bhCurveSummary,
  collectBhCurveConsumers,
  createBhCurve,
  createBhCurveReferenceCatalog,
  createEncryptedBhCurve,
  duplicateBhCurve,
  findBhCurves,
  hasMalformedBhCurveRoot,
  inspectBhCurveEntry,
  nextBhCurveId,
  replaceBhCurves,
  validateBhCurves,
} from './bhCurveModel';

function root(entries?: unknown[]) {
  return {
    metaData: {type: 'EMSolution_Input'},
    ...(entries === undefined ? {} : {'20_BH_Curve': entries}),
  };
}

describe('B-H curve model', () => {
  it('classifies guided, encrypted, ambiguous, malformed, and unknown entries', () => {
    expect(inspectBhCurveEntry({BH_CURVE_ID: 1, data: {H: [0, 1], B: [0, 1]}}).kind).toBe('guided');
    expect(inspectBhCurveEntry({BH_CURVE_ID: 1, encrypted_data: 'secret'})).toMatchObject({kind: 'raw', reason: 'encrypted'});
    expect(inspectBhCurveEntry({data: {H: [], B: []}, encrypted_data: 'secret'})).toMatchObject({kind: 'raw', reason: 'ambiguous'});
    expect(inspectBhCurveEntry('bad')).toMatchObject({kind: 'raw', reason: 'malformed'});
    expect(inspectBhCurveEntry({BH_CURVE_ID: 1})).toMatchObject({kind: 'raw', reason: 'unknown'});
  });

  it('handles missing and malformed roots and replaces immutably', () => {
    const input = root();
    expect(findBhCurves(input)).toEqual([]);
    expect(hasMalformedBhCurveRoot({...input, '20_BH_Curve': {}})).toBe(true);
    const next = replaceBhCurves(input, [{BH_CURVE_ID: 1}]) as ReturnType<typeof root>;
    expect(next).not.toBe(input);
    expect(next['20_BH_Curve']).toEqual([{BH_CURVE_ID: 1}]);
    expect((input as any)['20_BH_Curve']).toBeUndefined();
  });

  it('allocates IDs and creates and duplicates entries without mutation', () => {
    const entries = [{BH_CURVE_ID: 1}, {BH_CURVE_ID: 3}];
    expect(nextBhCurveId(entries)).toBe(2);
    expect(createBhCurve(entries)).toEqual({BH_CURVE_ID: 2, data: {H: [0, 1], B: [0, 0]}});
    expect(createEncryptedBhCurve(entries)).toEqual({BH_CURVE_ID: 2, encrypted_data: ''});
    const original = {BH_CURVE_ID: 1, data: {H: [0, 4], B: [0, 2]}, vendor: {keep: true}};
    const duplicate = duplicateBhCurve(original, [original]) as typeof original;
    expect(duplicate).toEqual({...original, BH_CURVE_ID: 2});
    expect(duplicate.data).not.toBe(original.data);
    expect(original.BH_CURVE_ID).toBe(1);
  });

  it('validates structural errors, duplicate IDs, and advisory curve rules', () => {
    const value = root([
      {BH_CURVE_ID: 1, data: {H: [1, 2], B: [1, 0]}},
      {BH_CURVE_ID: 1, data: {H: [0], B: [0, Number.NaN]}},
      {BH_CURVE_ID: 3, encrypted_data: ''},
      {BH_CURVE_ID: 4, data: {H: [0, 1], B: [0, 1]}, encrypted_data: 'both'},
    ]);
    const issues = validateBhCurves(value);
    expect(issues).toEqual(expect.arrayContaining([
      expect.objectContaining({severity: 'warning', path: 'data[0]'}),
      expect.objectContaining({severity: 'warning', path: 'data.B[1]'}),
      expect.objectContaining({severity: 'error', message: expect.stringContaining('already used')}),
      expect.objectContaining({severity: 'error', message: expect.stringContaining('same number')}),
      expect.objectContaining({severity: 'error', path: 'encrypted_data'}),
      expect.objectContaining({severity: 'error', message: expect.stringContaining('either data or encrypted_data')}),
    ]));
  });

  it('accepts valid encrypted entries as raw with an advisory warning', () => {
    const value = root([{BH_CURVE_ID: 5, encrypted_data: 'ciphertext', vendor: 'keep'}]);
    expect(validateBhCurves(value)).toEqual([
      expect.objectContaining({severity: 'warning', entryIndex: 0, path: 'encrypted_data'}),
    ]);
    expect(bhCurveSummary(findBhCurves(value)[0])).toContain('Encrypted');
  });

  it('collects material and magnetization consumers and reports unresolved IDs', () => {
    const value = {
      ...root([{BH_CURVE_ID: 1, data: {H: [0, 1], B: [0, 1]}}]),
      '16_Material_Properties': {
        '16_1_3D_Element_Properties': [{MagneticProperty: {
          BH_CURVE_ID: 1,
          BH_CURVE_XYZ: {BH_XYZ_ID: [1, 2, 3]},
          ANISOTROPY2D: {BH_Z: 4},
        }}],
        '16_2_2D_Element_Properties': [{SURFACE_IMPEDANCE: {Nonliear_Parameters: {BH_CURVE_ID: 5}}}],
      },
      '20_6_Magnetization_BH_Curve': [{REF_BH_CURVE_ID: 6}],
    };
    expect(collectBhCurveConsumers(value).map((consumer) => consumer.curveId)).toEqual([1, 1, 2, 3, 4, 5, 6]);
    expect(validateBhCurves(value).filter((issue) => issue.entryIndex === undefined)).toHaveLength(5);
  });

  it('builds preview points only for complete finite paired tables', () => {
    const entry = {BH_CURVE_ID: 1, data: {H: [0, 10], B: [0, 1]}, vendor: 'keep'};
    expect(bhCurvePreviewPoints(entry)).toEqual([{h: 0, b: 0}, {h: 10, b: 1}]);
    expect(bhCurvePreviewPoints({BH_CURVE_ID: 1, data: {H: [0], B: [0, 1]}})).toEqual([]);
    expect(bhCurveSummary(entry)).toContain('2 point');
  });

  it('builds reference catalogs for missing, empty, malformed, guided, encrypted, and invalid entries', () => {
    expect(createBhCurveReferenceCatalog(root()).state).toBe('missing');
    expect(createBhCurveReferenceCatalog(root([])).state).toBe('empty');
    expect(createBhCurveReferenceCatalog({...root(), '20_BH_Curve': {}}).state).toBe('malformed');
    const catalog = createBhCurveReferenceCatalog(root([
      {BH_CURVE_ID: 1, data: {H: [0, 1], B: [0, 1]}},
      {BH_CURVE_ID: 2, encrypted_data: 'cipher'},
      {BH_CURVE_ID: 'bad', vendor: true},
      {BH_CURVE_ID: 1, vendor: 'duplicate'},
    ]));
    expect(catalog.state).toBe('ready');
    expect(catalog.choices).toEqual(expect.arrayContaining([
      expect.objectContaining({curveId: 1, typeLabel: 'H/B table', selectable: true, duplicate: true}),
      expect.objectContaining({curveId: 2, typeLabel: 'Encrypted / raw JSON', selectable: true, validationStatus: 'warning'}),
      expect.objectContaining({curveId: null, selectable: false, validationStatus: 'error'}),
      expect.objectContaining({curveId: 1, typeLabel: 'Unsupported raw JSON', selectable: true, duplicate: true}),
    ]));
    expect(catalog.choices[0].formattedJson).toContain('BH_CURVE_ID');
  });
});
