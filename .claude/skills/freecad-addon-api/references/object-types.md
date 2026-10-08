# Document TypeIds and property discovery

Use this reference to resolve the string passed to `Document.addObject`, or when a runtime object has properties absent from generated stubs. Findings are source-backed for revision `3160daf1e2`; runtime probes below have not been executed in FreeCAD.

For the full source-discovered inventory, read the [native object/property catalogue](object-types/index.md). It lists document TypeIds, native inheritance, direct C++ property registrations and conversion metadata, and retains unresolved owners and discovery diagnostics. Other property owners such as extensions and view providers are marked separately.

The [conversion audit](object-types/conversion-review.md) traces every original missing-metadata property occurrence to its exact getter and setter implementations, including conditional VTK support and properties with no supported Python value. These source reviews supplement the skill; they do not silently fix the upstream metadata. The [wrapper audit](object-types/wrapper-review.md) records every missing direct association and routes to verified implementation context or discovered binding ancestors without promoting a native descendant into an invented Python class. Evidence hashes invalidate manual reviews when their source files change.

## Native identity differs from a Python wrapper

`doc.addObject("Part::Box", "Box")` creates a native document object. `Part::Box` is a registered C++ TypeId. It is neither a Python import path nor proof that a public `Part.Box` class exists.

Creation follows `DocumentPy::addObject` in `src/App/DocumentPyImp.cpp` into `Document::addObject` in `src/App/Document.cpp`. FreeCAD resolves the registered native type, checks derivation from `App::DocumentObject`, constructs it, adds it to the document, and returns `getPyObject()`. `src/Base/Type.cpp` implements module loading from the prefix before `::` for module types; this depends on that module being available in the running build.

Different native classes can share a Python wrapper. Check `obj.TypeId` and `obj.isDerivedFrom("Part::Feature")` for native identity/inheritance; `type(obj)` describes its Python wrapper. Keep both identities when reporting a discovered object type.

Examples of type selection:

| Native TypeId | Intended object |
| --- | --- |
| `App::FeaturePython` | Document object whose Python proxy can implement behavior; no Part shape output is implied. |
| `Part::Feature` | Part document feature with a `Shape` property. |
| `Part::FeaturePython` | Part feature with Python proxy behavior and a `Shape` property. |
| `Part::Box` | Built-in parametric box with length, width, height, inherited shape and placement, and attachment behavior. |

Sources: `src/App/FeaturePython.h`, `src/App/FeaturePython.cpp`, `src/Mod/Part/App/PartFeature.h`, `src/Mod/Part/App/PartFeature.cpp`, `src/Mod/Part/App/FeaturePartBox.h`, `.cpp`, and `PrimitiveFeature.cpp`. Use the addon lifecycle guide for proxy contracts.

## Resolve inherited and extension properties

For `Part::Box`, trace:

```text
Part::Box -> Part::Primitive -> Part::Feature -> App::GeoFeature -> App::DocumentObject
```

`FeaturePartBox.cpp` registers `Length`, `Width`, and `Height`; `FeaturePartBox.h` declares them as `App::PropertyLength`. `PartFeature.cpp` registers `Shape`; `GeoFeature.cpp` registers `Placement`; `DocumentObject.cpp` registers `Label`, `Label2`, `ExpressionEngine`, and `Visibility`. `PrimitiveFeature.cpp` initializes the attachment extension. Include parent and extension properties when answering which properties an object supports.

The wrapper path is also instructive: `Primitive::getPyObject()` constructs a hand-written `PrimitivePy` derived from `PartFeaturePy` in `PrimitiveFeature.cpp`. Box does not require a dedicated binding specification to expose its own properties. A search only for `Box.pyi` or a generated `Part.Box` misses this object.

Property inheritance merging is implemented in `PropertyData::merge` in `src/App/PropertyContainer.cpp`; `PropertyContainer::getPropertyList` combines native and dynamic instance properties. Extensions contribute additional behavior and properties. An addon can call `addProperty` at runtime, so a static class catalogue cannot describe every instance.

## Probe the running build

Run discovery in the target FreeCAD Python console or embedded runtime. Import the relevant module before querying `supportedTypes`, since the registry reflects loaded types. That method enumerates native descendants, including types that may be abstract; its list is not a promise that every entry can be instantiated. Sources: `DocumentPy::supportedTypes` in `src/App/DocumentPyImp.cpp` and abstract property/type registrations such as `Part::Primitive` in `PrimitiveFeature.cpp`.

```python
import FreeCAD as App
import Part

doc = App.activeDocument()
if doc is None:
    raise RuntimeError("Open a document for API inspection")

print(App.Version(), App.GuiUp)
print([name for name in doc.supportedTypes() if name.startswith("Part::")])
obj = doc.getObject("Box")  # Substitute the object's internal name.
if obj is None:
    raise RuntimeError("Inspection object not found")
print(obj.TypeId, type(obj), obj.isDerivedFrom("Part::Feature"))
for name in obj.PropertiesList:
    print(
        name,
        obj.getTypeIdOfProperty(name),
        obj.getGroupOfProperty(name),
        obj.getPropertyStatus(name),
        obj.getDocumentationOfProperty(name),
    )
```

`PropertiesList` is the authoritative available property-name list for that instance. `getTypeIdOfProperty(name)` returns the native property class; `getTypeOfProperty(name)` instead returns flags such as `Hidden` or `ReadOnly`. `getPropertyByName(name, checkOwner=0, /)` returns a value, not a property descriptor. Linked properties may belong to another container: `checkOwner=1` enforces ownership; `checkOwner=2` returns `(owner, propertyValue)`.

Sources: `src/App/PropertyContainer.pyi` and `PropertyContainerPyImp.cpp`; native `TypeId` and `isDerivedFrom` in `src/Base/BaseClass.pyi`.

To discover writable representations, combine the property TypeId with the applicable `PropertyPythonContracts.pyi`; validate uncertain conversions using the C++ setter. Avoid probing setters on a user's object just to infer a signature. Use a disposable document when an actual construction or assignment test is necessary, and close it after the test.

## Recording a missing type or property

For a new catalogue entry, record the native TypeId, native parent, returned Python wrapper when established, module/load requirement, property declarations, inherited/extension members, and source evidence. Separate a property's getter representation from accepted setter inputs. Record runtime results with the tested FreeCAD version/build rather than silently treating them as universal.

The initial generator investigation found many C++ properties without a mapped public wrapper owner or conversion contract. Treat these as unresolved reference coverage, not unsupported APIs. Prefer the runtime instance and source registrations when they disagree with a stub. Conversely, a native registration in source does not prove availability in every build: module compilation and initialization still matter.
