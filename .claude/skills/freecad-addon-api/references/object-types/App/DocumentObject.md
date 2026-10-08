# `App::DocumentObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/DocumentObject.cpp:59`. Abstract macro: no.

Native parent: `App::TransactionalObject` (outside this document/property-owner inventory).

Direct binding association: `FreeCAD.DocumentObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `ExpressionEngine` | `App::PropertyExpressionEngine` | `list[tuple[str, str \| None]]` | No setter declared | Property expressions | `src/App/DocumentObject.cpp:74` |
| `Label` | `App::PropertyString` | `str` | `str` | User name of the object (UTF8) | `src/App/DocumentObject.cpp:71` |
| `Label2` | `App::PropertyString` | `str` | `str` | User description of the object (UTF8) | `src/App/DocumentObject.cpp:72` |
| `Visibility` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/App/DocumentObject.cpp:76` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

