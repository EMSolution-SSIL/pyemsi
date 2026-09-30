# `Gui::ViewProviderDocumentObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Gui/ViewProviderDocumentObject.cpp:62`. Abstract macro: no.

Native parent: `Gui::ViewProvider` (outside this document/property-owner inventory).

Direct binding association: `FreeCADGui.ViewProviderDocumentObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `DisplayMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set the display mode | `src/Gui/ViewProviderDocumentObject.cpp:69` |
| `OnTopWhenSelected` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Gui/ViewProviderDocumentObject.cpp:78` |
| `SelectionStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set the object selection style | `src/Gui/ViewProviderDocumentObject.cpp:73` |
| `ShowInTree` | `App::PropertyBool` | `bool` | `bool \| int` | Show the object in the tree view | `src/Gui/ViewProviderDocumentObject.cpp:71` |
| `Visibility` | `App::PropertyBool` | `bool` | `bool \| int` | Show the object in the 3d view | `src/Gui/ViewProviderDocumentObject.cpp:70` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

