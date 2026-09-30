# `TechDraw.DrawSVGTemplate`

[Module](index.md)

```python
class DrawSVGTemplate(DrawTemplate):
```

Feature for creating and manipulating Technical Drawing SVG Templates

Author: Luke Parry (l.parry@warwick.ac.uk)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 738. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawSVGTemplate.PageResult`

```python
@property
def PageResult(self) -> str:

@PageResult.setter
def PageResult(self, value: _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]) -> None:
```

Embedded SVG code for template. For system use.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 747, 752.

## `TechDraw.DrawSVGTemplate.Template`

```python
@property
def Template(self) -> str:

@Template.setter
def Template(self, value: str | dict[str, str]) -> None:
```

Template file name.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 756, 761.

## `TechDraw.DrawSVGTemplate.getEditFieldContent`

```python
def getEditFieldContent(self, edit_field_name: str, /) -> str | None:
```

getEditFieldContent(EditFieldName) - returns the content of a specific Editable Text Field

Evidence: public stub `TechDraw/__init__.pyi` line(s) 764.

## `TechDraw.DrawSVGTemplate.setEditFieldContent`

```python
def setEditFieldContent(self, edit_field_name: str, new_content: str, /) -> None:
```

setEditFieldContent(EditFieldName, NewContent) - sets a specific Editable Text Field to a new value

Evidence: public stub `TechDraw/__init__.pyi` line(s) 768.

## `TechDraw.DrawSVGTemplate.translateLabel`

```python
def translateLabel(self, context: str, base_name: str, unique_name: str, /) -> None:
```

translateLabel(translationContext, objectBaseName, objectUniqueName).
No return value.  Replace the current label with a translated version where possible.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 772.

