# `FreeCADGui.EditableDatumLabel`

[Module](index.md)

```python
class EditableDatumLabel:
```

Python wrapper for editable 3D datum labels.

This helper exposes the Gui-side editable datum label used by interactive
dimension and positioning workflows.

Evidence: public stub `FreeCADGui/__init__.pyi` line 1991. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.EditableDatumLabel.__init__`

```python
@overload
def __init__(self, viewer: Any, placement: Placement, color: Optional[Tuple[float, float, float]]=None, autoDistance: bool=False, avoidMouseCursor: bool=False) -> None:
```

Create an editable datum label attached to a 3D view.

viewer : Any
    A `Gui::View3DInventor` or `Gui::View3DInventorViewer` Python object.
placement : Placement
    Working placement used to position the label geometry.
color : tuple[float, float, float] | None
    Label RGB color. If `None`, the default datum label color is used.
autoDistance : bool
    If `True`, keep the label distance automatically adjusted relative to
    the current camera.
avoidMouseCursor : bool
    If `True`, bias automatic placement away from the mouse cursor.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2000.

## `FreeCADGui.EditableDatumLabel.activate`

```python
def activate(self) -> None:
```

Insert the label into the active 3D scene and start tracking camera changes.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2018.

## `FreeCADGui.EditableDatumLabel.deactivate`

```python
def deactivate(self) -> None:
```

Remove the label from the active 3D scene and stop any active editing session.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2024.

## `FreeCADGui.EditableDatumLabel.startEdit`

```python
def startEdit(self, value: float, eventFilter: Optional[Any]=None, visibleToMouse: bool=False) -> None:
```

Start in-place numeric editing for the current label.

value : float
    Initial numeric value shown by the editor.
eventFilter : Any | None
    Optional `QObject` used as an extra event filter for the embedded editor.
visibleToMouse : bool
    If `False`, the editor ignores mouse events and behaves as a keyboard-only
    overlay.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2030.

## `FreeCADGui.EditableDatumLabel.stopEdit`

```python
def stopEdit(self) -> None:
```

Stop the current edit session and keep the current displayed value.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2044.

## `FreeCADGui.EditableDatumLabel.isActive`

```python
def isActive(self) -> bool:
```

Return whether the label is currently attached to a viewer.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2050.

## `FreeCADGui.EditableDatumLabel.isInEdit`

```python
def isInEdit(self) -> bool:
```

Return whether the embedded spinbox editor is currently active.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2056.

## `FreeCADGui.EditableDatumLabel.getValue`

```python
def getValue(self) -> float:
```

Return the current numeric value tracked by the label.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2062.

## `FreeCADGui.EditableDatumLabel.setSpinboxValue`

```python
def setSpinboxValue(self, value: float, /) -> None:
```

Update the current numeric value and refresh the label text/editor state.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2068.

## `FreeCADGui.EditableDatumLabel.setPlacement`

```python
def setPlacement(self, placement: Placement, /) -> None:
```

Update the label placement used for 3D positioning.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2074.

## `FreeCADGui.EditableDatumLabel.setColor`

```python
def setColor(self, color: Optional[Tuple[float, float, float]], /) -> None:
```

Update the label color.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2080.

## `FreeCADGui.EditableDatumLabel.setPoints`

```python
def setPoints(self, p1: Vector, p2: Vector, /) -> None:
```

Set the label endpoints in the current placement coordinate system.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2086.

## `FreeCADGui.EditableDatumLabel.setFocus`

```python
def setFocus(self) -> None:
```

Request focus for the embedded editor widget when editing is active.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2092.

## `FreeCADGui.EditableDatumLabel.setFocusToSpinbox`

```python
def setFocusToSpinbox(self) -> None:
```

Explicitly move keyboard focus to the spinbox editor.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2098.

## `FreeCADGui.EditableDatumLabel.clearSelection`

```python
def clearSelection(self) -> None:
```

Clear any text selection inside the embedded spinbox editor.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2104.

## `FreeCADGui.EditableDatumLabel.setLabelType`

```python
def setLabelType(self, label_type: str, function: str='positioning', /) -> None:
```

Set the datum label type and its placement behavior.

label_type : str
    One of `angle`, `distance`, `distancex`, `distancey`, `radius`,
    `diameter`, `symmetric`, or `arclength`.
function : str
    One of `positioning`, `dimensioning`, or `forced`.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2110.

## `FreeCADGui.EditableDatumLabel.setLabelDistance`

```python
def setLabelDistance(self, distance: float, /) -> None:
```

Set the label offset distance from its measured geometry.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2122.

## `FreeCADGui.EditableDatumLabel.setLabelStartAngle`

```python
def setLabelStartAngle(self, angle: float, /) -> None:
```

Set the datum label start angle parameter.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2128.

## `FreeCADGui.EditableDatumLabel.setLabelRange`

```python
def setLabelRange(self, range: float, /) -> None:
```

Set the datum label angular/range parameter.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2134.

## `FreeCADGui.EditableDatumLabel.setLabelRecommendedDistance`

```python
def setLabelRecommendedDistance(self) -> None:
```

Recompute a camera-aware recommended label distance.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2140.

## `FreeCADGui.EditableDatumLabel.setLabelAutoDistanceReverse`

```python
def setLabelAutoDistanceReverse(self, enabled: bool, /) -> None:
```

Reverse the automatic label-distance direction when auto-distance is used.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2146.

## `FreeCADGui.EditableDatumLabel.setSpinboxVisibleToMouse`

```python
def setSpinboxVisibleToMouse(self, enabled: bool, /) -> None:
```

Control whether the embedded editor accepts mouse interaction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2152.

## `FreeCADGui.EditableDatumLabel.setLockedAppearance`

```python
def setLockedAppearance(self, locked: bool, /) -> None:
```

Toggle the visual "accepted/locked" appearance of the label.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2158.

## `FreeCADGui.EditableDatumLabel.resetLockedState`

```python
def resetLockedState(self) -> None:
```

Clear any accepted/locked editing state and restore normal appearance.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2164.

## `FreeCADGui.EditableDatumLabel.updateGeometry`

```python
def updateGeometry(self) -> None:
```

Recompute the label geometry and editor placement.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2170.

## `FreeCADGui.EditableDatumLabel.getFunction`

```python
def getFunction(self) -> str:
```

Return the current label function as `positioning`, `dimensioning`, or `forced`.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2176.

## `FreeCADGui.EditableDatumLabel.setValueChangedCallback`

```python
def setValueChangedCallback(self, callback: Optional[Callable[[float], object]], /) -> None:
```

Set a callback invoked whenever the current numeric value changes.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2182.

## `FreeCADGui.EditableDatumLabel.setEditingFinishedCallback`

```python
def setEditingFinishedCallback(self, callback: Optional[Callable[[float], object]], /) -> None:
```

Set a callback invoked when editing is accepted with Enter.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2188.

## `FreeCADGui.EditableDatumLabel.setEditingCanceledCallback`

```python
def setEditingCanceledCallback(self, callback: Optional[Callable[[float], object]], /) -> None:
```

Set a callback invoked when editing is canceled with Escape.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2194.

## `FreeCADGui.EditableDatumLabel.setParameterUnsetCallback`

```python
def setParameterUnsetCallback(self, callback: Optional[Callable[[], object]], /) -> None:
```

Set a callback invoked when the current editor input becomes unset/invalid.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2200.

## `FreeCADGui.EditableDatumLabel.setFinishEditingCallback`

```python
def setFinishEditingCallback(self, callback: Optional[Callable[[], object]], /) -> None:
```

Set a callback invoked for the "finish editing on all visible overlays" action.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2206.

