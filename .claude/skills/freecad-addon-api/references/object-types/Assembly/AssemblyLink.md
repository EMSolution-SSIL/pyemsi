# `Assembly::AssemblyLink`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Assembly/App/AssemblyLink.cpp:72`. Abstract macro: no.

Native parent: [App::Part](../App/Part.md). Read the parent record for inherited properties.

Direct binding association: `Assembly.AssemblyLink`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `LinkedObject` | `App::PropertyXLink` | `DocumentObject \| tuple[DocumentObject, str \| list[str]] \| None` | `DocumentObject \| None \| tuple[DocumentObject, str \| Sequence[str]] \| list[DocumentObject \| str \| Sequence[str]]` | The linked assembly. | `src/Mod/Assembly/App/AssemblyLink.cpp:85` |
| `Rigid` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Assembly/App/AssemblyLink.cpp:76` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

