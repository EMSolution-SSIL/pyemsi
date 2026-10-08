# GUI APIs and addon lifecycle contracts

Use this reference when building commands, workbenches, parametric Python objects,
view providers, or observers. Public APIs are methods the addon **calls**; callback
contracts are methods FreeCAD **calls on the addon**. A stub exposing `Proxy: object`
does not describe the latter. The tables below cover common callbacks, not the
entire extension surface. Evidence is this checkout's source; examples are
source-reviewed and have not been executed in a FreeCAD runtime.

Quick navigation: [environment](#choose-the-application-or-gui-environment-first),
[caller APIs](#apis-the-addon-calls), [feature proxies](#feature-proxies-model-callbacks),
[view providers](#view-provider-proxies-gui-callbacks),
[persistence](#save-and-restore-are-part-of-the-api-contract),
[commands/workbenches](#commands-and-workbenches),
[observers](#observers-callback-arguments-and-cleanup), [bootstrap](#bootstrap-layouts).

All `src/...` pointers below are relative to the FreeCAD repository root. Read the
named function at the indicated location when changing callback behavior.

## Choose the application or GUI environment first

```python
import FreeCAD as App

if App.GuiUp:
    import FreeCADGui as Gui
```

Model creation and feature recompute should work without importing GUI, Qt, or
Coin modules. Put GUI registration in GUI initialization. `App.GuiUp` is initially
`0` in `src/App/FreeCADInit.py:435` and becomes `1` in
`src/Gui/FreeCADGuiInit.py:543`. A successful import of `FreeCADGui` alone does not
establish that its document APIs exist in console mode.

`obj.ViewObject` can be `None`; it is not a model property. Its implementation
checks GUI module availability and requires the main thread when accessing the
GUI (`src/App/DocumentObjectPyImp.cpp:258`, `getViewObject`). App and GUI active
documents may be absent: check `App.ActiveDocument`/`Gui.activeDocument()` before
using them. Do not retain a GUI document or deleted document-object wrapper as a
permanent source of truth across document closure.

## APIs the addon calls

| API | Purpose and usage |
| --- | --- |
| `Gui.addCommand(name, instance, activation="")` | Register a Python command. Use a distinct internal name; its menu label comes from resources. Normal commands implement `Activated`; the optional activation string supplies an alternative command body. |
| `Gui.runCommand(name, index=0)` | Invoke a registered command. Check GUI, document, and command prerequisites. |
| `Gui.addWorkbench(instance_or_class)` | Register a workbench handler. Registration and initialization are separate. |
| `Gui.activateWorkbench(name)` | Activate the workbench by its registered internal name; returns success. |
| `Gui.activeWorkbench()`, `Gui.listWorkbenches()` | Inspect current/registered workbenches. |
| `Gui.activeDocument()`, `Gui.getDocument(doc)` | Obtain GUI documents, which provide active views and editing APIs. These differ from `App.Document`. |
| `Gui.Selection.getSelection()` | Read selected document objects. |
| `Gui.Selection.getSelectionEx(doc_name=None, resolve=1, single=False)` | Read extended selection records, preserving subelement names. `SelectionObject` carries `Object`, `SubElementNames`, `SubObjects`, and `PickedPoints`. |
| `Gui.Selection.addSelection(...)`, `removeSelection(...)`, `clearSelection(...)` | Change selection; observe the documented overloads and defaults. |
| `Gui.Selection.addObserver(observer, resolve=1)`, `removeObserver(observer)` | Subscribe/unsubscribe the same observer instance. |
| `App.addDocumentObserver(observer)`, `App.removeDocumentObserver(observer)` | Observe model-document/object events. |
| `Gui.addDocumentObserver(observer)`, `Gui.removeDocumentObserver(observer)` | Observe GUI-document/view-provider events. These callbacks receive GUI wrappers. |

Signatures and overloads: `src/Gui/FreeCADGui.module.pyi:355` (workbenches), `:439`
(commands), `:535` (documents), `:603` (observers);
`src/Gui/FreeCADGui.Selection.module.pyi:79` (selection mutation), `:202` (extended
selection), `:238` (observers); `src/Gui/Selection/SelectionObject.pyi:11`;
`src/App/FreeCAD.module.pyi:212` (application observers).

For subelement tools, use extended selection rather than reconstructing a face
from an object label. `resolve` affects link/mapped-element resolution; modes are
`NoResolve=0`, `OldStyleElement=1`, `NewStyleElement=2`, `FollowLink=3`
(`src/Gui/FreeCADGui.Selection.module.pyi:32`). Do not assume a saved `Face1` name
will identify the same topology after arbitrary shape changes.

## Feature proxies: model callbacks

Create a compatible scripted object, then assign `obj.Proxy = proxy`. For example,
`Part::FeaturePython` supplies a shape-bearing model with a Python proxy; an
`App::FeaturePython` does not automatically provide the same shape contract.

The following signatures are bound methods on an ordinary proxy instance. `self`
is omitted from the table. Implement only callbacks the addon needs.

| Callback | Trigger, arguments, and result |
| --- | --- |
| `execute(obj)` | Recompute the scripted feature. Update its computed properties here. Ordinary completion, including `None`, means handled. An actual boolean `False`, a missing callback, or `NotImplementedError` delegates to native feature execution. Other exceptions become a recompute error. |
| `mustExecute(obj)` | Additional recompute request when the feature is not already touched and native `mustExecute` did not request recompute. Return a truth value. Returning false cannot suppress recompute of a touched feature. |
| `onBeforeChange(obj, prop_name)` | Called before a named property changes. Return value is ignored. |
| `onChanged(obj, prop_name)` | Called after a named property changes. Return value is ignored. Do not assume all other properties are initialized yet. Guard dependent access and avoid recursive assignments to the same property. |
| `onDocumentRestored(obj)` | Model restoration callback; rebuild transient state or migrate missing/old properties. Return value is ignored. |
| `unsetupObject(obj)` | Called during object unsetup; release object-owned transient resources if needed. Return value is ignored. |
| `dumps()` / `loads(state)` | Persist/restore proxy state. These are serialization hooks on the proxy, not recompute callbacks. See persistence below. |

Dispatch: `src/App/FeaturePython.cpp:74` (`execute`), `:105` (`mustExecute`),
`:127` (`onBeforeChange`), `:186` (`onChanged`), `:216` (`onDocumentRestored`),
`:238` (`unsetupObject`). Native fallback and touched-object behavior:
`src/App/FeaturePython.h:198`. Callback discovery happens when `Proxy` changes
(`src/App/FeaturePython.h:440`); define methods on the class before attachment.

This table assumes the traditional proxy interface. Proxies with a `__object__`
attribute use alternate argument conventions for several callbacks; the dispatcher
detects attribute presence (`src/App/FeaturePython.cpp:60`). Do not accidentally add
that attribute to a traditional proxy. Specialized link, subobject, duplicate-label,
and partial-loading callbacks require inspecting the corresponding methods in
`src/App/FeaturePython.cpp` and the callback inventory in `src/App/FeaturePython.h:108`.

### Small model example

Save the class in an importable addon module such as `freecad.myaddon.feature`,
then call its factory. Keep an installed module path stable for saved documents.

```python
import FreeCAD as App
import Part


class Block:
    def __init__(self, obj):
        obj.addProperty("App::PropertyLength", "Size", "Block")
        obj.Size = 10
        obj.Proxy = self

    def execute(self, obj):
        size = obj.Size.Value
        if size <= 0:
            raise ValueError("Size must be positive")
        obj.Shape = Part.makeBox(size, size, size)

    def dumps(self):
        return None  # Model properties already hold the persistent state.

    def loads(self, state):
        pass


def create_block(doc):
    obj = doc.addObject("Part::FeaturePython", "AddonBlock")
    Block(obj)
    if App.GuiUp and obj.ViewObject is not None:
        obj.ViewObject.Proxy = 0  # Use native Part display; no custom scene graph.
    doc.recompute()
    return obj
```

`Proxy = 0` is the established native-display idiom used in
`src/Mod/TemplatePyMod/FeaturePython.py`; inspect that example alongside current
dispatcher code. Its comments calling every `execute` or `attach` implementation
mandatory overstate the native fallback behavior.

## View-provider proxies: GUI callbacks

Assign `obj.ViewObject.Proxy = view_proxy` only when the view provider exists.
The model proxy and view-provider proxy are separate objects. The document object
passed to `updateData` differs from the view-provider wrapper passed to `attach`
and `onChanged`.

| Callback | Trigger, arguments, and result |
| --- | --- |
| `attach(vobj)` | Attach GUI state to the view-provider wrapper after proxy assignment. Build transient scene nodes here; `vobj.Object` is the model. |
| `updateData(obj, prop_name)` | A property of the underlying model changes. |
| `onChanged(vobj, prop_name)` | A property of the view provider changes. |
| `getIcon()` | Supply a tree icon (file path or supported icon content). `None` permits native fallback. |
| `claimChildren()` | Return a sequence of document objects displayed as children in the tree. This is a presentation callback, not a substitute for model dependencies. |
| `getDisplayModes(vobj)` | Return additional mode names. The wrapper combines them with native modes. |
| `getDefaultDisplayMode()` | Return a default mode name; select a valid native or added mode. |
| `setDisplayMode(mode_name)` | Map a requested mode to a display-mode name; returns a string. It receives the mode name only. |
| `setEdit(vobj, mode)` / `unsetEdit(vobj, mode)` | Enter/leave editing. Return `True` for accepted or `False` for rejected. `None` or `NotImplementedError` delegates to native behavior. |
| `doubleClicked(vobj)` | Handle double click; return a boolean for accepted/rejected. Missing callback or `NotImplementedError` permits native fallback. |
| `setupContextMenu(vobj, menu)` | Customize the supplied Qt `QMenu`; the dispatcher interprets its return truth value. |
| `onDelete(vobj, subelements)` | Deletion permission; receives a tuple of selected subelement names. Return `True` to accept or `False` to reject. Missing callback or `NotImplementedError` delegates. Do not treat this callback as guaranteed final cleanup. |
| `beforeDelete(vobj)` | Cleanup callback before deletion; return value ignored. |
| `finishRestoring()` | Restore completion for a non-`None` proxy; rebuild transient GUI state as needed. No view-provider argument is passed. |
| `dumps()` / `loads(state)` | Persist/restore JSON-compatible proxy state; exclude Coin/Qt objects and live wrappers. |

Dispatch evidence: `src/Gui/ViewProviderFeaturePython.cpp:97` (icon), `:225`
(children), `:446`/`:488` (editing), `:583` (double click), `:615` (context menu),
`:651` (attach), `:677` (model property), `:710` (GUI property), `:776` (restore),
`:799` (before deletion), `:825` (delete permission), `:907`/`:930`/`:968`
(display modes). Native fallback/combination:
`src/Gui/ViewProviderFeaturePython.h:235`, `:377`, `:526`.

The `startRestoring` name appears in the callback inventory, but
`ViewProviderFeaturePythonImp::startRestoring()` is empty in this checkout
(`src/Gui/ViewProviderFeaturePython.cpp:776`); do not depend on it calling Python.
Several GUI callbacks also have alternate `__object__` conventions
(`src/Gui/ViewProviderFeaturePython.cpp:82`). Check each dispatcher; there is no
universal rule to add/remove `vobj` for every callback.

## Save and restore are part of the API contract

`src/App/PropertyPythonObject.cpp:238` uses JSON for proxy state. It chooses
`dumps()` first, then a custom legacy `__getstate__()`, then `__dict__`, then the
object itself. Restore similarly chooses `loads(state)`, legacy
`__setstate__(state)`, or dictionary replacement (`:290`). `dumps()` returns a
JSON-compatible **value**, not pre-encoded JSON text. Tuples round-trip as JSON
arrays; account for this in `loads`.

Save records the proxy module and class name (`:431`). Restore imports that module,
looks up the top-level class, and allocates it without calling `__init__` (`:463`).
Therefore initialize required restored attributes in `loads`, `onDocumentRestored`,
or GUI `attach`/`finishRestoring`, as appropriate. Do not persist a proxy class
defined only in a macro's `__main__`, a nested class, or a renamed module unless
you provide compatibility for existing documents.

Module import eligibility during restore is enforced in this checkout by
`isAllowedModule` (`src/App/PropertyPythonObject.cpp:89`), including recognized
module/macro directories and already-loaded modules. Installation/bootstrap and
importability matter; test reopening in a fresh FreeCAD process, not only the
process that created the object. A restore failure can leave the proxy as `None`.

Current examples: `src/Mod/Draft/draftobjects/base.py:78` (`onDocumentRestored`,
`dumps`, `loads`); `src/Mod/Draft/draftviewproviders/view_base.py:128` (omitting
nonserializable GUI state). These are implementation examples, not universal
requirements for every addon.

## Commands and workbenches

Normal command callbacks, implemented on the instance passed to `addCommand`:

| Callback | Contract |
| --- | --- |
| `GetResources()` | Returns a dictionary. Common string resources include `MenuText`, `ToolTip`, `Pixmap`, `Accel`, and `CmdType`. Registration reads resources. Specialized checkable/group commands have additional typed resources; do not assume every value is a string. |
| `Activated()` | Execute an ordinary command. Checkable commands instead receive an integer activation state. |
| `IsActive()` | Optional availability predicate. When absent, the command is active. When present, only an actual boolean `True` enables it; returning an object or integer does not. Exceptions disable it. |

Evidence: `src/Gui/Command.cpp:1454` (`PythonCommand`), `:1528` (`activated`),
`:1552` (`isActive`), `:1658` (checkable resource interpretation).

Subclass `Gui.Workbench`; its base supplies `GetClassName()` returning
`"Gui::PythonWorkbench"` and a no-op `ContextMenu`
(`src/Gui/FreeCADGuiInit.py:204`). `Initialize()` is called on first activation
after the C++ workbench wrapper is attached. Create commands, menus, and toolbars
there. `Activated()` and `Deactivated()` are optional callbacks on each successful
activation/switch; use them for workbench-scoped tools and observers. Repeatedly
registering observers in `Activated` without corresponding removal duplicates
notifications. `ContextMenu(recipient)` receives a string and can call
`appendContextMenu`. Workbench forwarding methods depend on the injected
`__Workbench__`; do not call `appendToolbar` in the constructor before activation.

Activation source: `src/Gui/Application.cpp:1862`; context menu dispatch: `:2195`.
Current lifecycle example: `src/Mod/Draft/InitGui.py:35`, `:164`, `:194`.

```python
# GUI initialization module; feature.py contains create_block above.
import FreeCAD as App
import FreeCADGui as Gui


class CreateBlockCommand:
    def GetResources(self):
        return {"MenuText": "Create block", "ToolTip": "Create a parametric block"}

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        from .feature import create_block
        doc = App.ActiveDocument
        if doc is not None:
            create_block(doc)


class MyWorkbench(Gui.Workbench):
    MenuText = "My addon"
    ToolTip = "Example addon tools"

    def Initialize(self):
        Gui.addCommand("MyAddon_CreateBlock", CreateBlockCommand())
        self.appendToolbar("My addon", ["MyAddon_CreateBlock"])
        self.appendMenu("My addon", ["MyAddon_CreateBlock"])


Gui.addWorkbench(MyWorkbench())
```

The relative import assumes an importable package GUI module. For legacy
`InitGui.py`, import the feature using its stable addon module name. Transaction
ownership should follow the calling command's `CmdType` and framework behavior;
do not add nested transactions blindly to an existing command implementation.

## Observers: callback arguments and cleanup

Implement only needed observer methods before registering the instance. Model
and GUI observer constructors cache available callbacks. Registries retain
instances; removal finds one matching registration. Duplicate registration is
not harmless (`src/App/DocumentObserverPython.cpp:42`,
`src/Gui/DocumentObserverPython.cpp:35`,
`src/Gui/Selection/SelectionObserverPython.cpp:224`). Retain the same instance,
register once, and remove it when the owning tool closes or workbench deactivates.
Use `try/finally` for short-lived operations; hook task-dialog and persistent-tool
closure for longer-lived subscriptions.

| Observer | Common callbacks, excluding `self` |
| --- | --- |
| Application document | `slotCreatedDocument(doc)`, `slotDeletedDocument(doc)`, `slotActivateDocument(doc)`, `slotCreatedObject(obj)`, `slotDeletedObject(obj)`, `slotBeforeChangeObject(obj, prop_name)`, `slotChangedObject(obj, prop_name)`, `slotRecomputedObject(obj)`, `slotBeforeRecomputeDocument(doc)`, `slotRecomputedDocument(doc)`, `slotStartSaveDocument(doc, filename)`, `slotFinishSaveDocument(doc, filename)` |
| GUI document | `slotCreatedDocument(gui_doc)`, `slotDeletedDocument(gui_doc)`, `slotActivateDocument(gui_doc)`, `slotCreatedObject(vobj)`, `slotDeletedObject(vobj)`, `slotChangedObject(vobj, prop_name)`, `slotInEdit(vobj)`, `slotResetEdit(vobj)` |
| Selection | `addSelection(doc_name, obj_name, sub_name, point_tuple)`, `removeSelection(doc_name, obj_name, sub_name)`, `setSelection(doc_name)`, `clearSelection(doc_name)`, `setPreselection(doc_name, obj_name, sub_name)`, `removePreselection(doc_name, obj_name, sub_name)`, `pickedListChanged()` |

Evidence: `src/App/DocumentObserverPython.cpp:68` (registration inventory), `:331`
(property names), `:522` (save callbacks); `src/Gui/DocumentObserverPython.cpp:60`
(inventory), `:194` (GUI properties);
`src/Gui/Selection/SelectionObserverPython.cpp:99` (selection dispatch).
Selection callbacks receive names rather than object wrappers; hover callbacks do
not receive the picked point even though `addSelection` does. Observe `resolve`
mode intentionally when dealing with links. Query current state for bulk changes
instead of assuming every notification supplies a complete selection snapshot.

```python
class SelectionTrace:
    def addSelection(self, doc_name, obj_name, sub_name, point):
        App.Console.PrintMessage(f"{doc_name}.{obj_name}:{sub_name}\n")


observer = SelectionTrace()
Gui.Selection.addObserver(observer)
try:
    # Perform a bounded operation that needs these notifications.
    Gui.Selection.clearSelection()
finally:
    Gui.Selection.removeObserver(observer)
```

For persistent tools, give the tool the `observer` reference and remove it in its
closure handler. App and GUI observer removal are separate APIs.

## Bootstrap layouts

| Layout | Application initialization | GUI initialization |
| --- | --- | --- |
| Legacy directory module | `Init.py` executed from discovered module directory; imports model/public modules | `InitGui.py` executed during GUI startup; register workbench handlers |
| Namespace package | Import `freecad.myaddon` (`__init__.py`), then optional `freecad.myaddon.init` | Import `freecad.myaddon.init_gui` during GUI startup |

Sources: `src/App/FreeCADInit.py:1062` (`ExtMod` namespace discovery), `:1105`
(package imports), `:1133`/`:1240` (`DirMod`/`Init.py`);
`src/Gui/FreeCADGuiInit.py:382`/`:392` (`DirModGui`/`InitGui.py`), `:455`/`:465`
(`ExtModGui`/`init_gui`). Metadata can select workbench subdirectories and supported
versions (`src/Gui/FreeCADGuiInit.py:419`); match the addon's established layout
and `package.xml`. Explicit imports are preferable to relying on names injected
into legacy initialization scope. Keep persistent model classes in ordinary
importable modules rather than in either bootstrap script.

## Validate a lifecycle change

For a model proxy, create and recompute, change a driving property, recompute,
save, then reopen in a fresh process and recompute again. Verify model behavior
with GUI unavailable if supported. For a GUI tool, activate/deactivate twice,
exercise selection and edit closure, close the document, and ensure subscriptions
are removed. These checks distinguish source-valid callback signatures from
working runtime lifecycle behavior. No runtime validation is implied by the
presence of this reference or by generated stubs.
