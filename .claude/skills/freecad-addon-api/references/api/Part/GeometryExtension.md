# `Part.GeometryExtension`

[Module](index.md)

```python
class GeometryExtension:
```

The abstract class GeometryExtension enables to extend geometry objects with application specific data.
Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2707. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.GeometryExtension.Name`

```python
Name: str = ''
```

Sets/returns the name of this extension.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2713.

## `Part.GeometryExtension.copy`

```python
def copy(self) -> 'GeometryExtension':
```

Create a copy of this geometry extension.

Evidence: public stub `Part/__init__.pyi` line(s) 2716.

