# Material task panel and named Materials

## Why

Today a Material is created and edited through a small modal pop-up (`AssignDialog` in `taskpanels.py`): a material
drop-down and a POTENTIAL box. That is out of step with the rest of the Study tree, where Excitations, Mesh Sizes and
the other items open a task panel (`ItemPanel`) with a name, settings and an editable pick list.

The two kinds of Material also behave differently:

- **Whole-body Material** (normal Study): no name is asked; the tree label is generated as `<body>: <material>`
  (`assignment_label`, kept up to date by `sync_labels`). The Gmsh physical group name and MAT_NAME come from the
  *body's* label (`volume_name(body)`).
- **Piece Material** (symmetric Study, faces of the drawing): a separate text pop-up asks for a name (default
  `Pieces`) before the material pop-up. The Gmsh group name and MAT_NAME come from that name (`volume_name(m)`).
- Neither kind can change *what* it covers after creation.

The goal is one consistent Material item: named by the user, edited in a task panel like the other items, with its
selection editable, and its name used in the mesh and the input file.

## Goals

1. Every Material (whole-body, Air Region, symmetric pieces) has a user-given name. No more generated
   `<body>: <material>` labels.
2. Assign Material and double-clicking a Material (in the tree or in the Materials folder panel) open a **task panel**,
   not a modal dialog.
3. The panel lets the user edit the selection: Add selection / Remove, with 3D highlight of the selected rows, for both
   whole-body and symmetric Materials.
4. The Material's name is the Gmsh physical group name and MAT_NAME (an Air Region's Material is named after the
   Air Region, so the result there is unchanged).
5. A sensible name is suggested from the selection.
6. Taking a body (or face) that already belongs to another Material asks for confirmation first.

## Non-goals

- Changing how many bodies a whole-body Material holds. The data model stays as it is: a whole-body Material links one
  body (`Body`), a piece Material holds faces (`Pieces`). The user asked to leave this question aside.
- MAT_ID allocation, the ID table, the Material Library, and the Materials folder table columns stay as they are.
- Excitation surface group names (`item_name`) are unchanged.

## Anti-goals

- Existing studies must not get different mesh group names or MAT_NAMEs just by being opened. (See Old files.)
- No second pop-up before the panel (the symmetric name prompt goes away).

## The panel

A `MaterialPanel`, built like `ItemPanel` (same layout style, same `ItemGate` selection gate while it is open,
`highlight` of selected list rows, `close()` removing gate and highlight, `autoClosedOnDeletedDocument`).

Fields, top to bottom:

- `Study: <label>` line and a one-line hint, as in `ItemPanel`. Hint for whole bodies: click a solid (3D) or region
  (2D), or select it in the tree; Air Regions can be picked in the tree. Hint for symmetric Studies: click faces of the
  drawing.
- **Name**: line edit.
- **Material**: combo of the Study's Material Library entries. No `— none —` entry; removing a Material is done by
  deleting the item. If the library is empty, the existing note ("The Material Library is empty: import materials from
  its folder first.") is shown and OK refuses.
- **POTENTIAL**: spin box 0..1000000, as today.
- **List** of what the Material covers: bodies / Air Regions for a whole-body Material, `Drawing.FaceN` entries for a
  piece Material. Extended selection; Add selection and Remove buttons.
- A **note** label under the list, hidden when empty, for pending side-effects (see Moving).

What can be picked:

- Normal Study: what `objects.assignable(study)` returns (main/moving geometry bodies and Air Regions), refused with
  `assignment_problem` messages as today. Tops of Symmetric Mesh items are refused with the existing message
  "Materials go on the faces (pieces) of <top>: select faces first."
- Symmetric Study: faces of a Symmetric Mesh top, as `AssignMaterial.Activated` picks them today.

Whole-body Materials link one body. In the panel, Add selection with one body replaces the one in the list; with
several bodies selected it warns "A Material holds one body: select one, or use Assign Material with several bodies
selected to give each its own Material."

### Several bodies at once (user's decision)

When Assign Material runs with **more than one** body / Air Region selected in a normal Study, or the Materials
folder's **Assign…** button runs with several rows selected, no panel opens. A small dialog asks for the library
material and POTENTIAL once (no name field), then makes one Material per body, each named by the suggestion rule
(its body's name, `_2`... on a clash). Bodies that already have a Material get the confirmation box from Moving
first; Cancel there skips them. One undo step. Each Material can then be renamed in its own panel.

OK / Cancel:

- New Material: created inside an open transaction when the panel opens (as `ItemPanel` does with `new=True`); OK
  commits, Cancel aborts it. OK with an empty list, an empty name or no material warns and keeps the panel open.
- Existing Material: OK opens one transaction "Edit <name>" that applies name, material, POTENTIAL, the selection and
  any moves; Cancel changes nothing.
- One undo step either way.

## Naming

- The Material gets a `GroupName` string property, like Excitations, holding the name exactly as typed.
  `display_name(m)` already prefers `GroupName`.
- **Tree label** (user's decision): `Label` is `<name>: <material>` (e.g. `Coil: Copper`), for whole-body and
  piece Materials alike, so it does not clash with the body's own label (FreeCAD keeps labels unique and would show
  `Coil001`). The user only types the name. `assignment_label` / `sync_labels` stay, rewritten to build the label from
  `GroupName` and the library material, so renaming a library material still updates the tree. Renaming a body no
  longer changes anything.
- **Mesh and input file**: the volume name of a body with a Material is `clean(display_name(material))`. A body
  **without** a Material keeps today's name (its label) so meshing without materials still works. This touches
  `volume_name` callers in `jobwriter.py`, `key_name` (also used by `studymaterials.study_material_rows` for MAT_NAME
  and by the ID table panel), and `validation._names`.
- **Air Regions** (user's decision): an Air Region keeps its own typed name as the mesh name and MAT_NAME (and
  `_fixed` / `_moving` halves), as today. Its Material's `GroupName` follows the Air Region's name: set when
  `AddAirRegion` creates it, and updated when the Air Region panel renames the Air Region. In the Material panel the
  Name field of an Air Region's Material is read-only, with a note "Named after its Air Region; rename it there".
- Duplicate names are already caught by `validation._names` (names equal after `clean`); the panel also refuses a
  name another Material in the Study already has, so the user sees it at once.
- `assignment_label`, `sync_labels` and their callers (the Materials folder view, the Material Library rename path)
  are removed. Renaming a body or a library material no longer renames the Material.

### Suggested name

Filled in when the name field is still untouched (the user has not typed in it):

- One body or Air Region in the list: its `display_name` (e.g. `Coil`). For a whole body this equals today's mesh
  name, so nothing changes for the user.
- Symmetric faces: the chosen library material's label (e.g. `Copper`); before a material is chosen, the drawing's
  (top's) label.
- Re-evaluated on Add selection and on material change, until the user edits the field.
- If the suggestion is taken by another Material in the Study, `_2`, `_3`, ... is appended.
- When the command is run with a selection, the panel opens with that selection already in the list and the name
  suggested from it. With nothing selected the panel opens empty.

## Moving a body or face from another Material

On **Add selection**, if any picked body (whole-body) or face (symmetric) already belongs to another Material, one
`QMessageBox` asks before anything is added:

> **Move to this Material?**
>
> These already belong to another Material:
> • Coil (in "Copper")
> • Yoke (in "Steel")
>
> A body can have only one Material. Move them to "Iron"?
>
> [Move] [Cancel]

(For faces: `Drawing.Face3 (in "Copper")`, and "A face can have only one Material.")

- **Move**: they are added to the list. The other Materials are changed only when this panel's OK runs.
- **Cancel**: those entries are skipped; picks without a conflict are still added.
- One box per Add selection, listing all conflicts.
- If a move would leave another Material with nothing, the note under the list says
  `"Copper" will be removed: it has nothing left.` and OK deletes it in the same transaction.
- Today, assigning a body that already has a Material silently updates that Material (`objects.assign`). Moving
  replaces that: the body leaves its old Material.

## Stored face positions (piece Materials)

*(Builder's call, by the designer.)* `PieceCentres` records where each face was, so `validation._moved` can warn when
FreeCAD renumbered faces. On OK:

- a face that stayed in the list the whole time the panel was open keeps its stored centre, so editing name, material
  or POTENTIAL never hides a real warning;
- a face added in this panel session gets a fresh centre, even if it was removed and re-added in the same session.
  That is how the user clears the warning: Remove the face, Add it again, OK;
- a Material losing faces through a move keeps the centres of the faces it still has.

The warning's advice text changes from "reassign it" to "remove and add it again in its Material's panel".

## Entry points

- `EMS_Material` command (`commands.AssignMaterial`): opens the panel for a new Material, pre-filled from the current
  selection. It no longer warns when nothing is selected. It is inactive while another task dialog is open, like the
  other item commands.
- Double-click on a Material in the tree (`ViewProviderItem.doubleClicked`): opens the panel for it (unless a task
  dialog is already open, as for other items).
- Materials folder panel (`FolderView`): double-clicking a row opens the panel for that row's Material; a row for a
  body without a Material opens a new-Material panel with that body in the list. The bulk **Assign…** button opens
  the panel for one selected row and the several-bodies dialog for more.
- `ask_piece_assignment`, `edit_piece_assignments` and the `ask_text` name prompt for pieces are removed;
  `AssignDialog` shrinks to the several-bodies dialog (no `— none —` entry, no `apply` hook). `objects.assign`, `assign_pieces` and `unassign` stay as the non-GUI API used by tests and
  scripts, gaining a `name` argument for `assign` (default: the suggestion rule).

## Old files

On document restore (`Material.onDocumentRestored`), a Material without `GroupName` gets one:

- whole-body Material: the body's `display_name` (today's mesh name, so the mesh and input file are unchanged). Its
  `Label` is already `<body>: <material>`, which matches the new scheme.
- Air Region Material: the Air Region's `display_name`.
- piece Material: its current `Label`; the label is then rewritten to `<name>: <material>`.

## Tests

- Unit (`pixi run -e addon test-addon`): naming of volumes with and without a Material, Air halves, the suggestion
  rule including `_2`, the restore migration, moving between Materials (old one emptied and removed), duplicate-name
  refusal. Update `test_study.py` / `test_symmetric_study.py` tests that rely on `assignment_label` / `sync_labels`.
- GUI smoke (`tests/freecad_addon/gui_smoke.py`): replace the `ask_assignment` / `ask_piece_assignment` stubs; open
  the panel from the command with a selection, check the suggested name, OK, double-click to reopen, add a body owned
  by another Material with the confirmation stubbed to Move, Cancel on a new Material leaves nothing behind.

## Left to the builder

- Exact widget layout, wording of hints, and whether `MaterialPanel` subclasses or shares helpers with `ItemPanel`.
- How the "user has typed in the name" state is tracked.
