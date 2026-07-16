import {describe, expect, it} from 'vitest';

import {
  createMaterialProperties,
  createSurfaceMaterial,
  createVolumeMaterial,
  hasMalformedMaterialPropertyRoot,
  inspectSurfaceMaterial,
  MATERIAL_DOCUMENTATION,
  nonlinearParametersKey,
  replaceMaterialProperties,
  SURFACE_MATERIAL_TYPES,
  validateMaterialProperties,
} from './materialPropertyModel';

function root(properties?: unknown, analysis: Record<string, number> = {STATIC: 0, AC: 0, TRANSIENT: 1}) {
  return {
    metaData: {type: 'EMSolution_Input'},
    '0_Release_Number': {},
    '1_Execution_Control': {},
    '2_Analysis_Type': analysis,
    ...(properties === undefined ? {} : {'16_Material_Properties': properties}),
    '20_BH_Curve': {BH_CURVE_ID: 1, data: {H: [0], B: [0]}},
  };
}

describe('EMSolution Material Property model', () => {
  it('defines all linked documentation pages and surface material types', () => {
    expect(MATERIAL_DOCUMENTATION.overview).toContain('16_Material_Properties');
    expect(MATERIAL_DOCUMENTATION.volume).toContain('16_1_3D_Element_Properties');
    expect(MATERIAL_DOCUMENTATION.electrostatic).toContain('16_1_2_ES_3D_Element_Properties');
    expect(MATERIAL_DOCUMENTATION.surface).toContain('16_2_2D_Element_Properties');
    expect(SURFACE_MATERIAL_TYPES).toEqual(['SURFACE_IMPEDANCE', 'GAP_ELEMENT', 'THIN_CONDUCTOR', 'SHELL_COIL']);
  });

  it('creates a missing material block without mutating the input', () => {
    const input = root();
    const properties = createMaterialProperties(input);
    expect(properties).toEqual({
      EXTEND_TOTAL_for_COIL: 0,
      '16_1_3D_Element_Properties': [],
      '16_2_2D_Element_Properties': [],
    });
    const next = replaceMaterialProperties(input, properties) as ReturnType<typeof root>;
    expect(next).not.toBe(input);
    expect(next['16_Material_Properties']).toEqual(properties);
    expect((input as any)['16_Material_Properties']).toBeUndefined();
  });

  it('uses context-aware defaults while keeping the shared volume shape', () => {
    expect(createVolumeMaterial(root(undefined, {STATIC: 2, AC: 0, TRANSIENT: 0}))).toEqual({
      MAT_ID: '', ElectricProperty: {conductivity: {SIGMA: 0}, permittivity: {EPS: 1}},
    });
    expect(createVolumeMaterial(root(undefined, {STATIC: 0, AC: 3, TRANSIENT: 0}))).toEqual({
      MAT_ID: '', POTENTIAL: 0,
      ElectricProperty: {conductivity: {SIGMA: 0}, permittivity: {EPS: 1}},
      MagneticProperty: {MU: 1},
    });
  });

  it('creates and recognizes every current surface type', () => {
    for (const type of SURFACE_MATERIAL_TYPES) {
      expect(inspectSurfaceMaterial(createSurfaceMaterial(type))).toMatchObject({kind: 'known', type});
    }
    expect(inspectSurfaceMaterial({FUTURE_SURFACE: {value: 1}})).toMatchObject({kind: 'raw', reason: 'unknown'});
    expect(inspectSurfaceMaterial({SURFACE_IMPEDANCE: {}, GAP_ELEMENT: {}})).toMatchObject({kind: 'raw', reason: 'multiple'});
    expect(inspectSurfaceMaterial(3)).toMatchObject({kind: 'raw', reason: 'malformed'});
  });

  it('retains both nonlinear-parameter spellings without migration', () => {
    expect(nonlinearParametersKey({Nonlinear_Parameters: {}})).toBe('Nonlinear_Parameters');
    expect(nonlinearParametersKey({Nonliear_Parameters: {}})).toBe('Nonliear_Parameters');
    const properties = {
      EXTEND_TOTAL_for_COIL: 0,
      '16_1_3D_Element_Properties': [],
      '16_2_2D_Element_Properties': [{SMAT_ID: 1, SURFACE_IMPEDANCE: {
        SIGMA: 1, MU: 1, IMP_TYPE: 1,
        Nonliear_Parameters: {BH_CURVE_ID: 1, AGRWALL: 0.75, K: 5, HK: 2000},
      }}],
    };
    const issues = validateMaterialProperties(root(properties));
    expect(issues).toContainEqual(expect.objectContaining({severity: 'warning', path: expect.stringContaining('Nonliear_Parameters')}));
    expect(properties['16_2_2D_Element_Properties'][0].SURFACE_IMPEDANCE).not.toHaveProperty('Nonlinear_Parameters');
  });

  it('validates advanced arrays, ranges, alternatives, and surface requirements', () => {
    const properties = {
      EXTEND_TOTAL_for_COIL: 0,
      THIN_CRITERION: 10,
      '16_1_3D_Element_Properties': [{
        MAT_ID: 1, MAT_NAME: 'steel', POTENTIAL: 0,
        ElectricProperty: {conductivity: {SIGMA: 1, SIGMA_XYZ: {COORD_ID: 0, FACTOR_XYZ: [1, 2, 0]}}},
        MagneticProperty: {
          MU: 1, PACKING: {PACKING_FACTOR: 1, COORD_ID: 0, PACKING_DIRECTION: [1, 1, 0]},
          ANISOTROPY2D: {COORD_ID: 0, BH_XY: 1},
          HYSTERESIS: {COORD_ID: 0, MU_Z: 1, DB_CAL: 0.001, J_A_Model: {MS: [1], K: [1, 1], C: [1, 1], A: [1, 1], ALPHA: [1, 1]}},
          IRON_LOSS: {COORD_ID: 0, MASS_DENSITY: 1, KE_XY: [1, 2]},
        },
      }],
      '16_2_2D_Element_Properties': [
        {SMAT_ID: 0, SURFACE_IMPEDANCE: {SIGMA: 1, MU: 1, IMP_TYPE: 2}},
        {SMAT_ID: 2, GAP_ELEMENT: {THICKNESS: 0}},
      ],
    };
    const issues = validateMaterialProperties(root(properties));
    expect(issues).toEqual(expect.arrayContaining([
      expect.objectContaining({path: expect.stringContaining('FACTOR_XYZ[1]'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('PACKING_FACTOR'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('PACKING_DIRECTION'), severity: 'warning'}),
      expect.objectContaining({path: expect.stringContaining('ANISOTROPY2D'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('J_A_Model.MS'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('IRON_LOSS'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('SMAT_ID'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('Nonlinear_Parameters'), severity: 'error'}),
      expect.objectContaining({path: expect.stringContaining('THICKNESS'), severity: 'error'}),
    ]));
  });

  it('round-trips active-file material names and unknown vendor data', () => {
    const material = {
      MAT_ID: 10,
      MAT_NAME: 'stator',
      POTENTIAL: 0,
      ElectricProperty: {conductivity: {SIGMA: 0, vendor: 'keep'}},
      MagneticProperty: {MU: 1, BH_CURVE_ID: 1},
      future: {enabled: true},
    };
    const properties = {EXTEND_TOTAL_for_COIL: 0, '16_1_3D_Element_Properties': [material], '16_2_2D_Element_Properties': []};
    const input = root(properties);
    const cloned = createMaterialProperties(input);
    expect(cloned['16_1_3D_Element_Properties']).toEqual([material]);
    expect(validateMaterialProperties(input).filter((issue) => issue.severity === 'error')).toEqual([]);
  });

  it('detects only malformed current-format roots and collections', () => {
    expect(hasMalformedMaterialPropertyRoot(root())).toBe(false);
    expect(hasMalformedMaterialPropertyRoot(root([]))).toBe(true);
    expect(hasMalformedMaterialPropertyRoot(root({'16_1_3D_Element_Properties': {MAT_ID: 1}}))).toBe(true);
    expect(hasMalformedMaterialPropertyRoot(root({'16_2_2D_Element_Properties': []}))).toBe(false);
  });
});
