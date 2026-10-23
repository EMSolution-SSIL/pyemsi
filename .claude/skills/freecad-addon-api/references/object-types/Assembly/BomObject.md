# `Assembly::BomObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Assembly/App/BomObject.cpp:56`. Abstract macro: no.

Native parent: [Spreadsheet::Sheet](../Spreadsheet/Sheet.md). Read the parent record for inherited properties.

Direct binding association: `Assembly.BomObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `columnsNames` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | List of the columns of the Bill of Materials. | `src/Mod/Assembly/App/BomObject.cpp:61` |
| `detailParts` | `App::PropertyBool` | `bool` | `bool \| int` | Detail Parts sub-components. | `src/Mod/Assembly/App/BomObject.cpp:77` |
| `detailSubAssemblies` | `App::PropertyBool` | `bool` | `bool \| int` | Detail sub-assemblies components. | `src/Mod/Assembly/App/BomObject.cpp:69` |
| `onlyParts` | `App::PropertyBool` | `bool` | `bool \| int` | Only Part containers will be added. Solids like PartDesign Bodies will be ignored. | `src/Mod/Assembly/App/BomObject.cpp:85` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

