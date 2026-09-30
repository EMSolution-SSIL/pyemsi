# `Sketcher::SketchObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Sketcher/App/SketchObject.cpp:186`. Abstract macro: no.

Native parent: [Part::Part2DObject](../Part/Part2DObject.md). Read the parent record for inherited properties.

Direct binding association: `Sketcher.SketchObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `ArcFitTolerance` | `App::PropertyPrecision` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Tolerance for fitting arcs of projected external geometry | `src/Mod/Sketcher/App/SketchObject.cpp:220` |
| `Constraints` | `Sketcher::PropertyConstraintList` | `list[Sketcher.Constraint]` | `Sketcher.Constraint \| list[Sketcher.Constraint]` | Sketch constraints | `src/Mod/Sketcher/App/SketchObject.cpp:192` |
| `Exports` | `App::PropertyLinkListHidden` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Sketch export geometry | `src/Mod/Sketcher/App/SketchObject.cpp:212` |
| `ExternalGeo` | `Part::PropertyGeometryList` | `list[Part.Geometry]` | `Part.Geometry \| Sequence[Part.Geometry]` | Sketch external geometry | `src/Mod/Sketcher/App/SketchObject.cpp:216` |
| `ExternalGeometry` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Sketch external geometry | `src/Mod/Sketcher/App/SketchObject.cpp:197` |
| `ExternalTypes` | `App::PropertyIntegerList` | `list[int]` | `Sequence[int]` | Sketch external geometry type: 0 = projection, 1 = intersection, 2 = both. | `src/Mod/Sketcher/App/SketchObject.cpp:202` |
| `FullyConstrained` | `App::PropertyBool` | `bool` | `bool \| int` | Sketch is fully constrained | `src/Mod/Sketcher/App/SketchObject.cpp:207` |
| `Geometry` | `Part::PropertyGeometryList` | `list[Part.Geometry]` | `Part.Geometry \| Sequence[Part.Geometry]` | Sketch geometry | `src/Mod/Sketcher/App/SketchObject.cpp:190` |
| `InternalShape` | `Part::PropertyPartShape` | `Part.Shape` | `Part.Shape` | Not documented by registration | `src/Mod/Sketcher/App/SketchObject.cpp:225` |
| `MakeInternals` | `App::PropertyBool` | `bool` | `bool \| int` | Enables selection of closed profiles within a sketch as input for operations | `src/Mod/Sketcher/App/SketchObject.cpp:227` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

