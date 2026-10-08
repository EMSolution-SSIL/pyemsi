# Python source module `femmesh.meshtools`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Fem/femmesh/meshtools.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## `femmesh.meshtools.get_subelements_by_references`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_subelements_by_references(sets_getter, femobj_ref, face_masks, edge_masks):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1606`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_mesh_group_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_mesh_group_elements(mesh_group_obj, aPart):
```

the Reference shapes of the mesh_group_object are searched in the Shape of aPart.
If found in shape they are added to a dict
{MeshGroupIdentifier : ["ShapeType of the Elements"], [ElementID, ElementID, ...], ...}

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1645`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_analysis_group_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_analysis_group_elements(aAnalysis, aPart):
```

all Reference shapes of all Analysis member are searched in the Shape of aPart.
If found in shape they are added to a dict
{ConstraintName : ["ShapeType of the Elements"], [ElementID, ElementID, ...], ...}

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1664`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_reference_group_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_reference_group_elements(obj, aPart):
```

obj is an FEM object which has reference shapes like the group object
the material, most of the constraints
aPart is geometry feature normally CompSolid
the method searches all reference shapes of obj inside aPart even if
the reference shapes are a totally different geometry feature.
a tuple is returned ("Name or Label of the FEMobject", ["Element1", "Element2", ...])
The names in the list are the Elements of the geometry aPart
whereas "Solid1" == aPart.Shape.Solids[0]
!!! It is strongly recommended to use as reference shapes the Solids of a CompSolid
and not the Solids the CompSolid is made of !!!
see https://forum.freecad.org/viewtopic.php?f=18&t=12212&p=175777#p175777
and following posts
Occt might change the Solids a CompSolid is made of during
creation of the CompSolid by adding Edges and vertices
Thus the Elements do not have the same geometry anymore

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1722`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_anlysis_empty_references_group_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_anlysis_empty_references_group_elements(group_elements, aAnalysis, aShape):
```

get the elementIDs if the Reference shape is empty
see get_analysis_group_elements() for more information

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1801`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.femelements_count_ok`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def femelements_count_ok(len_femelement_table, count_femelements):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1868`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.delete_duplicate_mesh_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def delete_duplicate_mesh_elements(refelement_table):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1883`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_triangle_area`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_triangle_area(P1, P2, P3):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1892`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.sortlistoflistvalues`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def sortlistoflistvalues(listoflists):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1903`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.is_solid_femmesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_solid_femmesh(femmesh):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1911`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.has_no_face_data`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def has_no_face_data(femmesh):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1918`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.is_face_femmesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_face_femmesh(femmesh):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1925`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.is_edge_femmesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_edge_femmesh(femmesh):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1932`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.is_zplane_2D_mesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_zplane_2D_mesh(femmesh):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1939`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femmesh_eletype`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femmesh_eletype(femmesh, femelement_table=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1953`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_three_non_colinear_nodes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_three_non_colinear_nodes(nodes_coords):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:2018`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.use_correct_fluidinout_ele_def`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def use_correct_fluidinout_ele_def(FluidInletoutlet_ele, fileName, fluid_inout_nodes_file):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:2063`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.compact_mesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def compact_mesh(old_femmesh):
```

removes all gaps in node and element ids, start ids with 1
returns a tuple (FemMesh, node_assignment_map, element_assignment_map)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:2140`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.sub_shape_at_global_placement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def sub_shape_at_global_placement(obj, sub_name):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:2198`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`femmesh.meshtools.__title__`, `femmesh.meshtools.__author__`, `femmesh.meshtools.__url__`. These are source internals unless an explicit export establishes otherwise.

