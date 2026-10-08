# `draftobjects.patharray.PathArray`

[Source module](index.md)

```python
class PathArray(DraftLink):
```

The Draft Path Array object.

The object distributes copies of an object along a path like a polyline,
spline, or bezier curve.

Attributes
----------
Align: bool
    It defaults to `False`.
    It sets whether the object will be specially aligned to the path.

AlignMode: str
    It defaults to `'Original'`.
    Indicates the type of alignment that will be calculated when
    `Align` is `True`.

    `'Original'` mode is the historic `'Align'` for old (v0.18) documents.
    It is not really the Fernat alignment. It uses the normal parameter
    from `getNormal` (or the default) as a constant, it does not calculate
    curve normal.
    `X` is curve tangent, `Y` is normal parameter, `Z` is the cross product
    `X` x `Y`.

    `'Tangent'` mode is similar to `Original`, but includes a pre-rotation
    (in execute) to align the `Base` object's `X` to `TangentVector`,
    then `X` follows curve tangent, normal input parameter
    is the Z component.

    If `ForceVertical` is `True`, the normal parameter from `getNormal`
    is ignored, and `X` is curve tangent, `Z` is `VerticalVector`,
    and `Y` is the cross product `X` x `Z`.

    `'Frenet'` mode orients the copies to a coordinate system
    along the path.
    `X` is tangent to curve, `Y` is curve normal, `Z` is curve binormal.
    If normal cannot be computed, for example, in a straight line,
    the default is used.

ForceVertical: bool
    It defaults to `False`.
    If it is `True`, and `AlignMode` is `'Original'` or `'Tangent'`,
    it will use the vector in `VerticalVector` as the `Z` axis.

StartOffset: float
    It defaults to 0.0.
    It is the length from the start of the path to the first copy.

EndOffset: float
    It defaults to 0.0.
    It is the length at the end of the path that will not be available
    for object placement.

ReversePath: bool
    It defaults to False.
    This will walk the path in reverse, also reversing object
    orientation. Start and end offsets will count from opposite ends
    of the path, etc.

SpacingMode: string
    It defaults to `'Fixed count'`.
    Objects can be spaced to divide the available length evenly
    (`'Fixed count'`, this is the original spacing mode from FreeCAD 1.0),
    or to be placed in given distances along the path from each other:
    `'Fixed spacing'` will keep placing objects for as long as there
    is still space available, while `'Fixed count and spacing'`
    will place a given number of objects (provided they fit in available
    space).

SpacingUnit: length
    It defaults to 20mm.
    When fixed spacing modes are used, this is the spacing distance
    used. If UseSpacingPattern is also enabled, this is the unit length
    of "1.0" in the spacing pattern (so, default pattern of [1.0, 2.0]
    with default SpacingUnit of 20mm means a spacing pattern of
    20mm, 40mm).

UseSpacingPattern: bool
    Default is False.
    Enables the SpacingPattern for uneven distribution of objects.
    Will have slightly different effect depending on SpacingMode.

SpacingPattern: float list
    Default is [1.0, 2.0]
    When UseSpacingPattern is True, this list contains the proportions
    of distances between consecutive object pairs. Can be used in any
    spacing mode. In "fixed spacing" modes SpacingPattern is multiplied
    by SpacingUnit. In flexible spacing modes ("fixed count"), spacing
    pattern defines the proportion of distances.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:88`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.patharray.PathArray.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:179`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.attach`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def attach(self, obj):
```

Set up the properties when the object is attached.

Note: we don't exactly know why the properties are added
in the `attach` method. They should probably be added in the `__init__`
method. Maybe this is related to the link behavior of this class.

For PathLinkArray, DraftLink.attach creates the link to the Base.

Realthunder: before the big merge, there was only the attach() method
in the view object proxy, not the object proxy.
I added that to allow the proxy to override the C++ view provider
type. The view provider type is normally determined by object's
C++ API getViewProviderName(), and cannot be overridden by the proxy.
I introduced the attach() method in proxy to allow the core
to attach the proxy before creating the C++ view provider.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:182`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, obj):
```

Set properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:202`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.set_general_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_general_properties(self, obj, properties):
```

Set general properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:216`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.set_align_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_align_properties(self, obj, properties):
```

Set general properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:274`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.set_spacing_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_spacing_properties(self, obj, properties):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:330`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.linkSetup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def linkSetup(self, obj):
```

Set up the object as a link object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:386`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Execute when the object is created or recomputed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:391`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.get_wires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_wires(self, path_object, subelements):
```

Get wires from the path object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:438`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.get_wire_from_subelements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_wire_from_subelements(self, subelements):
```

Make a wire from the path object subelements.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:450`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Execute when a property is changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:460`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.show_and_hide`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def show_and_hide(self, obj, prop):
```

Show and hide the properties depending on the touched property.

Note that when the array is created, some properties will change
more than once in a seemingly random order.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:465`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.PathArray.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:529`. Decorators are copied as source expressions and have not been executed.

