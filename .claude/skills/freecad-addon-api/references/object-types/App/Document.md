# `App::Document`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/App/Document.cpp:143`. Abstract macro: no.

Native parent: `App::PropertyContainer` (outside this document/property-owner inventory).

Direct binding association: `FreeCAD.Document`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Comment` | `App::PropertyString` | `str` | `str` | Additional tag to save a comment | `src/App/Document.cpp:1000` |
| `Company` | `App::PropertyString` | `str` | `str` | Additional tag to save the name of the company | `src/App/Document.cpp:987` |
| `CreatedBy` | `App::PropertyString` | `str` | `str` | The creator of the document | `src/App/Document.cpp:979` |
| `CreationDate` | `App::PropertyString` | `str` | `str` | Date of creation | `src/App/Document.cpp:980` |
| `FileName` | `App::PropertyString` | `str` | `str` | The path to the file where the document is saved to | `src/App/Document.cpp:974` |
| `Id` | `App::PropertyString` | `str` | `str` | ID of the document | `src/App/Document.cpp:1005` |
| `Label` | `App::PropertyString` | `str` | `str` | The name of the document | `src/App/Document.cpp:973` |
| `LastModifiedBy` | `App::PropertyString` | `str` | `str` | Not documented by registration | `src/App/Document.cpp:985` |
| `LastModifiedDate` | `App::PropertyString` | `str` | `str` | Date of last modification | `src/App/Document.cpp:986` |
| `License` | `App::PropertyString` | `str` | `str` | License string of the Item | `src/App/Document.cpp:1019` |
| `LicenseURL` | `App::PropertyString` | `str` | `str` | URL to the license text/contract | `src/App/Document.cpp:1020` |
| `Material` | `App::PropertyMap` | `dict[str, str]` | `dict[str, str]` | Map with material properties | `src/App/Document.cpp:1002` |
| `Meta` | `App::PropertyMap` | `dict[str, str]` | `dict[str, str]` | Map with additional meta information | `src/App/Document.cpp:1001` |
| `ShowHidden` | `App::PropertyBool` | `bool` | `bool \| int` | Whether to show hidden object items in the tree view | `src/App/Document.cpp:1025` |
| `Tip` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Link of the tip object of the document | `src/App/Document.cpp:1042` |
| `TipName` | `App::PropertyString` | `str` | `str` | Link of the tip object of the document | `src/App/Document.cpp:1047` |
| `TransientDir` | `App::PropertyString` | `str` | `str` | Transient directory, where the files live while the document is open | `src/App/Document.cpp:1037` |
| `Uid` | `App::PropertyUUID` | `str` | `str` | UUID of the document | `src/App/Document.cpp:1006` |
| `UnitSystem` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Unit system to use in this project | `src/App/Document.cpp:992` |
| `UseHasher` | `App::PropertyBool` | `bool` | `bool \| int` | Whether to use hasher on topological naming | `src/App/Document.cpp:1030` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

