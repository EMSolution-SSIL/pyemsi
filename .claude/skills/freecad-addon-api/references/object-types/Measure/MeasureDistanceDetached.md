# `Measure::MeasureDistanceDetached`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Measure/App/MeasureDistance.cpp:527`. Abstract macro: no.

Native parent: [Measure::MeasureBase](../Measure/MeasureBase.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Measure::MeasureBase` -> `Measure.MeasureBase`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Distance` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Distance between the two elements | `src/Mod/Measure/App/MeasureDistance.cpp:531` |
| `DistanceX` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Distance in X-direction | `src/Mod/Measure/App/MeasureDistance.cpp:540` |
| `DistanceY` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Distance in Y-direction | `src/Mod/Measure/App/MeasureDistance.cpp:548` |
| `DistanceZ` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Distance in Z-direction | `src/Mod/Measure/App/MeasureDistance.cpp:556` |
| `Position1` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Position1 | `src/Mod/Measure/App/MeasureDistance.cpp:565` |
| `Position2` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Position2 | `src/Mod/Measure/App/MeasureDistance.cpp:566` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

