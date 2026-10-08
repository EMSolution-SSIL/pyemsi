# `TechDraw::DrawViewSection`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewSection.cpp:143`. Abstract macro: no.

Native parent: [TechDraw::DrawViewPart](../TechDraw/DrawViewPart.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `TechDraw::DrawViewPart` -> `TechDraw.DrawViewPart`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BaseView` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | 2D View source for this Section | `src/Mod/TechDraw/App/DrawViewSection.cpp:160` |
| `CutSurfaceDisplay` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Appearance of Cut Surface | `src/Mod/TechDraw/App/DrawViewSection.cpp:207` |
| `FileGeomPattern` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | The PAT pattern file for geometric hatching | `src/Mod/TechDraw/App/DrawViewSection.cpp:217` |
| `FileHatchPattern` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | The hatch pattern file for the cut surface | `src/Mod/TechDraw/App/DrawViewSection.cpp:212` |
| `FuseBeforeCut` | `App::PropertyBool` | `bool` | `bool \| int` | Merge Source(s) into a single shape before cutting | `src/Mod/TechDraw/App/DrawViewSection.cpp:189` |
| `HatchOffset` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Hatch pattern offset | `src/Mod/TechDraw/App/DrawViewSection.cpp:244` |
| `HatchRotation` | `App::PropertyFloat` | `float` | `float` | Rotation of hatch pattern in degrees anti-clockwise | `src/Mod/TechDraw/App/DrawViewSection.cpp:239` |
| `HatchScale` | `App::PropertyFloat` | `float` | `float` | Hatch pattern size adjustment | `src/Mod/TechDraw/App/DrawViewSection.cpp:238` |
| `NameGeomPattern` | `App::PropertyString` | `str` | `str` | The pattern name for geometric hatching | `src/Mod/TechDraw/App/DrawViewSection.cpp:233` |
| `PatIncluded` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded Pat pattern file. System use only. | `src/Mod/TechDraw/App/DrawViewSection.cpp:228` |
| `SectionDirection` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Orientation of this Section in the Base View | `src/Mod/TechDraw/App/DrawViewSection.cpp:180` |
| `SectionLineStretch` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Adjusts the length of the section line.  1.0 is normal length.  1.1 would be 10% longer, 0.9 would be 10% shorter. | `src/Mod/TechDraw/App/DrawViewSection.cpp:246` |
| `SectionNormal` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Section Plane normal direction | `src/Mod/TechDraw/App/DrawViewSection.cpp:168` |
| `SectionOrigin` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Section Plane Origin | `src/Mod/TechDraw/App/DrawViewSection.cpp:174` |
| `SectionSymbol` | `App::PropertyString` | `str` | `str` | The identifier for this section | `src/Mod/TechDraw/App/DrawViewSection.cpp:155` |
| `SvgIncluded` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded Svg hatch file. System use only. | `src/Mod/TechDraw/App/DrawViewSection.cpp:223` |
| `TrimAfterCut` | `App::PropertyBool` | `bool` | `bool \| int` | Trim the resulting shape after the section cut | `src/Mod/TechDraw/App/DrawViewSection.cpp:194` |
| `UsePreviousCut` | `App::PropertyBool` | `bool` | `bool \| int` | Use the cut shape from the base view instead of the original object | `src/Mod/TechDraw/App/DrawViewSection.cpp:199` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

