# Conversion aliases

[Catalogue index](index.md)

Typing expressions from the existing property metadata; these are not runtime imports. Unqualified Base and DocumentObject refer to FreeCAD.Base and FreeCAD.DocumentObject.

```python
_DocumentObjectSubLinkPairInput = tuple[DocumentObject, str | Sequence[str]] | list[DocumentObject | str | Sequence[str]]
_DocumentObjectLink = DocumentObject | None
_DocumentObjectList = list[DocumentObject | None]
_DocumentObjectListInput = Sequence[DocumentObject]
_DocumentObjectSubLinkValue = tuple[DocumentObject, list[str]] | None
_DocumentObjectSubLinkInput = DocumentObject | None | _DocumentObjectSubLinkPairInput
_DocumentObjectSubLinkListItemInput = DocumentObject | _DocumentObjectSubLinkPairInput
_DocumentObjectSubLinkList = list[tuple[DocumentObject, tuple[str, ...]]]
_DocumentObjectSubLinkListInput = _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]
_XLinkListInput = _DocumentObjectListInput | _DocumentObjectSubLinkListInput
_XLinkListValue = _DocumentObjectList | _DocumentObjectSubLinkList
_QuantityInput = float | str | Base.Quantity | Base.Unit
_QuantityValueInput = float | str | Base.Quantity
_IntegerConstraintInput = int | dict[str, int] | tuple[int, int, int, int]
_FloatConstraintInput = float | int | dict[str, float] | tuple[float, float, float, float]
_VectorValue = Base.Vector
_VectorInput = Base.Vector | tuple[float, float, float]
_VectorList = list[Base.Vector]
_VectorListInput = Sequence[_VectorInput]
_StringList = list[str]
_StringListInput = Sequence[str]
_FloatList = list[float]
_FloatListInput = Sequence[float]
_IntegerList = list[int]
_IntegerListInput = Sequence[int]
_FileInput = str | bytes | IOBase
_FileIncludedInput = _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]
_ColorValue = tuple[float, float, float, float]
_ColorInput = int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]
_XLinkValue = DocumentObject | tuple[DocumentObject, str | list[str]] | None
_XLinkInput = DocumentObject | None | tuple[DocumentObject, str | Sequence[str]] | list[DocumentObject | str | Sequence[str]]
```
