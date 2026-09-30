# `FreeCAD.Material`

[Module](index.md)

```python
class Material:
```

App.Material class.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL
UserDocu: This is the Material class

Evidence: public stub `FreeCAD/__init__.pyi` line 2446. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Material.set`

```python
def set(self, string: str, /) -> None:
```

Set(string) -- Set the material.

The material must be one of the following values:
Brass, Bronze, Copper, Gold, Pewter, Plaster, Plastic, Silver, Steel, Stone, Shiny plastic,
Satin, Metalized, Neon GNC, Chrome, Aluminium, Obsidian, Neon PHC, Jade, Ruby or Emerald.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2455.

## `FreeCAD.Material.AmbientColor`

```python
AmbientColor: Any = ...
```

Ambient color

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2464.

## `FreeCAD.Material.DiffuseColor`

```python
DiffuseColor: Any = ...
```

Diffuse color

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2466.

## `FreeCAD.Material.EmissiveColor`

```python
EmissiveColor: Any = ...
```

Emissive color

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2468.

## `FreeCAD.Material.SpecularColor`

```python
SpecularColor: Any = ...
```

Specular color

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2470.

## `FreeCAD.Material.Shininess`

```python
Shininess: float = 0.0
```

Shininess

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2472.

## `FreeCAD.Material.Transparency`

```python
Transparency: float = 0.0
```

Transparency

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2474.

