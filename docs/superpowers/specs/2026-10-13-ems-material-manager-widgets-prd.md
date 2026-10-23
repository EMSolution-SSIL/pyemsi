# EMS Material Manager: Reusable Editor Widget and Picker Dialog (PRD)

Date: 2026-10-13
Target repository: `EMSolution-SSIL/EMS_MaterialManager`
Requested by: pyemsi FreeCAD add-on ([Study Material Library design](2026-10-13-study-material-library-design.md))

## 1. Problem

Products that embed EMS Material Manager can only show the full
`MaterialManagerWindow` (a 1200 px `QMainWindow`). The material editor
(identity, version, provenance, catalog-driven property tree, validation, save)
is built inside `MaterialManagerWindow.__init__` and cannot be placed in
another layout. Picking materials only happens inside that window.

The pyemsi FreeCAD add-on needs to:

1. edit one material inside a FreeCAD task panel (about 400 px wide), and
2. let the user pick one or more materials from the Material Manager root to
   copy into a Study.

Until this ships, the add-on uses temporary stand-ins (its own picker, and the
full window opened on a Study-backed repository).

## 2. Goals

- A `MaterialEditorWidget` that edits one material on any `MaterialRepository`
  and fits a narrow panel.
- A `MaterialPickerDialog` that returns the selected materials.
- `MaterialManagerWindow` uses the widget itself, so behaviour and look are
  unchanged for current users.
- Public, documented API; importable from `ems_material.gui`.

## 3. Non-goals

- New editing features, data model changes or new property types.
- A FreeCAD-specific widget. The widgets are plain Qt (qtpy).

## 4. Requirements

### 4.1 `MaterialEditorWidget(QWidget)`

```python
MaterialEditorWidget(
    library: MaterialManager,
    parent: QWidget | None = None,
    *,
    layout: Literal["wide", "compact"] = "wide",
)
```

- `set_material(material_id: str | None)`: load a material (or clear).
- `material_id() -> str | None`, `is_dirty() -> bool`.
- `set_read_only(bool)`; also read-only when `library.is_writable(id)` is false.
- `save() -> Material | None`: validate, write through `library.update`
  (with `expected_version`), return the saved record; show the existing error
  dialogs on failure.
- `revert()`: discard unsaved edits.
- Signals: `changed()` (any edit, dirty state changes), `saved(str)` (material
  ID), `validation_changed(bool)`.
- Contents: everything in today's right-hand pane: identity, version,
  provenance, property tree with catalog status, add/edit/clear property using
  the existing `ScalarEditorDialog` / `CurveEditorDialog`, validation label,
  Edit/Save buttons.
- `layout="compact"`: the identity / version / provenance groups stack
  vertically (or collapse into a single collapsible section), the property
  tree keeps Property / Value / Unit / Status columns with Type and Note
  available as tooltips, and the widget has no minimum width above ~360 px.
- Works on any `MaterialRepository` passed through
  `MaterialManager(repository=...)`, including ones whose only source is not
  `User`. It must not assume the `User` source or a configured root; the
  catalog falls back to package defaults when the repository has no `root`.
- Lists every attribute it reads from the repository beyond the
  `MaterialRepository` protocol (today `MaterialManager.__init__` reads `root`
  and `allow_reference_updates` via `getattr`). Ideally there are none.

### 4.2 `MaterialPickerDialog(QDialog)`

```python
MaterialPickerDialog(
    library: MaterialManager,
    parent: QWidget | None = None,
    *,
    multi_select: bool = True,
    disabled_ids: Iterable[str] = (),
    disabled_reason: str = "",
    title: str = "Select Materials",
)
```

- `selected_materials() -> tuple[Material, ...]` after `exec()` is accepted.
- Same source / family / material tree and search box as the window (shared
  code, not a copy).
- Materials in `disabled_ids` are shown greyed out with `disabled_reason` as
  tooltip and cannot be selected.
- A read-only preview of the highlighted material (the compact
  `MaterialEditorWidget` in read-only mode, or a summary of key values).
- Convenience: `MaterialPickerDialog.pick(library, parent, **kw) -> tuple[Material, ...]`
  (empty on cancel).

### 4.3 `MaterialManagerWindow`

- Built from a material tree on the left and `MaterialEditorWidget(layout="wide")`
  on the right. Menus, admin banner and help unchanged.
- Existing attribute names used by product code (`property_table`, etc.) keep
  working, or the release notes list the changes.

### 4.4 Optional: EMSolution fragment with given IDs

`EMSolutionInputAdapter` today assigns `MAT_ID` and curve IDs itself, and
`_build_fragment` (which accepts them) is private. pyemsi rewrites the IDs after
`export_material`. A public method would remove that step:

```python
EMSolutionInputAdapter().material_fragment(
    material, *, mat_id: int, mat_name: str, curve_ids: Sequence[int],
    selection: ExportSelection | None = None,
) -> dict  # {"material": entry, "bh_curves": [...]}
```

plus `curve_count(material, selection) -> int` so callers can reserve IDs.

## 5. pyemsi usage after the release

- Material Library task panel embeds
  `MaterialEditorWidget(MaterialManager(repository=StudyMaterialRepository(study)), layout="compact")`
  and calls `set_material` when the table selection changes.
- **Import from Material Manager…** calls
  `MaterialPickerDialog.pick(MaterialManager(root), disabled_ids=<Study IDs>, disabled_reason="already in Material Library")`.
- The add-on deletes its `materialpicker.py` stand-in and the call that opens
  `MaterialManagerWindow`.

## 6. Acceptance

- Existing GUI tests pass; window behaviour unchanged.
- New tests: the widget on an in-memory repository (load, edit, dirty,
  save, version conflict, read-only); the picker (search, multi-select,
  disabled IDs, cancel returns empty).
- The compact widget renders at 380 px wide without horizontal scrolling of
  the identity forms.
- Released to PyPI as 0.2.0, with the new API documented in
  `docs/api-emsolution.md` (or a new `docs/api-gui.md`).
