# Python source module `ObjectsFem`

[Python catalogue](../index.md)

Evidence: `src/Mod/Fem/ObjectsFem.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## `ObjectsFem.makeMeshManipulate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshManipulate(doc, base_mesh, name='Manipulate'):
```

makeMeshManipulate(document, base_mesh, [name]):
creates a FEM mesh refinement object to manipulate the output of refinements

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:608`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshAdvanced`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshAdvanced(doc, base_mesh, name='Advanced'):
```

makeMeshAdvanced(document, base_mesh, [name]):
creates a FEM mesh refinement with various advanced methods

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:628`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshShape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshShape(doc, base_mesh, name='Shape'):
```

makeMeshShape(document, base_mesh [name]):
creates a FEM mesh refinement object to define properties for a refinement of a FEM mesh

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:647`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshTransfiniteCurve`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshTransfiniteCurve(doc, base_mesh, name='TransfiniteCurve'):
```

makeMeshTransfiniteCurve(document, base_mesh, [name]):
creates a FEM mesh refinement for transfinite curves

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:666`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshTransfiniteSurface`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshTransfiniteSurface(doc, base_mesh, name='TransfiniteSurface'):
```

makeMeshTransfiniteSurface(document, base_mesh, [name]):
creates a FEM mesh refinement for transfinite surfaces

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:686`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshTransfiniteVolume`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshTransfiniteVolume(doc, base_mesh, name='TransfiniteVolume'):
```

makeMeshTransfiniteVolume(document, base_mesh, [name]):
creates a FEM mesh refinement for transfinite volumes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:706`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshResult`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshResult(doc, name='MeshResult'):
```

makeMeshResult(document, name): makes a Fem MeshResult object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:726`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeResultMechanical`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeResultMechanical(doc, name='ResultMechanical'):
```

makeResultMechanical(document, [name]):
creates a mechanical result object to hold FEM results

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:740`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostVtkFilterClipRegion`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostVtkFilterClipRegion(doc, base_vtk_result, name='VtkFilterClipRegion'):
```

makePostVtkFilterClipRegion(document, base_vtk_result, [name]):
creates a FEM post processing region clip filter object (vtk based)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:754`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostVtkFilterClipScalar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostVtkFilterClipScalar(doc, base_vtk_result, name='VtkFilterClipScalar'):
```

makePostVtkFilterClipScalar(document, base_vtk_result, [name]):
creates a FEM post processing scalar clip filter object (vtk based)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:762`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostVtkFilterCutFunction`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostVtkFilterCutFunction(doc, base_vtk_result, name='VtkFilterCutFunction'):
```

makePostVtkFilterCutFunction(document, base_vtk_result, [name]):
creates a FEM post processing cut function filter object (vtk based)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:770`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostVtkFilterWarp`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostVtkFilterWarp(doc, base_vtk_result, name='VtkFilterWarp'):
```

makePostVtkFilterWarp(document, base_vtk_result, [name]):
creates a FEM post processing warp filter object (vtk based)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:778`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostVtkFilterContours`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostVtkFilterContours(doc, base_vtk_result, name='VtkFilterContours'):
```

makePostVtkFilterContours(document, base_vtk_result, [name]):
creates a FEM post processing contours filter object (vtk based)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:786`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostFilterGlyph`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostFilterGlyph(doc, base_vtk_result, name='Glyph'):
```

makePostVtkFilterGlyph(document, [name]):
creates a FEM post processing filter that visualizes vector fields with glyphs

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:794`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostVtkResult`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostVtkResult(doc, result_data, name='VtkResult'):
```

makePostVtkResult(document, base_result, [name]):
creates a FEM post processing result data (vtk based) to hold FEM results
Note: Result data get expanded, it can either be single result [result] or everything
      needed for a multistep result: [results_list, value_list, unit, description]

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:810`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostLineplot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostLineplot(doc, name='Lineplot'):
```

makePostLineplot(document, [name]):
creates a FEM post processing line plot

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:827`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostLineplotFieldData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostLineplotFieldData(doc, name='FieldData2D'):
```

makePostLineplotFieldData(document, [name]):
creates a FEM post processing data extractor for 2D Field data

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:842`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostLineplotIndexOverFrames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostLineplotIndexOverFrames(doc, name='IndexOverFrames2D'):
```

makePostLineplotIndexOverFrames(document, [name]):
creates a FEM post processing data extractor for 2D index data

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:857`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostHistogram`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostHistogram(doc, name='Histogram'):
```

makePostHistogram(document, [name]):
creates a FEM post processing histogram plot

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:872`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostHistogramFieldData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostHistogramFieldData(doc, name='FieldData1D'):
```

makePostHistogramFieldData(document, [name]):
creates a FEM post processing data extractor for 1D Field data

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:887`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostHistogramIndexOverFrames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostHistogramIndexOverFrames(doc, name='IndexOverFrames1D'):
```

makePostHistogramIndexOverFrames(document, [name]):
creates a FEM post processing data extractor for 1D Field data

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:902`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostTable`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostTable(doc, name='Table'):
```

makePostTable(document, [name]):
creates a FEM post processing histogram plot

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:917`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostTableFieldData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostTableFieldData(doc, name='FieldData1D'):
```

makePostTableFieldData(document, [name]):
creates a FEM post processing data extractor for 1D Field data

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:932`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makePostTableIndexOverFrames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePostTableIndexOverFrames(doc, name='IndexOverFrames1D'):
```

makePostTableIndexOverFrames(document, [name]):
creates a FEM post processing data extractor for 1D Field data

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:947`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationDeformation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationDeformation(doc, base_solver=None, name='Deformation'):
```

makeEquationDeformation(document, [base_solver], [name]):
creates a FEM deformation (nonlinear elasticity) equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:971`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationElasticity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationElasticity(doc, base_solver=None, name='Elasticity'):
```

makeEquationElasticity(document, [base_solver], [name]):
creates a FEM elasticity equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:979`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationElectricforce`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationElectricforce(doc, base_solver=None, name='Electricforce'):
```

makeEquationElectricforce(document, [base_solver], [name]):
creates a FEM Electricforce equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:987`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationElectrostatic`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationElectrostatic(doc, base_solver=None, name='Electrostatic'):
```

makeEquationElectrostatic(document, [base_solver], [name]):
creates a FEM electrostatic equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:995`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationFlow`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationFlow(doc, base_solver=None, name='Flow'):
```

makeEquationFlow(document, [base_solver], [name]):
creates a FEM flow equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1003`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationFlux`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationFlux(doc, base_solver=None, name='Flux'):
```

makeEquationFlux(document, [base_solver], [name]):
creates a FEM flux equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1011`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationHeat`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationHeat(doc, base_solver=None, name='Heat'):
```

makeEquationHeat(document, [base_solver], [name]):
creates a FEM heat equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1019`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationMagnetodynamic`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationMagnetodynamic(doc, base_solver=None, name='Magnetodynamic'):
```

makeEquationMagnetodynamic(document, [base_solver], [name]):
creates a FEM magnetodynamic equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1027`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationMagnetodynamic2D`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationMagnetodynamic2D(doc, base_solver=None, name='Magnetodynamic2D'):
```

makeEquationMagnetodynamic2D(document, [base_solver], [name]):
creates a FEM magnetodynamic2D equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1035`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeEquationStaticCurrent`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquationStaticCurrent(doc, base_solver=None, name='StaticCurrent'):
```

makeEquationStaticCurrent(document, [base_solver], [name]):
creates a FEM static current equation for a solver

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1043`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeSolverCalculiXCcxTools`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSolverCalculiXCcxTools(doc, name='SolverCcxTools'):
```

makeSolverCalculiXCcxTools(document, [name]):
makes a Calculix solver object for the ccx tools module

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1051`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeSolverCalculiX`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSolverCalculiX(doc, name='SolverCalculiX'):
```

makeSolverCalculiX(document, [name]):
makes a Calculix solver object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1065`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeSolverElmer`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSolverElmer(doc, name='SolverElmer'):
```

makeSolverElmer(document, [name]):
makes a Elmer solver object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1079`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeSolverMystran`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSolverMystran(doc, name='SolverMystran'):
```

makeSolverMystran(document, [name]):
makes a Mystran solver object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1094`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeSolverZ88`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSolverZ88(doc, name='SolverZ88'):
```

makeSolverZ88(document, [name]):
makes a Z88 solver object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:1103`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ObjectsFem.__title__`, `ObjectsFem.__author__`, `ObjectsFem.__url__`, `ObjectsFem._equation_creator`. These are source internals unless an explicit export establishes otherwise.

