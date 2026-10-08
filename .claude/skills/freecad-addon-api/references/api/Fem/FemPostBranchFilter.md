# `Fem.FemPostBranchFilter`

[Module](index.md)

```python
class FemPostBranchFilter(FemPostFilter):
```

The FemPostBranch class.

Author: Stefan Tröger (stefantroeger@gmx.net)
License: LGPL-2.1-or-later

Evidence: public stub `Fem/__init__.pyi` line 396. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Fem.FemPostBranchFilter.Output`

```python
@property
def Output(self) -> str:

@Output.setter
def Output(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `Fem/__init__.pyi` line(s) 405, 409.

## `Fem.FemPostBranchFilter.getFilter`

```python
def getFilter(self) -> Any:
```

Returns all filters, that this pipeline uses (non recursive, result does not contain branch child filters)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Fem/__init__.pyi` line(s) 412.

## `Fem.FemPostBranchFilter.recomputeChildren`

```python
def recomputeChildren(self) -> None:
```

Recomputes all children of the pipeline

Evidence: public stub `Fem/__init__.pyi` line(s) 416.

## `Fem.FemPostBranchFilter.getLastPostObject`

```python
def getLastPostObject(self) -> FemPostObject | None:
```

Get the last post-processing object

Evidence: public stub `Fem/__init__.pyi` line(s) 420.

## `Fem.FemPostBranchFilter.holdsPostObject`

```python
def holdsPostObject(self, obj: FemPostObject, /) -> bool:
```

Check if this pipeline holds a given post-processing object

Evidence: public stub `Fem/__init__.pyi` line(s) 424.

