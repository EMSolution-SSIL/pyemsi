# Python source module `femmesh.meshtools`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Fem/femmesh/meshtools.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import numpy as np

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femmesh.meshtools.np` -> `numpy`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:32`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femmesh.meshtools.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:34`.

### from femtools import geomtools

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femmesh.meshtools.geomtools` -> `femtools.geomtools`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:36`.

## `femmesh.meshtools.get_femnodes_by_femobj_with_references`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femnodes_by_femobj_with_references(femmesh, femobj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:40`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelements_by_references`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelements_by_references(femmesh, femelement_table, references, femnodes_ele_table=None):
```

get the femelements for a list of references

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:65`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femnodes_by_references`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femnodes_by_references(femmesh, references):
```

get the femnodes for a list of references

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:87`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femnodes_by_refshape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femnodes_by_refshape(femmesh, ref):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:99`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_table(femmesh):
```

get_femelement_table(femmesh): { elementid : [ nodeid, nodeid, ... , nodeid ] }

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:127`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_volumes_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_volumes_table(femmesh):
```

get_femelement_volumes_table(femmesh): { elementid : [ nodeid, nodeid, ... , nodeid ] }

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:145`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_faces_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_faces_table(femmesh, faces_only=None):
```

get_femelement_faces_table(femmesh): { elementid : [ nodeid, nodeid, ... , nodeid ] }

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:154`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_edges_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_edges_table(femmesh, edges_only=None):
```

get_femelement_edges_table(femmesh): { elementid : [ nodeid, nodeid, ... , nodeid ] }

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:165`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femnodes_ele_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femnodes_ele_table(femnodes_mesh, femelement_table):
```

the femnodes_ele_table contains for each node its membership in elements
{nodeID : [[eleID, NodePosition], [], ...], nodeID : [[], [], ...], ...}
stored information is:
element number, the number of nodes per element
the position of the node in the element.
The position of the node in the element is coded
as a set bit at that position in a bit array (integer)
FIXME: the number of nodes per element should be
replaced by the type of the element
but I did not know how to get this from the mesh.
Since the femelement_table contains either
volume or face or edgemesh the femnodes_ele_table only
has either volume or face or edge elements
see get_femelement_table()

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:176`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_copy_of_empty_femelement_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_copy_of_empty_femelement_table(femelement_table):
```

{eleID : 0, eleID : 0, ...}

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:205`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_bit_pattern_dict`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_bit_pattern_dict(femelement_table, femnodes_ele_table, node_set):
```

Now we are looking for nodes inside of the Faces = filling the bit_pattern_dict
{eleID : [lenEleNodes, binary_position]}
see forum post for a very good explanation of what"s really happening
https://forum.freecad.org/viewtopic.php?f=18&t=17318&start=50#p141108
The bit_pattern_dict holds later an integer (bit array) for each element, which gives us
the information we are searching for:
Is this element part of the node list (searching for elements)
or has this element a face we are searching for?
The number in the ele_dict is organized as a bit array.
The corresponding bit is set, if the node of the node_set is contained in the element.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:214`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_element_volumes_elements_from_binary_search`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_element_volumes_elements_from_binary_search(bit_pattern_dict):
```

get volume element by coincident nodes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:238`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_element_faces_elements_from_binary_search`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_element_faces_elements_from_binary_search(bit_pattern_dict):
```

get face element by coincident nodes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:263`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_element_edges_elements_from_binary_search`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_element_edges_elements_from_binary_search(bit_pattern_dict):
```

get edge element by coincident nodes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:284`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_element_edges_from_binary_search`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_element_edges_from_binary_search(bit_pattern_dict, mask_tria3={}, mask_tria6={}, mask_quad4={}, mask_quad8={}):
```

get face element edges by coincident nodes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:301`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_element_faces_from_binary_search`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_element_faces_from_binary_search(bit_pattern_dict, mask_tetra4={}, mask_tetra10={}, mask_hexa8={}, mask_hexa20={}, mask_penta6={}, mask_penta15={}):
```

get volume element faces by coincident nodes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:321`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelements_by_femnodes_bin`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelements_by_femnodes_bin(femelement_table, femnodes_ele_table, node_list):
```

for every femelement of femelement_table
if all nodes of the femelement are in node_list,
the femelement is added to the list which is returned
blind fast binary search, but works for volumes only

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:354`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelements_by_femnodes_std`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelements_by_femnodes_std(femelement_table, node_list):
```

for every femelement of femelement_table
if all nodes of the femelement are in node_list,
the femelement is added to the list which is returned
e: elementlist
nodes: nodelist

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:373`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femvolumeelements_by_femfacenodes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femvolumeelements_by_femfacenodes(femelement_table, node_list):
```

assume femelement_table only has volume elements
for every femvolumeelement of femelement_table
for tetra4 and tetra10 the C++ methods could be used --> test again to be sure
if hexa8 volume element
    --> if exact 4 element nodes are in node_list --> add femelement
if hexa20 volume element
    --> if exact 8 element nodes are in node_list --> add femelement
if penta6 volume element
    --> if exact 3 or 6 element nodes are in node_list --> add femelement
if penta15 volume element
    --> if exact 6 or 8 element nodes are in node_list --> add femelement
e: elementlist
nodes: nodelist

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:392`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_sets`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_sets(femmesh, femelement_table, fem_objects, femnodes_ele_table=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:456`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_direction1D_set`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_direction1D_set(femmesh, femelement_table, beamrotation_objects, theshape=None):
```

get for each geometry edge direction, the local direction m and the element ids and
# write all into the beamrotation_objects
means no return value, we're going to write into the beamrotation_objects dictionary
FEMRotations1D is a list of dictionaries for every beamdirection of all edges
beamrot_obj["FEMRotations1D"] = [{
    "ids" : [theids],
    "direction" : direction,
    "beam_axis_m" : beam_axis_m
}, ... ]

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:508`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_directions_theshape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_directions_theshape(femmesh, femelement_table, theshape):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:562`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_beam_main_axis_m`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_beam_main_axis_m(beam_direction: FreeCAD.Vector, defined_angle: int) -> FreeCAD.Vector:
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:584`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femmesh_groupdata_sets_by_name`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femmesh_groupdata_sets_by_name(femmesh, fem_object, group_data_type):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:672`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_femelement_sets_from_group_data`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_femelement_sets_from_group_data(femmesh, fem_objects):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:695`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_elset_short_name`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_elset_short_name(obj, i):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:723`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_force_obj_vertex_nodeload_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_force_obj_vertex_nodeload_table(femmesh, frc_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:751`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_force_obj_edge_nodeload_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_force_obj_edge_nodeload_table(femmesh, femelement_table, femnodes_mesh, frc_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:789`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_ref_edgenodes_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_ref_edgenodes_table(femmesh, femelement_table, refedge):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:920`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_ref_edgenodes_lengths`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_ref_edgenodes_lengths(femnodes_mesh, edge_table):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:978`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_force_obj_face_nodeload_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_force_obj_face_nodeload_table(femmesh, femelement_table, femnodes_mesh, frc_obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1032`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_ref_facenodes_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_ref_facenodes_table(femmesh, femelement_table, ref_face):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1120`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_ref_facenodes_areas`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_ref_facenodes_areas(femnodes_mesh, face_table):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1186`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.build_mesh_faces_of_volume_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def build_mesh_faces_of_volume_elements(face_table, femelement_table):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1334`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_ref_shape_node_sum_geom_table`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_ref_shape_node_sum_geom_table(node_geom_table):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1488`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.pair_obj_reference`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pair_obj_reference(obj_ref):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1504`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_elements(sets_getter, ref_pair, face_masks, edge_masks):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1514`. Decorators are copied as source expressions and have not been executed.

## `femmesh.meshtools.get_elements_by_references`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_elements_by_references(sets_getter, femobj_ref):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femmesh/meshtools.py:1567`. Decorators are copied as source expressions and have not been executed.

