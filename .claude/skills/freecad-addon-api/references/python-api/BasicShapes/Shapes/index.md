# Python source module `BasicShapes.Shapes`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BasicShapes/Shapes.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BasicShapes.Shapes.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BasicShapes/Shapes.py:31`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BasicShapes.Shapes.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BasicShapes/Shapes.py:32`.

## Classes

- [BasicShapes.Shapes.TubeFeature](TubeFeature.md)

## `BasicShapes.Shapes.makeTube`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeTube(outerRadius, innerRadius, height):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BasicShapes/Shapes.py:35`. Decorators are copied as source expressions and have not been executed.

## `BasicShapes.Shapes.addTube`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addTube(doc, name='Tube'):
```

addTube(document, [name]): adds a tube object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BasicShapes/Shapes.py:64`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BasicShapes.Shapes.__title__`, `BasicShapes.Shapes.__author__`, `BasicShapes.Shapes.__url__`, `BasicShapes.Shapes.__doc__`. These are source internals unless an explicit export establishes otherwise.

