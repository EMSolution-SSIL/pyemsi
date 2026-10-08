# Python source module `femresult.resulttools`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Fem/femresult/resulttools.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import numpy as np

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femresult.resulttools.np` -> `numpy`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femresult/resulttools.py:31`.

### from math import isnan

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femresult.resulttools.isnan` -> `math.isnan`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femresult/resulttools.py:32`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femresult.resulttools.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femresult/resulttools.py:34`.

### from femtools.femutils import is_of_type

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femresult.resulttools.is_of_type` -> `femtools.femutils.is_of_type`.

[Source module `femtools.femutils`](../../femtools/femutils/index.md).

Evidence: `src/Mod/Fem/femresult/resulttools.py:36`.

## `femresult.resulttools.purge_result_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def purge_result_objects(analysis):
```

Removes all result objects and result meshes from an analysis group.

Parameters
----------
analysis : Fem::FemAnalysis
    analysis group as a container for all  objects needed for the analysis

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:39`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.purge_postprocessing_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def purge_postprocessing_objects(analysis):
```

Removes all postprocessing objects and visualizations form the analysis

Parameters
----------
analysis : Fem::FemAnalysis
    analysis group as a container for all  objects needed for the analysis

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:69`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.purge_results`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def purge_results(analysis):
```

Removes all result and postprocessing objects and result meshes from an analysis group.

Parameters
----------
analysis : Fem::FemAnalysis
    analysis group as a container for all  objects needed for the analysis

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:92`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.reset_mesh_deformation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def reset_mesh_deformation(resultobj):
```

Resets result mesh deformation.

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:110`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.reset_mesh_color`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def reset_mesh_color(resultobj):
```

Resets result mesh color

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:124`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.show_displacement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def show_displacement(resultobj, displacement_factor=0.0):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:142`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.show_result`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def show_result(resultobj, result_type='Sabs', limit=None):
```

Sets mesh color using selected type of results.

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object
result_type : str, optional
    default is Sabs
    FreeCAD FEM mechanical result object
    - U1, U2, U3 - deformation
    - Uabs - absolute deformation
    - Sabs - Von Mises stress
limit : float
    limit cutoff value. All values over the limit are treated
    as equal to the limit. Useful for filtering out hotspots.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:152`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.show_color_by_scalar_with_cutoff`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def show_color_by_scalar_with_cutoff(resultobj, values, limit=None):
```

Sets mesh color using list of values. Internally used by show_result function.

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object
values : list of floats
    the values to be colored and cutoff
    has to be the same length as resultobj.NodeNumbers
    resultobj.NodeNumbers has to be present in the resultobj
limit : float
    limit cutoff value. All values over the limit are treated
    as equal to the limit. Useful for filtering out hotspots.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:188`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.get_stats`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_stats(res_obj, result_type):
```

Returns minimum and maximum value for provided result type

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object
result_type : str
    type of FEM result
    allowed are: see dict keys in def get_all_stats()
    None - always return (0.0, 0.0)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:219`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.get_all_stats`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_all_stats(res_obj):
```

Returns all stats for provided result type.

- U1, U2, U3 - deformation
- Uabs - absolute deformation
- Sabs - Von Mises stress
- MaxPrin - Principal stress 1
- MidPrin - Principal stress 2
- MinPrin - Principal stress 3
- MaxShear - maximum shear stress
- Peeq - peeq strain
- Temp - Temperature
- MFlow - MassFlowRate
- NPress - NetworkPressure

for more information on result types and names
see in code file src/Mod/Fem/App/FemVTKTools.cpp
the methods _getFreeCADMechResultVectorProperties()
and _getFreeCADMechResultScalarProperties()
as well as forum topic
https://forum.freecad.org/viewtopic.php?f=18&t=33106&start=30#p277434

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:252`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.fill_femresult_stats`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def fill_femresult_stats(res_obj):
```

Fills a FreeCAD FEM mechanical result object with stats data.

Parameters
----------
resultobj : Fem::ResultMechanical
    FreeCAD FEM mechanical result object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:299`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.add_disp_apps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def add_disp_apps(res_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:410`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.add_von_mises`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def add_von_mises(res_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:416`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.add_principal_stress_std`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def add_principal_stress_std(res_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:433`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_csr`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_csr(ps1, ps2, ps3, alpha, beta, res_obj):
```

Calculate critical strain ratio.

Forum Discussion: https://forum.freecad.org/viewtopic.php?f=18&t=35893#p303392
Background: https://www.vtt.fi/inf/julkaisut/muut/2017/VTT-R-01177-17.pdf

critical strain ratio = peeq / critical_strain (>1.0 indicates ductile rupture)
    peeq = equivalent plastic strain
    critical strain = alpha * np.exp(-beta * T)
        alpha and beta are material parameters,
        where alpha can be related to unixial test data (user input) and
        beta is normally kept fixed at 1.5,
        unless available from extensive research experiments
        T = pressure / von Mises stress (stress triaxiality)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:496`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.get_concrete_nodes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_concrete_nodes(res_obj):
```

Determine concrete / non-concrete nodes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:527`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.add_principal_stress_reinforced`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def add_principal_stress_reinforced(res_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:571`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.compact_result`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def compact_result(res_obj):
```

compacts result.Mesh and appropriate result.NodeNumbers

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:683`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_von_mises`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_von_mises(stress_tensor):
```

Calculate Von mises stress.
See http://en.wikipedia.org/wiki/Von_Mises_yield_criterion
Simplification: https://forum.freecad.org/viewtopic.php?f=18&t=33974&p=296542#p296542

stress_tensor ... (Sxx, Syy, Szz, Sxy, Sxz, Syz)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:710`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_principal_stress_std`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_principal_stress_std(stress_tensor):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:726`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_principal_stress_reinforced`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_principal_stress_reinforced(stress_tensor):
```

Calculate principal stress vectors and values.

For total stresses use:
stress_tensor[0], stress_tensor[1], stress_tensor[2]
on the diagonal of the stress tensor

Difference with the original method:
https://forum.freecad.org/viewtopic.php?f=18&t=33106&start=90#p296539

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:751`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_rho`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_rho(stress_tensor, fy):
```

Calculation of Reinforcement Ratios and Concrete Stresses
(in accordance with http://heronjournal.nl/53-4/3.pdf)

Parameters
----------
- fy: factored yield strength of reinforcement bars

See post:
https://forum.freecad.org/viewtopic.php?f=18&t=28821

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:801`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_mohr_coulomb`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_mohr_coulomb(prin1, prin3, phi, fck):
```

Calculation of Mohr Coulomb yield criterion to judge
concrete crushing and shear failure.

Parameters
----------
- phi: angle of internal friction
- fck: factored compressive strength of the matrix material (usually concrete)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:959`. Decorators are copied as source expressions and have not been executed.

## `femresult.resulttools.calculate_disp_abs`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_disp_abs(displacements):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femresult/resulttools.py:979`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`femresult.resulttools.__title__`, `femresult.resulttools.__author__`, `femresult.resulttools.__url__`. These are source internals unless an explicit export establishes otherwise.

