# `Path::FeatureArea`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/CAM/App/FeatureArea.cpp:41`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Direct binding association: `CAM.FeatureArea`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Sources` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Not documented by registration | `src/Mod/CAM/App/FeatureArea.cpp:48` |
| `WorkPlane` | `Part::PropertyPartShape` | `Part.Shape` | `Part.Shape` | Not documented by registration | `src/Mod/CAM/App/FeatureArea.cpp:49` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

