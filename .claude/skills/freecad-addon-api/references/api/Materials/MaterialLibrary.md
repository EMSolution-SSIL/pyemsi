# `Materials.MaterialLibrary`

[Module](index.md)

```python
class MaterialLibrary(BaseClass):
```

Material library.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 277. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.MaterialLibrary.Name`

```python
Name: str = ...
```

Name of the library

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 284.

## `Materials.MaterialLibrary.Icon`

```python
Icon: bytes = ...
```

Icon as an array of bytes.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 286.

## `Materials.MaterialLibrary.Directory`

```python
Directory: str = ...
```

Local directory where the library is located. For non-local libraries this will be empty

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 288.

## `Materials.MaterialLibrary.ReadOnly`

```python
ReadOnly: bool = ...
```

True if the library is local.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 290.

## `Materials.MaterialLibrary.Local`

```python
Local: bool = ...
```

True if the library is local.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 292.

