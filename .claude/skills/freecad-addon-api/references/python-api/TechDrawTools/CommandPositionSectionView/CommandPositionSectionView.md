# `TechDrawTools.CommandPositionSectionView.CommandPositionSectionView`

[Source module](index.md)

```python
class CommandPositionSectionView:
```

Orthogonally align a section view with its source view.

Evidence: `src/Mod/TechDraw/TechDrawTools/CommandPositionSectionView.py:42`. Source-defined class; runtime behavior and support status unverified.

## `TechDrawTools.CommandPositionSectionView.CommandPositionSectionView.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self):
```

Initialize variables for the command that must exist at all times.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/CommandPositionSectionView.py:45`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.CommandPositionSectionView.CommandPositionSectionView.GetResources`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def GetResources(self):
```

Return a dictionary with data that will be used by the button or menu item.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/CommandPositionSectionView.py:49`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.CommandPositionSectionView.CommandPositionSectionView.Activated`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def Activated(self):
```

Run the following code when the command is activated (button pressed).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/CommandPositionSectionView.py:57`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.CommandPositionSectionView.CommandPositionSectionView.IsActive`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def IsActive(self):
```

Return True when the command should be active or False when it should be disabled (greyed).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/CommandPositionSectionView.py:105`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.CommandPositionSectionView.CommandPositionSectionView.getTrianglePoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getTrianglePoint(self, p1, dir, p2):
```

Calculate the third vertex of a right triangle.

Parameters:
p1, p2 : vertices of the hypotenuse
dir    : direction vector of one leg (kathete)

Returns:
p3 : the third vertex completing the right triangle

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/CommandPositionSectionView.py:112`. Decorators are copied as source expressions and have not been executed.

