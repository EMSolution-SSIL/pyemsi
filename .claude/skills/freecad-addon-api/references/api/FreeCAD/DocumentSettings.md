# `FreeCAD.DocumentSettings`

[Module](index.md)

```python
class DocumentSettings:
```

Namespaced document settings backed by the owning document's Meta map.

Namespaces may contain dot-separated identifier segments. Keys are single
identifiers within that namespace.

Evidence: public stub `FreeCAD/__init__.pyi` line 2085. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.DocumentSettings.getString`

```python
def getString(self, key: str, default: str='', /) -> str:
```

Return a string setting, or default when the key is missing.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2093.

## `FreeCAD.DocumentSettings.setString`

```python
def setString(self, key: str, value: str, /) -> None:
```

Store a string setting.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2099.

## `FreeCAD.DocumentSettings.getInt`

```python
def getInt(self, key: str, default: int=0, /) -> int:
```

Return an integer setting, or default when the key is missing or invalid.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2105.

## `FreeCAD.DocumentSettings.setInt`

```python
def setInt(self, key: str, value: int, /) -> None:
```

Store an integer setting.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2111.

## `FreeCAD.DocumentSettings.getFloat`

```python
def getFloat(self, key: str, default: float=0.0, /) -> float:
```

Return a float setting, or default when the key is missing or invalid.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2117.

## `FreeCAD.DocumentSettings.setFloat`

```python
def setFloat(self, key: str, value: float, /) -> None:
```

Store a float setting.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2123.

## `FreeCAD.DocumentSettings.getBool`

```python
def getBool(self, key: str, default: bool=False, /) -> bool:
```

Return a bool setting, or default when the key is missing or invalid.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2129.

## `FreeCAD.DocumentSettings.setBool`

```python
def setBool(self, key: str, value: bool, /) -> None:
```

Store a bool setting.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2135.

## `FreeCAD.DocumentSettings.remove`

```python
def remove(self, key: str, /) -> None:
```

Remove one setting from this namespace.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2141.

## `FreeCAD.DocumentSettings.keys`

```python
def keys(self) -> list[str]:
```

Return setting keys present in this namespace.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2147.

