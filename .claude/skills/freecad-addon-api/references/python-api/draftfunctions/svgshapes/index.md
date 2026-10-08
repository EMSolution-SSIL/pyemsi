# Python source module `draftfunctions.svgshapes`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py`. Import path is source-routed; installed availability is unverified.

Provides functions to return the SVG representation of some shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:32`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:36`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:37`.

### from draftgeoutils import edges as geo_edges

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.geo_edges` -> `draftgeoutils.edges`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:38`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:39`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:40`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:41`.

### from draftutils.messages import _msg, _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgshapes._msg` -> `draftutils.messages._msg`.

Bound source name `draftfunctions.svgshapes._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:42`.

## `draftfunctions.svgshapes.get_proj`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_proj(vec, plane=None):
```

Get a projection of the vector in the plane's u and v directions.

TODO: check if the same function for SVG and DXF projection can be used
so that this function is not just duplicated code.
This function may also be present elsewhere, like `WorkingPlane`
or `DraftGeomUtils`, so we should avoid code duplication.

Parameters
----------
vec: Base::Vector3
    An arbitrary vector that will be projected on the U and V directions.

plane: WorkingPlane.PlaneBase
    Working plane.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:52`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.getProj`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getProj(vec, plane=None):
```

Get a projection of a vector. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:88`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.get_discretized`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_discretized(edge, plane):
```

Get a discretized edge on a plane.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:94`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.getDiscretized`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDiscretized(edge, plane):
```

Get a discretized edge on a plane. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:120`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.get_circle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_circle(plane, fill, stroke, linewidth, lstyle, edge):
```

Get the SVG representation from a circular edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:271`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.getCircle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCircle(plane, fill, stroke, linewidth, lstyle, edge):
```

Get the SVG representation from a circular edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:303`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.get_ellipse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_ellipse(plane, fill, stroke, linewidth, lstyle, edge):
```

Get the SVG representation from an elliptical edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:309`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.getEllipse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getEllipse(plane, fill, stroke, linewidth, lstyle, edge):
```

Get the SVG representation from an elliptical edge. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:329`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.get_path`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_path(obj, plane, fill, pathdata, stroke, linewidth, lstyle, fill_opacity=None, edges=[], wires=[], pathname=None):
```

Get the SVG representation from an object's edges or wires.

TODO: the `edges` and `wires` must not default to empty list `[]`
but to `None`. Verify that the code doesn't break with this change.

`edges` and `wires` are mutually exclusive. If no `wires` are provided,
sort the `edges`, and use them. If `wires` are provided, sort the edges
in these `wires`, and use them.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:335`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgshapes.getPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPath(obj, plane, fill, pathdata, stroke, linewidth, lstyle, fill_opacity, edges=[], wires=[], pathname=None):
```

Get the SVG representation from a path. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgshapes.py:464`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.svgshapes._get_path_circ_ellipse`, `draftfunctions.svgshapes._get_path_bspline`. These are source internals unless an explicit export establishes otherwise.

