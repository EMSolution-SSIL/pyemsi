# `TechDraw.DrawPage`

[Module](index.md)

```python
class DrawPage(DocumentObject):
```

Feature for creating and manipulating Technical Drawing Pages

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 448. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawPage.KeepUpdated`

```python
@property
def KeepUpdated(self) -> bool:

@KeepUpdated.setter
def KeepUpdated(self, value: bool | int) -> None:
```

Keep page in sync with model

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 457, 462.

## `TechDraw.DrawPage.NextBalloonIndex`

```python
@property
def NextBalloonIndex(self) -> int:

@NextBalloonIndex.setter
def NextBalloonIndex(self, value: int) -> None:
```

Auto-numbering for Balloons

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 466, 471.

## `TechDraw.DrawPage.ProjectionType`

```python
@property
def ProjectionType(self) -> str:

@ProjectionType.setter
def ProjectionType(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 475, 479.

## `TechDraw.DrawPage.Scale`

```python
@property
def Scale(self) -> float:

@Scale.setter
def Scale(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Scale factor for this Page

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 483, 488.

## `TechDraw.DrawPage.Template`

```python
@property
def Template(self) -> DocumentObject | None:

@Template.setter
def Template(self, value: DocumentObject | None) -> None:
```

Attached Template

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 492, 497.

## `TechDraw.DrawPage.Views`

```python
@property
def Views(self) -> list[DocumentObject | None]:

@Views.setter
def Views(self, value: Sequence[DocumentObject]) -> None:
```

Attached Views

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 501, 506.

## `TechDraw.DrawPage.addView`

```python
def addView(self, view: DrawView, /) -> int:
```

addView(DrawView) - Add a View to this Page

Evidence: public stub `TechDraw/__init__.pyi` line(s) 509.

## `TechDraw.DrawPage.removeView`

```python
def removeView(self, view: DrawView, /) -> int:
```

removeView(DrawView) - Remove a View to this Page

Evidence: public stub `TechDraw/__init__.pyi` line(s) 513.

## `TechDraw.DrawPage.getViews`

```python
def getViews(self) -> Any:
```

getViews() - returns a list of all the views on page excluding Views inside Collections

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 517.

## `TechDraw.DrawPage.getAllViews`

```python
def getAllViews(self) -> Any:
```

getAllViews() - returns a list of all the views on page including Views inside Collections

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 521.

## `TechDraw.DrawPage.translateLabel`

```python
def translateLabel(self, context: str, base_name: str, unique_name: str, /) -> None:
```

translateLabel(translationContext, objectBaseName, objectUniqueName).
No return value.  Replace the current label with a translated version where possible.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 525.

## `TechDraw.DrawPage.requestPaint`

```python
def requestPaint(self) -> Any:
```

Ask the Gui to redraw this page

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 532.

## `TechDraw.DrawPage.PageWidth`

```python
PageWidth: Final[float]
```

Returns the width of this page

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 535.

## `TechDraw.DrawPage.PageHeight`

```python
PageHeight: Final[float]
```

Returns the height of this page

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 537.

## `TechDraw.DrawPage.PageOrientation`

```python
PageOrientation: Final[str]
```

Returns the orientation of this page

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 539.

