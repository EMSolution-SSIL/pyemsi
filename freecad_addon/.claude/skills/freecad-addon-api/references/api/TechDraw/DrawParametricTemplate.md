# `TechDraw.DrawParametricTemplate`

[Module](index.md)

```python
class DrawParametricTemplate(DrawTemplate):
```

Feature for creating and manipulating Technical Drawing Templates

Author: Luke Parry (l.parry@warwick.ac.uk)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 542. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawParametricTemplate.Template`

```python
@property
def Template(self) -> str:

@Template.setter
def Template(self, value: str | dict[str, str]) -> None:
```

Template script

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 551, 556.

## `TechDraw.DrawParametricTemplate.drawLine`

```python
def drawLine(self, x1: float, y1: float, x2: float, y2: float, /) -> None:
```

Draw a line

Evidence: public stub `TechDraw/__init__.pyi` line(s) 559.

## `TechDraw.DrawParametricTemplate.GeometryCount`

```python
GeometryCount: Final[int]
```

Number of geometry in template

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 562.

