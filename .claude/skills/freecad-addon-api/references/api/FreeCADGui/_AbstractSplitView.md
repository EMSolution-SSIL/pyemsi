# `FreeCADGui._AbstractSplitView`

[Module](index.md)

```python
class _AbstractSplitView:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 694. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._AbstractSplitView.fitAll`

```python
def fitAll(self) -> None:
```

Fit all visible content into the active split view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 696.

## `FreeCADGui._AbstractSplitView.viewBottom`

```python
def viewBottom(self) -> None:
```

Orient the active split view to the bottom direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 700.

## `FreeCADGui._AbstractSplitView.viewFront`

```python
def viewFront(self) -> None:
```

Orient the active split view to the front direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 704.

## `FreeCADGui._AbstractSplitView.viewLeft`

```python
def viewLeft(self) -> None:
```

Orient the active split view to the left direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 708.

## `FreeCADGui._AbstractSplitView.viewRear`

```python
def viewRear(self) -> None:
```

Orient the active split view to the rear direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 712.

## `FreeCADGui._AbstractSplitView.viewRight`

```python
def viewRight(self) -> None:
```

Orient the active split view to the right direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 716.

## `FreeCADGui._AbstractSplitView.viewTop`

```python
def viewTop(self) -> None:
```

Orient the active split view to the top direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 720.

## `FreeCADGui._AbstractSplitView.viewAxometric`

```python
def viewAxometric(self) -> None:
```

Orient the active split view axometrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 724.

## `FreeCADGui._AbstractSplitView.viewIsometric`

```python
def viewIsometric(self) -> None:
```

Orient the active split view isometrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 728.

## `FreeCADGui._AbstractSplitView.getViewer`

```python
def getViewer(self, index: int, /) -> _View3DInventorViewer:
```

Return one contained viewer by index.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 732.

## `FreeCADGui._AbstractSplitView.close`

```python
def close(self) -> None:
```

Close the split-view container.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 736.

## `FreeCADGui._AbstractSplitView.cast_to_base`

```python
def cast_to_base(self) -> _MDIView:
```

Return the base MDI view wrapper for this split view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 740.

## `FreeCADGui._AbstractSplitView.__getitem__`

```python
def __getitem__(self, index: int, /) -> _View3DInventorViewer:
```

Return one contained viewer by index using sequence access.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 744.

## `FreeCADGui._AbstractSplitView.__len__`

```python
def __len__(self) -> int:
```

Return the number of contained 3D viewers.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 748.

