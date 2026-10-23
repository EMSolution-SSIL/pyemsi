# Python source module `CompoundTools.Explode`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/CompoundTools/Explode.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `CompoundTools.Explode.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/CompoundTools/Explode.py:3`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `CompoundTools.Explode.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/CompoundTools/Explode.py:4`.

### from .CompoundFilter import makeCompoundFilter

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `CompoundTools.Explode.makeCompoundFilter` -> `CompoundTools.CompoundFilter.makeCompoundFilter`.

[Source module `CompoundTools.CompoundFilter`](../CompoundFilter/index.md).

Evidence: `src/Mod/Part/CompoundTools/Explode.py:6`.

## `CompoundTools.Explode.explodeCompound`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def explodeCompound(compound_obj, b_group=None):
```

explodeCompound(compound_obj, b_group = None): creates a bunch of compound filters, to extract every child of a compound into a separate object.
group: if True, Group is always made. If False, group is never made. If None, group is made if there is more than one child.
returns: (group_object, list_of_child_objects)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/CompoundTools/Explode.py:9`. Decorators are copied as source expressions and have not been executed.

