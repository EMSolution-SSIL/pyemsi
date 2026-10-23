# EMSolution Study Setup Plan

Date: 2026-10-02
Branch: `codex/study-setup-plan`
Status: implemented and verified on 2026-10-02

Build a Study setup workflow that supports separate 2D and 3D Studies in one document, with Parts and Groups selectable through dropdowns. Keep common behavior in one Study class and keep geometry handling separate from the task panel. This phase prepares and saves the setup; implementing new mesh generation comes later.

## Scope and decisions

- A Study represents one analysis setup. Its fixed and moving regions belong to the same Study.
- One `Study` class has a `Dimension` property, chosen when creating the Study. Separate Studies are separate instances, each with its own folders, assignments, IDs, settings, and result link.
- Use one New Study command with a name field and a 2D or 3D choice. Default to 3D to preserve the existing workflow. Treat dimension as fixed after creation in this phase; changing it could invalidate assignments.
- Movement choices are No movement and Sliding motion. Deformation is excluded.
- Both Parts and ordinary Groups are valid geometry sources in either dimension. Inspect the contents rather than choosing by workbench or container type.
- The Study panel owns overall setup and presents general mesh settings. Mesh Sizes presents local size assignments.
- Gmsh `.msh` is supported by EMSolution, as confirmed by the user. Do not add a format conversion requirement.
- Keep using FreeCAD properties, PySide widgets, existing transactions, and existing tests. Add no dependencies, abstract base classes, factories, Study2D/Study3D subclasses, or separate GUI frameworks.

## What the current code requires us to change

`objects.find_study()` returns the first Study in the document. `commands.active_study()` uses it for every command, and `FolderView` uses it even when another Study owns the selected folder. `NewStudy.IsActive()` prevents creating a second Study. These assumptions must be removed together before multiple Studies are exposed.

Study currently opens the ID table on double click. Folder watchers show panels on single selection. General mesh settings are stored and edited on `MeshSizesGroup`; the job writer reads those properties directly. Geometry selection accepts shape objects but excludes Parts and Groups, and export currently requires exactly one solid per object.

The existing output folder defaults to one document-wide directory containing `job.json` and geometry files. Multiple Studies must not accidentally overwrite each other's jobs or outputs. The runner already receives a specific Study and stores its result on that Study; keep that direct ownership.

## Study panel behavior

Selecting Study opens its setup panel using the existing task watcher pattern. Double click should keep that panel available instead of opening the ID dialog. An Edit IDs button opens the existing dialog for that Study.

```text
Motor cross-section Study
Dimension:       2D
Movement:        [ Sliding motion v ]

Fixed geometry:  [ Stator faces (Group) v ]
                 48 face regions included
Moving geometry: [ Rotor faces (Group) v ]
                 26 face regions included

[ Inspect geometry ]
Output folder:   ...
MSH version:     [ 4.1 v ]
Default size:    ...
[ Advanced mesh settings ]
[ Edit IDs ]
Mesh generation for this setup is planned for a later phase.
```

Use Main geometry when there is no movement, and Fixed geometry plus Moving geometry for sliding motion. The inactive moving selection stays saved when switching modes, but is excluded from the current setup. Parts and Groups appear in the same dropdown with their type shown. Identify them internally by document object Name, never by Label or dropdown index; labels can repeat or change.

One container per region is the initial shortcut. Users needing several containers can put them under an existing parent Group. A Manual selection option supports standalone geometry and bulk selection. Open its editor with `Gui.Control.showDialog`, following ItemPanel's existing OK/Cancel pattern: a selection watcher panel alone would disappear when users select geometry in the tree.

Inspect geometry lists the resolved contents and supports highlight. Container membership is live: reopening or refreshing the panel reflects Bodies or face objects added later. No geometry is copied. Show named errors for empty, missing, invalid, or conflicting sources. Clearing a deleted source must produce an empty setup, not a fallback to every document object.

Sliding-interface configuration and its dimensional rules belong to the later meshing phase. Show that requirement as explanatory text for now; do not create a selector that implies the interface is already supported.

## Architecture for maintainability

Keep persistent properties and ownership helpers in `objects.py`. Add Dimension, Movement, and geometry references to Study. For each region, use a source reference plus an explicit object list used only in Manual selection mode. Use global link properties for geometry in nested Parts, consistent with existing material and excitation references; verify the exact property types in the installed FreeCAD before implementing them. Do not persist Qt widgets, resolved content caches, or labels as identity.

Add one small `geometry.py` module for recursive collection, classification, and setup validation. Model and panel code both call it. Its functions return object references and named diagnostics without importing GUI modules. Keep the 2D and 3D differences in short classification helpers rather than scattering dimension checks through command handlers. If it needs global shape placement, move the existing `global_shape` helper there and update jobwriter/highlight/test callers; do not duplicate that logic.

Keep StudyView and a small Study watcher in `taskpanels.py`. Reuse MeshSettings, highlighting, and the existing watcher registration lifecycle. Avoid turning FolderWatcher into a general plugin registry. Rebuild candidate lists when opening or explicitly refreshing the panel; add no permanent document observer unless a demonstrated stale-state problem requires one.

Initially relocate the mesh settings UI while retaining their existing single storage location on `MeshSizesGroup`. StudyView passes that folder to MeshSettings. This avoids a property migration and keeps current export readers working. Explain this choice in the code; there must not be a second settings copy on Study. Revisit storage only when a later meshing change needs it.

## Implementation sequence

### 1 Make Study ownership explicit

Files: `objects.py`, `commands.py`, `taskpanels.py`, relevant existing tests.

- [x] Add a helper that lists Studies and an owner lookup for a Study, its folders, its items, and its result. Resolve ownership through actual Study/folder membership, not arbitrary geometry references.
- [x] Make FolderView obtain the selected folder's owner directly.
- [x] Allow New Study when a document exists, even if it already contains Studies. Canceling the creation dialog leaves no partial objects.
- [x] Define command targeting: a selected Study or its child establishes the active Study for that document; subsequent geometry selections retain that target. Show its name in the setup/editor UI. Use a small transient GUI mapping, clear or validate it on deletion/document closure, and keep it out of saved model properties.
- [x] With exactly one Study, retain the convenient automatic target. With several and no valid active target, ask the user to select a Study; never choose the first silently. Conflicting Study selections disable editing commands.
- [x] Capture the target once before opening a dialog so a later selection cannot redirect the operation.

Acceptance: editing Study B's folder or adding a material to B cannot modify Study A; switching documents cannot carry an invalid target across documents.

### 2 Add saved setup and container resolution

Files: `objects.py`, new `geometry.py`, `tests/test_study.py`.

- [x] Add the setup properties and defaults to new Studies. Preserve the stable `emsolution.objects.Study` proxy name.
- [x] Restore old Studies through an idempotent `onDocumentRestored` upgrade that only adds missing properties. Default old Studies to 3D, No movement, and their existing material-based geometry behavior. Preserve IDs, settings, links, output folders, and labels.
- [x] Traverse only container membership, with a visited set. Treat a PartDesign Body as its final shape; do not descend into its sketch and feature history.
- [x] For Part-workbench results, exclude inputs already consumed by a final modeling result in the selected source. Do not use visibility as the definition of final geometry. Cover a Boolean result plus its operands with a regression check; report ambiguous unsupported structures instead of silently meshing every Shape encountered.
- [x] In 3D, initially accept final objects with exactly one solid, matching the current support limit. In 2D, accept planar face objects without solids and verify that the selected regions share a plane in global coordinates. Do not extract every boundary face from a 3D solid, or convert wires/sketches into faces automatically.
- [x] Exclude Study objects and generated mesh results from candidates. Report unsupported links/assemblies rather than advertising unimplemented traversal.
- [x] Deduplicate references, preserve deterministic order, report wrong-dimension geometry, and detect objects assigned to both fixed and moving regions. Geometrical overlap detection remains a meshing concern.

Acceptance: a Group of planar faces and a Part of Bodies both resolve correctly; renaming keeps source links intact; adding a new member updates resolved contents; deleting a source never expands the selection unexpectedly.

### 3 Add the Study task panel

Files: `taskpanels.py`, `commands.py`, `InitGui.py`, `tests/gui_smoke.py`.

- [x] Add the creation dialog and Study watcher, reusing the current FreeCAD task panel lifecycle.
- [x] Add movement and geometry controls, type-labelled container dropdowns, counts, diagnostics, refresh, and inspect/highlight actions.
- [x] Implement bulk Manual selection in a persistent task dialog with Apply on OK and no writes on Cancel.
- [x] Add output folder, MSH version, default size, and Edit IDs controls. Move the existing general settings widget out of FolderView into StudyView; place advanced options behind an expandable section.
- [x] Every saved edit is an appropriate undo transaction. Populating widgets must not trigger writes or create undo entries.
- [x] Selecting a Body or a face must keep the existing workbench-switch behavior. Repeated activation must not duplicate watchers or observers; close/dispose panel widgets and temporary highlights correctly.

Acceptance: single-click Study shows setup; Mesh Sizes shows local assignments; changing Study B's general settings changes only B; inspecting geometry does not alter saved selection or object appearance.

### 4 Keep setup separate from unsupported export

Files: `commands.py`, `jobwriter.py` only where needed for guards/output ownership; `runner.py` only if needed for presentation. Do not change Gmsh algorithms or the job schema.

- [x] Clearly indicate that 2D generation, sliding-motion generation, and export based on the new geometry sources are deferred. Disable generation for these setups and enforce the same guard at the export entry point so direct calls cannot silently ignore the saved setup.
- [x] Preserve the existing 3D No movement material-based export for legacy Studies without explicit new geometry configuration. Do not present expected future EMSolution filenames as files already generated.
- [x] Give new Studies separate default output directories based on stable internal Study Names. Preserve old Studies' effective output paths during upgrade. Before a legacy run, reject another Study's identical effective output directory rather than silently sharing job/geometry files.
- [x] Materials, excitations, and local sizing retain existing 3D behavior. Do not advertise complete 2D assignment/ID semantics yet; show unavailable operations clearly for 2D Studies. Their dimensional mapping is part of the later meshing design.

Acceptance: saving a 2D or sliding setup works, but Run Mesh cannot run the existing 3D exporter on it. A legacy 3D Study still works, and separate Studies cannot overwrite one another's default files.

### 5 Verify the complete setup workflow

Extend the existing unittest and GUI smoke checks; add no test framework. Test behavior that can lose assignments or route edits incorrectly, rather than every widget/property getter.

- [x] Two Studies keep independent ownership, assignments, IDs, and settings through save/reopen in a fresh FreeCAD process.
- [x] Restore an old Study, run the upgrade twice, and confirm original settings/IDs/output paths and legacy export remain intact.
- [x] Check nested Groups/Parts, Body history, Boolean operands, duplicate labels, added/deleted members, empty and wrong-dimension sources, and a Body placed inside a transformed Part. Verify 2D coplanarity using global placement.
- [x] Exercise active-target selection, conflicting selections, document switching, deletion, undo/redo, and canceled dialogs in the GUI.
- [x] Exercise Study single-click, both dropdown types, manual multi-selection, highlighting, general settings relocation, Edit IDs, and workbench activation twice.
- [x] Verify unsupported export fails before files or IDs are changed; verify output isolation and the existing legacy mesh smoke workflow.

Run from the repository root with the installed FreeCAD Python, as the current tests require:

```powershell
$freecadPython = 'C:/Users/eskandarih/AppData/Local/Programs/FreeCAD 1.1/bin/python.exe'
& $freecadPython -m unittest tests.test_study -v
```

Run the existing `tests/gui_smoke.py` in a disposable FreeCAD profile using its documented launcher, with `Start-Process -WindowStyle Hidden`. Read its PASS/FAIL report; FreeCAD's process exit alone does not establish test success.

## Deferred work

Implement 2D/3D meshing, fixed/moving job generation, sliding-interface data, dimension-specific material/excitation/ID mapping, and filenames such as `pre_geom.msh` and `rotor_mesh.msh` in a separate meshing plan. Deformation, multi-source dropdown lists, automatic sketch filling, and assembly/link traversal remain outside this phase. Introduce subclasses or strategies only if actual implemented behavior makes the shared class difficult to maintain.

## Completion criteria

Multiple named Studies can be created, configured, saved, reopened, and edited independently. One consistent Study panel supports Parts, Groups, and bulk manual selection. Shared UI/model behavior has one implementation, dimension-specific selection has one clear home, old documents retain their settings, and unsupported meshing cannot ignore the setup. The implementation should land in the sequence above as small reviewable commits.


## Verification results

The installed FreeCAD 1.1.4 runtime passed all 43 Study tests, including restoration in a fresh process and preservation of older Study settings. The isolated GUI smoke test passed Study selection, Part and Group dropdowns, bulk selection, cancel, undo and redo, highlighting, settings isolation, document switching, deletion, repeated workbench activation, and the existing 3D mesh workflow. Git diff whitespace checks passed. New mesh generation remains deferred as described above.

## Follow-up: selected 3D geometry export (2026-10-06)

The setup phase was committed as `2249167`. The next change enables 3D No movement export from Part/Group and manual geometry selections. Selected geometry determines the included bodies and their IDs; material assignments supply each body's material. Missing materials identify the affected bodies before job files or IDs are changed. Conflicting materials on included bodies are rejected. Material, excitation, and local-size assignments outside the selected geometry are excluded from export.

New Studies start with geometry unassigned. Older Studies retain their saved selections and the legacy material-based workflow. Run Mesh stays enabled for supported 3D setups even when geometry or material validation needs attention, and the Study panel displays the validation message.

Volume physical groups use the sanitized body label alone (for example, `Body1`), without the material prefix. The ID table uses the same names. Material validation and numeric IDs are unchanged; excitation surfaces retain their excitation/body naming.

At the user's request, general Gmsh settings are back in the Mesh Sizes task panel, alongside local assignments. Advanced options are expanded by default. The Study panel retains geometry and output configuration; settings still have one storage location on each Study's Mesh Sizes folder.

All 65 Study and mesher tests passed in FreeCAD 1.1.4. The isolated GUI smoke test passed selected-geometry generation and missing-material diagnostics while the generation button remained enabled. The user's `Unnamed.FCStd` also generated MSH and UNV files from its saved Stator selection in a separate diagnostic output directory, without saving or changing the original document.

2D generation, sliding-motion interfaces, and separate fixed/moving mesh output remain deferred.

