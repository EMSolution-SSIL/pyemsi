# Python source module `ObjectsFem`

[Python catalogue](../index.md)

Evidence: `src/Mod/Fem/ObjectsFem.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ObjectsFem.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/ObjectsFem.py:33`.

## `ObjectsFem.makeAnalysis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeAnalysis(doc, name='Analysis'):
```

makeAnalysis(document, [name]):
makes a Fem Analysis object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:50`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstantVacuumPermittivity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstantVacuumPermittivity(doc, name='ConstantVacuumPermittivity'):
```

makeConstantVacuumPermittivity(document, [name]):
makes a Fem ConstantVacuumPermittivity object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:58`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintBearing`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintBearing(doc, name='ConstraintBearing'):
```

makeConstraintBearing(document, [name]):
makes a Fem ConstraintBearing object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:73`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintBodyHeatSource`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintBodyHeatSource(doc, name='BodyHeatSource'):
```

makeConstraintBodyHeatSource(document, [name]):
makes a Fem ConstraintBodyHeatSource object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:80`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintCentrif`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintCentrif(doc, name='CentrifugalForce'):
```

makeConstraintCentrif(document, [name]):
creates a centrif object to define centrifugal body load constraint

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:94`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintCurrentDensity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintCurrentDensity(doc, name='CurrentDensity'):
```

makeConstraintCurrentDensity(document, [name]):
makes a Fem CurrentDensity object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:108`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintContact`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintContact(doc, name='Contact'):
```

makeConstraintContact(document, [name]):
makes a Fem ConstraintContact object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:122`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintDisplacement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintDisplacement(doc, name='Displacement'):
```

makeConstraintDisplacement(document, [name]):
makes a Fem ConstraintDisplacement object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:129`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintElectricChargeDensity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintElectricChargeDensity(doc, name='ElectricCharge'):
```

makeConstraintElectricChargeDensity(document, [name]):
makes a Fem ElectricChargeDensity object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:136`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintElectromagnetic`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintElectromagnetic(doc, name='Electromagnetic'):
```

makeConstraintElectromagnetic(document, [name]):
makes a Fem Electromagnetic object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:150`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintFixed`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintFixed(doc, name='Fixed'):
```

makeConstraintFixed(document, [name]):
makes a Fem ConstraintFixed object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:164`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintRigidBody`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintRigidBody(doc, name='RigidBody'):
```

makeConstraintRigidBody(document, [name]):
makes a Fem ConstraintRigidBody object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:171`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintFlowVelocity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintFlowVelocity(doc, name='FlowVelocity'):
```

makeConstraintFlowVelocity(document, [name]):
makes a Fem ConstraintFlowVelocity object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:178`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintFluidBoundary`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintFluidBoundary(doc, name='FluidBoundary'):
```

makeConstraintFluidBoundary(document, name):
makes a Fem ConstraintFluidBoundary object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:192`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintForce`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintForce(doc, name='Force'):
```

makeConstraintForce(document, [name]):
makes a Fem ConstraintForce object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:199`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintGear`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintGear(doc, name='ConstraintGear'):
```

makeConstraintGear(document, [name]):
makes a Fem ConstraintGear object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:206`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintHeatflux`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintHeatflux(doc, name='HeatFlux'):
```

makeConstraintHeatflux(document, [name]):
makes a Fem ConstraintHeatflux object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:213`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintInitialFlowVelocity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintInitialFlowVelocity(doc, name='InitialFlowVelocity'):
```

makeConstraintInitialFlowVelocity(document, [name]):
makes a Fem ConstraintInitialFlowVelocity object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:220`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintInitialPressure`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintInitialPressure(doc, name='InitialPressure'):
```

makeConstraintInitialPressure(document, [name]):
makes a Fem ConstraintInitialPressure object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:234`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintInitialTemperature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintInitialTemperature(doc, name='InitialTemperature'):
```

makeConstraintInitialTemperature(document, name):
makes a Fem ConstraintInitialTemperature object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:248`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintMagnetization`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintMagnetization(doc, name='Magnetization'):
```

makeConstraintMagnetization(document, [name]):
makes a Fem Magnetization object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:255`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintPlaneRotation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintPlaneRotation(doc, name='PlaneRotation'):
```

makeConstraintPlaneRotation(document, [name]):
makes a Fem ConstraintPlaneRotation object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:269`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintPressure`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintPressure(doc, name='Pressure'):
```

makeConstraintPressure(document, [name]):
makes a Fem ConstraintPressure object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:276`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintPulley`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintPulley(doc, name='Pulley'):
```

makeConstraintPulley(document, [name]):
makes a Fem ConstraintPulley object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:283`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintSelfWeight`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintSelfWeight(doc, name='Gravity'):
```

makeConstraintSelfWeight(document, [name]):
creates a self weight object to define a gravity load

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:290`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintTemperature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintTemperature(doc, name='Temperature'):
```

makeConstraintTemperature(document, [name]):
makes a Fem ConstraintTemperature object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:304`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintTie`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintTie(doc, name='Tie'):
```

makeConstraintTie(document, [name]):
creates a tie object to define bonded faces constraint

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:311`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintTransform`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintTransform(doc, name='Transform'):
```

makeConstraintTransform(document, [name]):
makes a Fem ConstraintTransform object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:325`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintSectionPrint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintSectionPrint(doc, name='SectionPrint'):
```

makeConstraintSectionPrint(document, [name]):
creates a section print object to evaluate forces and moments of defined face

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:332`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeConstraintSpring`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConstraintSpring(doc, name='Spring'):
```

makeConstraintSpring(document, [name]):
makes a Fem ConstraintSpring object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:346`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeElementFluid1D`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeElementFluid1D(doc, name='ElementFluid1D'):
```

makeElementFluid1D(document, [name]):
creates a 1D fluid element object to define 1D flow

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:354`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeElementGeometry1D`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeElementGeometry1D(doc, sectiontype='Rectangular', width=10.0, height=25.0, thickness=2.0, name='ElementGeometry1D'):
```

makeElementGeometry1D(document, [width], [height], [name]):
creates a 1D geometry element object to define a cross section

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:368`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeElementGeometry2D`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeElementGeometry2D(doc, thickness=1.0, name='ElementGeometry2D'):
```

makeElementGeometry2D(document, [thickness], [name]):
creates a 2D geometry element object to define a plate thickness

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:400`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeElementRotation1D`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeElementRotation1D(doc, name='ElementRotation1D'):
```

makeElementRotation1D(document, [name]):
creates a 1D geometry rotation element object to rotate a 1D cross section

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:415`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMaterialFluid`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMaterialFluid(doc, name='MaterialFluid'):
```

makeMaterialFluid(document, [name]):
makes a FEM Material for fluid

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:430`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMaterialMechanicalNonlinear`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMaterialMechanicalNonlinear(doc, base_material, name='MaterialMechanicalNonlinear'):
```

makeMaterialMechanicalNonlinear(document, base_material, [name]):
creates a nonlinear material object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:445`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMaterialReinforced`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMaterialReinforced(doc, name='MaterialReinforced'):
```

makeMaterialReinforced(document, [matrix_material], [reinforcement_material], [name]):
creates a reinforced material object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:460`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMaterialSolid`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMaterialSolid(doc, name='MaterialSolid'):
```

makeMaterialSolid(document, [name]):
makes a FEM Material for solid

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:474`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshBoundaryLayer`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshBoundaryLayer(doc, base_mesh, name='MeshBoundaryLayer'):
```

makeMeshBoundaryLayer(document, base_mesh, [name]):
creates a FEM mesh BoundaryLayer object to define boundary layer properties

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:490`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshGmsh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshGmsh(doc, name='MeshGmsh'):
```

makeMeshGmsh(document, [name]):
makes a Gmsh FEM mesh object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:510`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshGroup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshGroup(doc, base_mesh, use_label=False, name='MeshGroup'):
```

makeMeshGroup(document, base_mesh, [use_label], [name]):
creates a FEM mesh refinement object to define properties for a region of a FEM mesh

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:524`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshNetgen`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshNetgen(doc, name='MeshNetgen'):
```

makeMeshNetgen(document, [name]):
makes a Netgen FEM mesh object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:546`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshNetgenLegacy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshNetgenLegacy(doc, name='MeshNetgen'):
```

makeMeshNetgenLegacy(document, [name]):
makes a old implementation Netgen FEM mesh object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:560`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshRegion`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshRegion(doc, base_mesh, element_length=0.0, name='MeshRegion'):
```

makeMeshRegion(document, base_mesh, [element_length], [name]):
creates a FEM mesh refinement object to define properties for a refinement of a FEM mesh

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:567`. Decorators are copied as source expressions and have not been executed.

## `ObjectsFem.makeMeshDistance`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMeshDistance(doc, base_mesh, name='Distance'):
```

makeMeshDistance(document, base_mesh, [name]):
creates a FEM mesh refinement object to define properties for a refinement of a FEM mesh

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/ObjectsFem.py:589`. Decorators are copied as source expressions and have not been executed.

