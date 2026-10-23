# `Sketcher::SketchObjectSF`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Sketcher/App/SketchObjectSF.cpp:33`. Abstract macro: no.

Native parent: [Part::Part2DObject](../Part/Part2DObject.md). Read the parent record for inherited properties.

Direct binding association: `Sketcher.SketchObjectSF`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `SketchFlatFile` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | SketchFlat file (*.skf) which defines this sketch | `src/Mod/Sketcher/App/SketchObjectSF.cpp:37` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

