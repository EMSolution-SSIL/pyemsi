# `TechDraw::DrawGeomHatch`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawGeomHatch.cpp:74`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawGeomHatch`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `FilePattern` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | The crosshatch pattern file for this area | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:83` |
| `NamePattern` | `App::PropertyString` | `str` | `str` | The name of the pattern | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:87` |
| `PatIncluded` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded Pat hatch file. System use only. | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:85` |
| `PatternOffset` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Pattern offset | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:94` |
| `PatternRotation` | `App::PropertyFloat` | `float` | `float` | Pattern rotation in degrees anticlockwise | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:92` |
| `ScalePattern` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | GeomHatch pattern size adjustment | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:89` |
| `Source` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | The View + Face to be crosshatched | `src/Mod/TechDraw/App/DrawGeomHatch.cpp:80` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

