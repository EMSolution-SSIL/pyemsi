# `PartDesign::SubShapeBinder`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/ShapeBinder.cpp:346`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BindCopyOnChange` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/PartDesign/App/ShapeBinder.cpp:419` |
| `BindMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/PartDesign/App/ShapeBinder.cpp:387` |
| `ClaimChildren` | `App::PropertyBool` | `bool` | `bool \| int` | Claim linked object as children | `src/Mod/PartDesign/App/ShapeBinder.cpp:385` |
| `Context` | `App::PropertyXLink` | `DocumentObject \| tuple[DocumentObject, str \| list[str]] \| None` | `DocumentObject \| None \| tuple[DocumentObject, str \| Sequence[str]] \| list[DocumentObject \| str \| Sequence[str]]` | Not documented by registration | `src/Mod/PartDesign/App/ShapeBinder.cpp:408` |
| `Fuse` | `App::PropertyBool` | `bool` | `bool \| int` | Fuse solids from bound shapes | `src/Mod/PartDesign/App/ShapeBinder.cpp:352` |
| `MakeFace` | `App::PropertyBool` | `bool` | `bool \| int` | Create face using wires from bound shapes | `src/Mod/PartDesign/App/ShapeBinder.cpp:353` |
| `Offset` | `App::PropertyFloat` | `float` | `float` | 2D offset face or wires, 0.0 = no offset | `src/Mod/PartDesign/App/ShapeBinder.cpp:354` |
| `OffsetFill` | `App::PropertyBool` | `bool` | `bool \| int` | True = make face between original wire and offset. | `src/Mod/PartDesign/App/ShapeBinder.cpp:364` |
| `OffsetIntersection` | `App::PropertyBool` | `bool` | `bool \| int` | False = offset child wires independently. | `src/Mod/PartDesign/App/ShapeBinder.cpp:378` |
| `OffsetJoinType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Arcs, Tangent, Intersection | `src/Mod/PartDesign/App/ShapeBinder.cpp:361` |
| `OffsetOpenResult` | `App::PropertyBool` | `bool` | `bool \| int` | False = make closed offset from open wire. | `src/Mod/PartDesign/App/ShapeBinder.cpp:371` |
| `PartialLoad` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/App/ShapeBinder.cpp:396` |
| `Refine` | `App::PropertyBool` | `bool` | `bool \| int` | Refine shape (clean up redundant edges) after adding/subtracting | `src/Mod/PartDesign/App/ShapeBinder.cpp:433` |
| `Relative` | `App::PropertyBool` | `bool` | `bool \| int` | Enable relative sub-object binding | `src/Mod/PartDesign/App/ShapeBinder.cpp:386` |
| `Support` | `App::PropertyXLinkSubList` | list[tuple[FreeCAD.DocumentObject, tuple[str, ...]]] (source review) | PropertyLinkSub input or list/tuple of PropertyLinkSub inputs (source review) | Support of the geometry | `src/Mod/PartDesign/App/ShapeBinder.cpp:350` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

