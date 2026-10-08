# `SketcherGui::ViewProviderSketch`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:580`. Abstract macro: no.

Native parent: [PartGui::ViewProvider2DObject](../PartGui/ViewProvider2DObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartGui::ViewProviderPartExt` -> `PartGui.ViewProviderPartExt`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AutoColor` | `App::PropertyBool` | `bool` | `bool \| int` | If true, this sketch will be colored based on user preferences. Turn it off to set color explicitly. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:664` |
| `Autoconstraints` | `App::PropertyBool` | `bool` | `bool \| int` | Create auto constraints | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:601` |
| `AvoidRedundant` | `App::PropertyBool` | `bool` | `bool \| int` | Avoid redundant autoconstraint | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:606` |
| `EditingWorkbench` | `App::PropertyString` | `str` | `str` | Name of the workbench to activate when editing this sketch. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:653` |
| `ForceOrtho` | `App::PropertyBool` | `bool` | `bool \| int` | If true, camera type will be forced to orthographic view when entering editing mode. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:641` |
| `HideDependent` | `App::PropertyBool` | `bool` | `bool \| int` | If true, all objects that depend on the sketch are hidden when opening editing. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:617` |
| `RestoreCamera` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:635` |
| `SectionView` | `App::PropertyBool` | `bool` | `bool \| int` | If true, only objects (or part of) located behind the sketch plane are visible. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:647` |
| `ShowLinks` | `App::PropertyBool` | `bool` | `bool \| int` | If true, all objects used in links to external geometry are shown when opening sketch. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:623` |
| `ShowSupport` | `App::PropertyBool` | `bool` | `bool \| int` | If true, all objects this sketch is attached to are shown when opening sketch. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:629` |
| `TempoVis` | `App::PropertyPythonObject` | object (source review) | object (source review) | Object that handles hiding and showing other objects when entering/leaving sketch. | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:611` |
| `VisualLayerList` | `SketcherGui::PropertyVisualLayerList` | raises NotImplementedError (source review) | nonempty values raise NotImplementedError; no supported Python counterpart (source review) | Information about the Visual Representation of layers | `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:658` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

