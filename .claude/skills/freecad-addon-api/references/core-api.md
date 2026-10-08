# Core documents, values, and properties

Use this reference when creating document objects, updating parameters, or working with values and units. Public signatures come from the checked-out source at revision `3160daf1e2`; examples were checked against source, not executed in FreeCAD. Consult generated API references for full member lists and overloads.

## Documents and identity

```python
import FreeCAD as App

doc = App.activeDocument()
if doc is None:
    doc = App.newDocument("AddonExample")
```

`FreeCAD` is the public module; `App` is an import alias. `FreeCAD.Base` exposes value classes, also commonly reexported as `App.Vector`, `App.Rotation`, and `App.Placement`. C++ names containing `::` are native type identifiers, not Python import paths. Read [object-types.md](object-types.md) before choosing an `addObject` type.

| Public call | Purpose and relevant behavior |
| --- | --- |
| `App.newDocument(name=None, label=None, hidden=False, temp=False) -> Document` | Creates a document; internal name is made unique. `temp=True` marks it temporary so it is not saved. |
| `App.activeDocument() -> Document \| None` | Returns the current document; check for absence. |
| `App.getDocument(name, /) -> Document` | Retrieves an existing document; raises if it is absent. |
| `App.listDocuments(sort=False, /) -> dict[str, Document]` | Lists loaded documents by internal name. |
| `App.openDocument(name, hidden=False, temporary=False) -> Document` | Opens a project file. Non-file restore failures may leave a document open for recovery. |
| `doc.getObject(name_or_id, /) -> DocumentObject \| None` | Looks up an object by internal name or numeric ID. |
| `doc.getObjectsByLabel(label, /) -> list[DocumentObject]` | Labels can repeat; do not assume one result. |
| `doc.removeObject(object, /) -> None` | Removes an object by internal name or document object. |
| `doc.saveAs(path, /) -> None` / `doc.save() -> None` | Saves under a new path / current path. |

Sources: `src/App/FreeCAD.module.pyi`, `src/App/Document.pyi`, `src/App/DocumentPyImp.cpp`.

Use the object returned by `addObject`, then its `Name` when a call needs a name; the requested name may have been made unique. `Name` is internal identity, while `Label` is editable user-facing text. Keep an explicit document reference in commands that may change the active document.

## Transactions and recompute

Group one logical document edit in a transaction when implementing an undoable command. Recompute after changing feature inputs before consuming their derived geometry.

```python
import Part  # Registers Part types and makes the dependency explicit.

doc.openTransaction("Create addon box")
try:
    box = doc.addObject("Part::Box", "AddonBox")
    box.Label = "Addon box"
    box.Length = "20 mm"
    box.Width = "10 mm"
    box.Height = "5 mm"
    doc.recompute()
    if not box.isValid():
        raise RuntimeError(box.getStatusString())
except Exception:
    doc.abortTransaction()
    raise
else:
    doc.commitTransaction()
```

The example assumes this command owns the transaction. Integrate with the caller's transaction when one is already open. In this checkout, `doc.openTransaction(name)` delegates to application active-transaction handling; changes across multiple documents can receive a shared transaction ID. It is not a general nested transaction context manager.

Undo setup differs across versions. The installed FreeCAD 1.1.4 runtime needed `doc.UndoMode = 1` for the tested owned-document rollback case; the current checkout implements that setter as a no-op and reports mode 1. Consult [runtime validation](runtime-validation.md) and [version discrepancies](runtime-and-version.md) before applying target-version transaction setup. Do not copy that enable command as a universal requirement.

`doc.recompute(objs=None, force=False, check_cycle=False, /) -> int` returns the amount of recomputed features, not a success boolean. `obj.recompute(recursive=False, /) -> bool` is a different API. Use `obj.isValid()` and `obj.getStatusString()` to inspect a feature result; check that expected output geometry exists when the addon requires it.

`obj.touch()` forces a future recompute; `obj.touch("")` marks it touched without forcing recompute; `obj.touch("PropertyName")` touches that property. Use `obj.enforceRecompute()` when forcing execution is needed. `purgeTouched()` clears state and should not replace execution. The document's `RecomputesFrozen` flag disables automatic recomputes; account for the caller's state before changing it.

Sources: `src/App/Document.pyi`, `src/App/DocumentObject.pyi`, `src/App/DocumentPyImp.cpp`; box inputs and execution in `src/Mod/Part/App/FeaturePartBox.h` and `.cpp`.

## Value classes and units

| Public value | Common operations |
| --- | --- |
| `App.Base.Vector(x=0, y=0, z=0)` | Components, `Length`, `dot(vector)`, `cross(vector)`; `multiply(factor)` mutates this vector. |
| `App.Base.Rotation(axis, angle)` | Axis-angle construction uses degrees. Other overloads cover quaternions, direction alignment, and Euler conventions. `multVec(vector)` transforms a vector. |
| `App.Base.Placement(base, rotation)` | Combines translation and rotation; `multVec(vector)`, `multiply(placement)`, `inverse()`, `toMatrix()`. |
| `App.Base.Matrix` | Matrix values and transforms; inspect the required matrix/placement overload rather than treating them as interchangeable everywhere. |
| `App.Base.Quantity("20 mm")` | Parses a value with units; `.Value` is numeric in the internal system (mm, kg, s); `.Unit` holds dimensions. |
| `App.Units.parseQuantity(expression, /)` | Parses a unit expression into a quantity. `toNumber(...)` formats using the active schema and returns a string. |

Sources: `src/Base/Vector.pyi`, `Rotation.pyi`, `RotationPyImp.cpp`, `Placement.pyi`, `Matrix.pyi`, `Quantity.pyi`, `FreeCAD.Units.module.pyi`.

Use explicit unit strings for dimensioned user inputs. For a length property, a plain numeric assignment uses its internal unit. A quantity with incompatible dimensions raises a units mismatch error. Quantity constraint subclasses can clamp values, so inspect the value actually stored if limits matter. Display schemas affect formatting; avoid globally changing `App.Units.setSchema` just to display one value.

Property values can be copies. `PropertyPlacement`, `PropertyVector`, and `PropertyQuantity` getters construct fresh Python values. Reassign a modified value to invoke the document property's setter and change tracking:

```python
placement = box.Placement
placement.Base = App.Base.Vector(10, 0, 0)
box.Placement = placement
doc.recompute()
```

Sources: `src/App/PropertyGeo.cpp` (`PropertyPlacement::getPyObject`, `PropertyVector::getPyObject`), `src/App/PropertyUnits.cpp` (`PropertyQuantity::getPyObject`, `setPyObject`, `PropertyQuantityConstraint::setPyObject`).

## Dynamic properties and conversion contracts

`obj.addProperty(type, name, group="", doc="", attr=0, read_only=False, hidden=False, locked=False, enum_vals=None) -> DocumentObject` adds a property and returns the object. `type` is a native property TypeId such as `App::PropertyLength`, not `float` or `Quantity`. `removeProperty(name)` removes only user-defined properties.

```python
obj = doc.addObject("App::FeaturePython", "AddonParameters")
obj.addProperty("App::PropertyLength", "Thickness", "Parameters", "Wall thickness")
obj.Thickness = "2 mm"
obj.addProperty("App::PropertyEnumeration", "Mode", "Parameters")
obj.Mode = ["Solid", "Hollow"]  # Sets available choices.
obj.Mode = "Solid"              # Selects a choice.
doc.recompute()
```

This creates a parameter container, not a geometric feature implementation. Read the addon lifecycle guide when attaching a Python proxy with execution or restoration behavior.

Property getters and setters may use different Python representations:

| Native property TypeId | Getter representation | Setter inputs from conversion metadata |
| --- | --- | --- |
| `App::PropertyLength` | `Base.Quantity` through inherited conversion | Number, unit string, or `Base.Quantity` through quantity-constraint conversion |
| `App::PropertyPlacement` | `Base.Placement` | `Base.Placement` or `Base.Matrix` |
| `App::PropertyVector` | `Base.Vector` | `Base.Vector` or a three-float tuple |
| `App::PropertyEnumeration` | Selected choice as `str` | Choice string or `list[str]` to define choices |
| `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` |
| `App::PropertyLinkSub` | `(DocumentObject, list[str]) \| None` | Document object, `None`, or an object/subelement pair |
| `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | Single sublink or sequence of sublink inputs |
| `Part::PropertyPartShape` | `Part.Shape` | `Part.Shape` |

These contract files are generator inputs, not importable runtime APIs: `src/App/PropertyPythonContracts.pyi` and `src/Mod/Part/App/PropertyPythonContracts.pyi`. The property inheritance graph and conversions are C++ owned. Resolve inherited conversions in `PropertyUnits.cpp`, `PropertyGeo.cpp`, `PropertyLinks.cpp`, and `PropertyStandard.cpp` when an exact contract matters.

Metadata is not exhaustive: `PropertyEnumeration::setPyObject` also accepts an integer index, and its getter returns `None` for an invalid enumeration (`src/App/PropertyStandard.cpp`). Prefer strings for readable addon code. A missing contract or absent generated member does not prove the property is unavailable.

`setEditorMode(name, 1)` controls the property editor. `ReadOnly` and `Hidden` statuses describe editor behavior; they do not necessarily forbid Python assignment. `PropertyContainerPy::setCustomAttributes` checks `Immutable` before invoking the property setter (`src/App/PropertyContainerPyImp.cpp`). Check the actual property contract instead of treating every editor flag as Python write protection.

Use `obj.setExpression(name, expression, /)` for expression-driven properties; pass `None` or use `clearExpression(name)` to remove an expression. Account for expressions before assigning a value expected to remain fixed.

## Preferences and runtime boundaries

`App.ParamGet(path, /) -> ParameterGrp` returns an application preference group. Use the typed `GetBool`, `GetInt`, `GetString`, etc., with defaults, and their corresponding `Set...` methods; keep addon settings in its own subtree. Sources: `src/App/FreeCAD.module.pyi`, `src/Base/FreeCAD.ParameterGrp.pyi`.

`obj.ViewObject` is `None` when the GUI is unavailable. Application modeling code can run without `FreeCADGui`; guard GUI operations using `App.GuiUp` and the returned view provider. Consult the GUI reference for commands, selection, and presentation.
