# `TechDraw.DrawViewCollection`

[Module](index.md)

```python
class DrawViewCollection(DrawView):
```

Feature for creating and manipulating Technical Drawing View Collections

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1158. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewCollection.Views`

```python
@property
def Views(self) -> list[DocumentObject | None]:

@Views.setter
def Views(self, value: Sequence[DocumentObject]) -> None:
```

Collection Views

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1167, 1172.

## `TechDraw.DrawViewCollection.addView`

```python
def addView(self, view: DrawView, /) -> int:
```

addView(DrawView object) - Add a new View to this Group. Returns count of views.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1175.

## `TechDraw.DrawViewCollection.removeView`

```python
def removeView(self, view: DrawView, /) -> int:
```

removeView(DrawView object) - Remove specified Viewfrom this Group. Returns count of views in Group.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1179.

