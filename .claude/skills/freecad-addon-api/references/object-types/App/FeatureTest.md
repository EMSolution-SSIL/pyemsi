# `App::FeatureTest`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/FeatureTest.cpp:68`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/App/FeatureTest.cpp:101` |
| `Bool` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/App/FeatureTest.cpp:80` |
| `BoolList` | `App::PropertyBoolList` | tuple[bool, ...] (source review) | bool \| int \| Iterable[bool \| int] \| dict[int, bool \| int] \| str (source review) | Not documented by registration | `src/App/FeatureTest.cpp:81` |
| `Colour` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/App/FeatureTest.cpp:95` |
| `ColourList` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Not documented by registration | `src/App/FeatureTest.cpp:96` |
| `ConstraintFloat` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/App/FeatureTest.cpp:90` |
| `ConstraintInt` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/App/FeatureTest.cpp:88` |
| `Distance` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Not documented by registration | `src/App/FeatureTest.cpp:100` |
| `Enum` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/App/FeatureTest.cpp:86` |
| `ExceptionType` | `App::PropertyInteger` | `int` | `int` | The type of exception the execution method throws | `src/App/FeatureTest.cpp:126` |
| `ExecCount` | `App::PropertyInteger` | `int` | `int` | Number of executions | `src/App/FeatureTest.cpp:131` |
| `ExecResult` | `App::PropertyString` | `str` | `str` | Result of the execution | `src/App/FeatureTest.cpp:125` |
| `Float` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/App/FeatureTest.cpp:79` |
| `FloatList` | `App::PropertyFloatList` | `list[float]` | `Sequence[float]` | Not documented by registration | `src/App/FeatureTest.cpp:104` |
| `Integer` | `App::PropertyInteger` | `int` | `int` | Not documented by registration | `src/App/FeatureTest.cpp:78` |
| `IntegerList` | `App::PropertyIntegerList` | `list[int]` | `Sequence[int]` | Not documented by registration | `src/App/FeatureTest.cpp:103` |
| `Link` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Not documented by registration | `src/App/FeatureTest.cpp:106` |
| `LinkList` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Not documented by registration | `src/App/FeatureTest.cpp:108` |
| `LinkSub` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Not documented by registration | `src/App/FeatureTest.cpp:107` |
| `LinkSubList` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Not documented by registration | `src/App/FeatureTest.cpp:109` |
| `Material` | `App::PropertyMaterial` | FreeCAD.Material (source review) | FreeCAD.Material \| _ColorInput (source review) | Not documented by registration | `src/App/FeatureTest.cpp:97` |
| `MaterialList` | `App::PropertyMaterialList` | tuple[FreeCAD.Material, ...] (source review) | FreeCAD.Material \| Iterable[FreeCAD.Material] \| dict[int, FreeCAD.Material] (source review) | Not documented by registration | `src/App/FeatureTest.cpp:98` |
| `Matrix` | `App::PropertyMatrix` | Base.Matrix (source review) | Base.Matrix \| tuple[float \| int, ...] (source review) | Not documented by registration | `src/App/FeatureTest.cpp:113` |
| `Path` | `App::PropertyPath` | str (source review) | str (source review) | Not documented by registration | `src/App/FeatureTest.cpp:83` |
| `Placement` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Not documented by registration | `src/App/FeatureTest.cpp:118` |
| `QuantityLength` | `App::PropertyQuantity` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Not documented by registration | `src/App/FeatureTest.cpp:165` |
| `QuantityOther` | `App::PropertyQuantity` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Not documented by registration | `src/App/FeatureTest.cpp:167` |
| `Source1` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Source for testing links | `src/App/FeatureTest.cpp:122` |
| `Source2` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Source for testing links | `src/App/FeatureTest.cpp:123` |
| `SourceN` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Source for testing links | `src/App/FeatureTest.cpp:124` |
| `String` | `App::PropertyString` | `str` | `str` | Not documented by registration | `src/App/FeatureTest.cpp:82` |
| `StringList` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Not documented by registration | `src/App/FeatureTest.cpp:84` |
| `TypeAll` | `App::PropertyInteger` | `int` | `int` | An example property which has the types 'Output', 'ReadOnly' and 'Hidden' | `src/App/FeatureTest.cpp:159` |
| `TypeHidden` | `App::PropertyInteger` | `int` | `int` | An example property which has the type 'Hidden' | `src/App/FeatureTest.cpp:134` |
| `TypeNoRecompute` | `App::PropertyInteger` | `int` | `int` | An example property which has the type 'NoRecompute' | `src/App/FeatureTest.cpp:154` |
| `TypeOutput` | `App::PropertyInteger` | `int` | `int` | An example property which has the type 'Output' | `src/App/FeatureTest.cpp:144` |
| `TypeReadOnly` | `App::PropertyInteger` | `int` | `int` | An example property which has the type 'ReadOnly' | `src/App/FeatureTest.cpp:139` |
| `TypeTransient` | `App::PropertyInteger` | `int` | `int` | An example property which has the type 'Transient' | `src/App/FeatureTest.cpp:149` |
| `Vector` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Not documented by registration | `src/App/FeatureTest.cpp:111` |
| `VectorList` | `App::PropertyVectorList` | `list[Base.Vector]` | `Sequence[_VectorInput]` | Not documented by registration | `src/App/FeatureTest.cpp:112` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

