# Python source module `draftfunctions.svg`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/svg.py`. Import path is source-routed; installed availability is unverified.

Provides functions to return the SVG representation of various shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:32`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:36`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:37`.

### from draftfunctions import svgtext

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.svgtext` -> `draftfunctions.svgtext`.

[Source module `draftfunctions`](../index.md).

Evidence: `src/Mod/Draft/draftfunctions/svg.py:38`.

### from draftfunctions.svgshapes import get_proj, get_circle, get_path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.get_proj` -> `draftfunctions.svgshapes.get_proj`.

Bound source name `draftfunctions.svg.get_circle` -> `draftfunctions.svgshapes.get_circle`.

Bound source name `draftfunctions.svg.get_path` -> `draftfunctions.svgshapes.get_path`.

[Source module `draftfunctions.svgshapes`](../svgshapes/index.md).

Evidence: `src/Mod/Draft/draftfunctions/svg.py:39`.

### from draftobjects import layer

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.layer` -> `draftobjects.layer`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:42`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:43`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:44`.

### from draftutils.messages import _wrn, _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svg._wrn` -> `draftutils.messages._wrn`.

Bound source name `draftfunctions.svg._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:45`.

## `draftfunctions.svg.get_line_style`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_line_style(line_style, scale):
```

Return a linestyle scaled by a factor.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:55`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.getLineStyle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getLineStyle(linestyle, scale):
```

Return a Line style. DEPRECATED. Use get_line_style.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:85`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.get_pattern`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_pattern(pat):
```

Get an SVG pattern.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:91`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.getPattern`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPattern(pat):
```

Get an SVG pattern. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:100`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.get_arrow`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_arrow(obj, arrowtype, point, arrowsize, color, linewidth, angle=0):
```

Get the SVG representation from an arrow.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:106`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.getArrow`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getArrow(obj, arrowtype, point, arrowsize, color, linewidth, angle=0):
```

Get the SVG representation from an arrow. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:177`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.get_overshoot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_overshoot(point, shootsize, color, linewidth, angle=0):
```

Get the SVG representation of a dimension line overshoot.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:183`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.getOvershoot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getOvershoot(point, shootsize, color, linewidth, angle=0):
```

Get the SVG representation of a dimension line overshoot. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:199`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.format_point`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def format_point(coords, action='L'):
```

Return a string with a formatted point.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:205`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.get_svg`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_svg(obj, scale=1, linewidth=0.35, fontsize=12, fillstyle='shape color', direction=None, linestyle=None, color=None, linespacing=None, techdraw=False, rotation=0, fillspaces=False, override=True):
```

Return a string containing an SVG representation of the object.

Paramaeters
-----------
scale: float, optional
    It defaults to 1.
    It allows scaling line widths down, so they are resolution-independent.

linewidth: float, optional
    It defaults to 0.35.

fontsize: float, optional
    It defaults to 12, which is interpreted as `pt` unit (points).
    It is used if the given object contains any text.

fillstyle: str, optional
    It defaults to 'shape color'.

direction: Base::Vector3, optional
    It defaults to `None`.
    It is an arbitrary projection vector or a `WorkingPlane.PlaneBase`
    instance.

linestyle: optional
    It defaults to `None`.

color: optional
    It defaults to `None`.

linespacing: float, optional
    It defaults to `None`.

techdraw: bool, optional
    It defaults to `False`.
    If it is `True`, it sets some options for generating SVG strings
    for displaying inside TechDraw.

rotation: float, optional
    It defaults to 0.

fillspaces: bool, optional
    It defaults to `False`.

override: bool, optional
    It defaults to `True`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:388`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.get_print_color`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_print_color(obj):
```

Return the print color of the parent layer, if available.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:1233`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svg.getSVG`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSVG(obj, scale=1, linewidth=0.35, fontsize=12, fillstyle='shape color', direction=None, linestyle=None, color=None, linespacing=None, techdraw=False, rotation=0, fillSpaces=False, override=True):
```

Return SVG string of the object. DEPRECATED. Use 'get_svg'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svg.py:1244`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.svg._svg_shape`, `draftfunctions.svg._svg_dimension`, `draftfunctions.svg._get_view_object`. These are source internals unless an explicit export establishes otherwise.

