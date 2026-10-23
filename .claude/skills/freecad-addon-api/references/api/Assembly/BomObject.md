# `Assembly.BomObject`

[Module](index.md)

```python
class BomObject(Sheet):
```

This class is the BOM object of assemblies, it derives from Spreadsheet::Sheet.

Author: Ondsel (development@ondsel.com)
License: LGPL-2.1-or-later

Evidence: public stub `Assembly/__init__.pyi` line 199. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Assembly.BomObject.columnsNames`

```python
@property
def columnsNames(self) -> list[str]:

@columnsNames.setter
def columnsNames(self, value: Sequence[str]) -> None:
```

List of the columns of the Bill of Materials.

Access: getter and setter declared in the stub.

Evidence: public stub `Assembly/__init__.pyi` line(s) 208, 213.

## `Assembly.BomObject.detailParts`

```python
@property
def detailParts(self) -> bool:

@detailParts.setter
def detailParts(self, value: bool | int) -> None:
```

Detail Parts sub-components.

Access: getter and setter declared in the stub.

Evidence: public stub `Assembly/__init__.pyi` line(s) 217, 222.

## `Assembly.BomObject.detailSubAssemblies`

```python
@property
def detailSubAssemblies(self) -> bool:

@detailSubAssemblies.setter
def detailSubAssemblies(self, value: bool | int) -> None:
```

Detail sub-assemblies components.

Access: getter and setter declared in the stub.

Evidence: public stub `Assembly/__init__.pyi` line(s) 226, 231.

## `Assembly.BomObject.onlyParts`

```python
@property
def onlyParts(self) -> bool:

@onlyParts.setter
def onlyParts(self, value: bool | int) -> None:
```

Only Part containers will be added. Solids like PartDesign Bodies will be ignored.

Access: getter and setter declared in the stub.

Evidence: public stub `Assembly/__init__.pyi` line(s) 235, 240.

