# `MatGui.MaterialTreeWidget`

[Module](index.md)

```python
class MaterialTreeWidget(BaseClass):
```

Material tree widget.

Evidence: public stub `MatGui/__init__.pyi` line 8. Inherited members are on the named base's reference; aliases keep their imported identity.

## `MatGui.MaterialTreeWidget.UUID`

```python
UUID: str = ...
```

Material UUID.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 12.

## `MatGui.MaterialTreeWidget.expanded`

```python
expanded: bool = ...
```

Expand material tree.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 14.

## `MatGui.MaterialTreeWidget.IncludeFavorites`

```python
IncludeFavorites: bool = ...
```

Include favorites in the material list.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 16.

## `MatGui.MaterialTreeWidget.IncludeRecent`

```python
IncludeRecent: bool = ...
```

Include recently used materials in the material list.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 18.

## `MatGui.MaterialTreeWidget.IncludeEmptyFolders`

```python
IncludeEmptyFolders: bool = ...
```

Include empty folders in the material list.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 20.

## `MatGui.MaterialTreeWidget.IncludeEmptyLibraries`

```python
IncludeEmptyLibraries: bool = ...
```

Include empty libraries in the material list.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 22.

## `MatGui.MaterialTreeWidget.IncludeLegacy`

```python
IncludeLegacy: bool = ...
```

Include legacy materials in the material list.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MatGui/__init__.pyi` line(s) 24.

## `MatGui.MaterialTreeWidget.setFilter`

```python
def setFilter(self, filter: MaterialFilter | list[MaterialFilter], /) -> None:
```

Set the material filter or list of filters.

Evidence: public stub `MatGui/__init__.pyi` line(s) 27.

## `MatGui.MaterialTreeWidget.selectFilter`

```python
def selectFilter(self, name: str, /) -> None:
```

Set the current material filter. Currently has no effect.

Evidence: public stub `MatGui/__init__.pyi` line(s) 33.

