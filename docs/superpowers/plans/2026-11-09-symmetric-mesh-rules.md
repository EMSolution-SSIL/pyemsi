# Symmetric Mesh by Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Mirror / Polar Array chain with Symmetric Groups: the user picks cell objects, gives ordered rules and says what each object's copies become; anything not in a group is meshed normally around the copies.

**Architecture:** The mesher comes first and is built from job files, with no FreeCAD: `meshfrozen.py` holds array operations and free-object meshing, and `meshgroups.py` runs a new `symmetric.groups` job. A checkpoint then has the user solve the first meshes in EMSolution. After that the add-on side is built: a pure rule engine in `symmetry.py`, a `SymmetricGroup` Study item whose Shape is the drawing, Materials per part, validation, job writing and panels. The old path stays working until a single cutover task removes it.

**Tech Stack:** Python 3.11, gmsh 4.15 Python API and numpy 2.4 (mesher process), FreeCAD 1.1 Part (add-on), PySide (panels), pytest.

**Spec:** `docs/superpowers/specs/2026-11-09-symmetric-mesh-rules-design.md`. Read it first, and read section 1's "The logic is general" twice. The older specs `2026-10-23-symmetric-mesh-design.md` and `2026-11-05-symmetric-mesh-3d-design.md` still describe the seams, sliding grid and copied excitations.

## Global Constraints

- Before Task 1: `git checkout -b feature/symmetric-rules` from `feature/symmetric-mesh-3d` (11 commits ahead of `main`), then commit the spec and this plan.
- Run everything through Pixi, never `pip`. One file: `pixi run -e addon pytest tests/freecad_addon/<file> -q -p no:cacheprovider`. Whole add-on suite: `pixi run -e addon test-addon`.
- `meshfrozen.py`, `meshgroups.py`, `meshsym.py`, `mesher.py`, `mesher2d.py`, `meshcommon.py`, `symmetry.py`, `winding.py` never import FreeCAD at module level (`symmetry.read_chain` only uses the objects it is handed). GUI code lives only in `commands.py` and `taskpanels.py`.
- `pixi run format` and `pixi run lint` before each commit. Ruff only, line length 120, double quotes. Never reorder imports, never `--no-verify`. Only format files you changed. `highlight.py` stays out of commits.
- Every existing test in `tests/freecad_addon/` keeps passing at every commit until Task 16, which migrates them.
- GUI changes (Tasks 14, 15, 16) also run `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`; the last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.
- The rule engine, validation and mesher contain no test for a kind of device or for a name (spec section 1). Motor knowledge lives only in `winding.py`.
- Something is refused for only three reasons: the geometry does not fit, the solver cannot do it, or the method does not handle it yet, and then the message says it is a limit of the tool.
- Quality threshold of the poor-element report: min SICN below 0.1 (`POOR = 0.1` in `meshgroups.py`).
- End every commit message with: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Review Focus

1. Saving and reopening a document keeps rules, rows, tables and part Materials, and the drawing shows again (test in Task 10).
2. A typing slip such as a count of 100000 must not freeze FreeCAD: past `MAX_DRAWN` copies the drawing stays empty and the panel and Validate say why (tests in Tasks 8 and 10).
3. A cell object deleted after the group was made gives a named error, not an exception (tests in Tasks 10 and 12).
4. A cell object inside a moved App::Part is copied from where the user sees it (test in Task 10).
5. Two part names that become equal in the mesh, such as `A+` and `A_` after `objects.clean`, are refused (test in Task 12).

---

## Job format (used by Tasks 2 to 7 and written by Task 13)

```python
job = {
    "model_name": "Model", "mesh_file": path, "rotor_file": path,  # rotor_file only when sliding
    "dimension": "2D",                                             # 2D jobs only; a 3D job has no such key
    "options": {...},                                              # as today
    "symmetric": {"groups": [GROUP, ...], "free": [FREE, ...], "slide": SLIDE},  # free and slide optional
}
GROUP = {
    "name": "Stator", "side": "fixed",  # or "moving"
    "job": CELL_JOB,                    # what mesher.build / mesher2d.build read: "volumes" and "surfaces" (3D) or
                                        # "bodies" (2D), "sizes", and "transfinite", "recombine", "recombine_faces" if any
    "cells": [1, 2],                    # local ids of CELL_JOB's bodies
    "transforms": [[16 floats], ...],   # row major, identity first
    "parts": [{"mat_id": 7, "name": "Iron"}, ...],
    "rows": [{"cell": 1, "file": None, "parts": [0, 0, 1, ...]}],  # one part index per transform.
                                        # file: BREP of that solid when a cell has several rows, else None
    "turns": 12,                        # copies around Z; only with a slide
    "excitations": [...],               # as today's sides
}
FREE = {"side": "fixed", "job": FREE_JOB}  # the side's free bodies, with final MAT_IDs and any excitation surfaces
SLIDE = today's block + {"z_range": [z0, z1]}  # z_range in 3D: the height of the whole drawing
```

Today's jobs with `symmetric.sides` keep running through `meshsym.run` until Task 16. `mesher.run_job`, `mesher.check_job` and their `mesher2d` twins send a job to `meshgroups` when `"groups" in job["symmetric"]`.

---

## Part 1: The mesher

### Task 1: Array operations

**Files:**
- Create: `freecad_addon/emsolution/meshfrozen.py`
- Test: `tests/freecad_addon/test_meshfrozen.py`

**Interfaces:**
- Produces, in `meshfrozen`:
  - `read_model(dim: int, entities: dict[key, list[int]]) -> (xyz: ndarray[n,3], {key: {etype: ndarray}})`: the current gmsh model's elements of those entities, node indexes 0-based; nodes shared by keys stay shared.
  - `copy_mesh(xyz, bodies, transforms: list[list[float]]) -> (V, {(key, copy): {etype: ndarray}})`: moved nodes, connectivity reversed when the transform's determinant is negative, coincident nodes joined.
  - `join_nodes(V, tol=1e-6) -> (count, labels)`
  - `boundary(V, elements: list[{etype: ndarray}], dim) -> Boundary`, a namedtuple of `tri`, `quad`, `edge` (facets used once; empty arrays where not applicable), `tri_owner`, `quad_owner`, `edge_owner` (centroid of the element using each facet), `over_used` (facets in 3 or more elements), `shared_area` (area, or length in 2D, of the facets used twice).
  - `quad_pyramids(V, quads) -> (V2, pyramids: ndarray[n,5], tris: ndarray[4n,3])`, apex = centroid + n × 0.3 × sqrt(area), with n the facet's outward normal.
  - constants `NPE`, `FLIP`, `TRI_FACES`, `QUAD_FACES`, `EDGE_FACES` for gmsh element types 1 to 7.

- [ ] **Step 1: Write the failing tests**

```python
ID = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
MX = [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
SHIFT = [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
CUBE = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], float)
HEX = {"a": {5: np.arange(8)[None]}}

def signed(V, c):  # triple product of the three edges at the first corner of a hexahedron
    return np.dot(np.cross(V[c[1]] - V[c[0]], V[c[3]] - V[c[0]]), V[c[4]] - V[c[0]])

def test_mirrored_copy_keeps_positive_volume():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, MX])
    assert signed(V, out[("a", 0)][5][0]) > 0 and signed(V, out[("a", 1)][5][0]) > 0

def test_copies_share_nodes_where_they_touch():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, SHIFT])
    assert len(V) == 12

def test_join_stops_at_the_tolerance():
    assert meshfrozen.join_nodes(np.array([(0, 0, 0), (0, 0, 1e-8), (0, 0, 1e-3)], float))[0] == 2

def test_boundary_of_two_touching_cubes():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, SHIFT])
    b = meshfrozen.boundary(V, list(out.values()), 3)
    assert len(b.quad) == 10 and b.over_used == 0 and b.shared_area == pytest.approx(1.0)

def test_face_of_three_elements_is_counted():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, SHIFT])
    b = meshfrozen.boundary(V, list(out.values()) + [out[("a", 0)]], 3)
    assert b.over_used > 0

def test_pyramid_points_away_from_its_hexahedron():
    b = meshfrozen.boundary(CUBE, [HEX["a"]], 3)
    V2, pyr, tris = meshfrozen.quad_pyramids(CUBE, b.quad)
    assert (np.abs(V2[pyr[:, 4]] - 0.5) > 0.5).any(axis=1).all() and len(tris) == 24

def test_boundary_of_two_squares_in_2d():
    xy = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], float)
    V, out = meshfrozen.copy_mesh(xy, {"a": {3: np.arange(4)[None]}}, [ID, SHIFT])
    b = meshfrozen.boundary(V, list(out.values()), 2)
    assert len(b.edge) == 6 and b.shared_area == pytest.approx(1.0)
```

- [ ] **Step 2: Run:** `pixi run -e addon pytest tests/freecad_addon/test_meshfrozen.py -q -p no:cacheprovider`. Expected: FAIL, no module `meshfrozen`. The test imports it as `from emsolution import meshfrozen`; `conftest.py` puts the add-on on the path.

- [ ] **Step 3: Implement the five functions in `meshfrozen.py`.** No FreeCAD. `join_nodes` rounds to two grids offset by half a cell and propagates the lowest label until stable, so a pair split by one grid is caught by the other; no scipy (not in the environments). `FLIP = {2: [0, 2, 1], 3: [0, 3, 2, 1], 4: [0, 2, 1, 3], 5: [4, 5, 6, 7, 0, 1, 2, 3], 6: [3, 4, 5, 0, 1, 2], 7: [0, 3, 2, 1, 4]}`. `TRI_FACES` and `QUAD_FACES` list each element's faces with outward orientation: `TRI_FACES = {4: [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]], 6: [[0, 2, 1], [3, 4, 5]], 7: [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]}`, `QUAD_FACES = {5: [[0, 3, 2, 1], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]], 6: [[0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]], 7: [[0, 3, 2, 1]]}`, `EDGE_FACES = {2: [[0, 1], [1, 2], [2, 0]], 3: [[0, 1], [1, 2], [2, 3], [3, 0]]}`.

- [ ] **Step 4: Run the tests.** Expected: PASS.

- [ ] **Step 5: Commit** `meshfrozen.py` and the test: `Symmetric rules: array copy, node join and boundary of a mesh`.

### Task 2: Group jobs, no sliding

**Files:**
- Create: `freecad_addon/emsolution/meshgroups.py`
- Modify: `freecad_addon/emsolution/mesher.py:158-169`, `freecad_addon/emsolution/mesher2d.py:154-162`
- Test: `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Consumes: Task 1; from `meshsym`: `_periodic`, `_cell_patches`, `_land_surfaces`, `_entity`, `_side_seams`; from `meshcommon`: `generate`, `publish`, `write_split`, `MSH_VERSION`, `JobError`.
- Produces: `meshgroups.mesh(job, folder, build, dim) -> Model` (gmsh model `"full"` current; `Model` holds `split` and `surfaces`, `{side: {id: (name, [entities])}}`, the shape `meshsym._copy` returns), `meshgroups.run(job_path, build, dim)`, `meshgroups.check(job_path, build, dim)`, `meshgroups.report(job) -> list[str]`, and `meshgroups.mesh_cell(group, job, folder, build, dim) -> Copied`, a namedtuple of `V`, `elements` (`{(row index, copy): {etype: ndarray}}`), `patches`.

- [ ] **Step 1: Write the failing tests.** Class `GroupJobTest(unittest.TestCase)` with the setUp of `MeshSymTest`, and `self.run_job(groups, free=(), slide=None, dim=2, check=False)` that writes the job above and starts `MESHER2D` or `MESHER`.

```python
def test_one_part_over_twelve_copies(self):                    # 2D, sector(10, 20, 0, 30), Rotate × 12
    one = self.count_of(transforms=[ID])                       # the same job with one copy
    found = groups(mesh)
    assert list(found) == [7] and found[7][0] == "Iron" and found[7][1] == 12 * one
    assert mesh_check(mesh, [10, 20])[1:] == (0, 0)

def test_rows_give_parts_by_copy(self):                        # the same cell, parts [0, 1] repeated
    assert {k: v[0] for k, v in groups(mesh).items()} == {7: "North", 8: "South"}

def test_parts_do_not_change_the_mesh(self):                   # the two jobs above: same elements and nodes
    assert element_count(one_part) == element_count(two_parts) and node_count(one_part) == node_count(two_parts)

def test_cell_with_two_rows_splits_by_solid(self):             # one body of two faces, a file per row
    assert groups(mesh)[7][1] + groups(mesh)[8][1] == self.count_of(one_row=True)

def test_structured_and_free_cells_in_one_group(self):         # a transfinite recombined sector beside a free one
    assert element_names(mesh) == {"Quadrilateral 4", "Triangle 3"} and mesh_check(mesh, radii)[1:] == (0, 0)

def test_z_mirror_3d(self):                                    # write_sector_solids(10, 20, 0, 30, 0, 5): Mirror z = 0, Rotate × 12
    assert z_range(mesh) == (-5, 5) and volume(mesh) == pytest.approx(full_ring_volume, rel=1e-2) and faces_in_three(mesh) == 0

def test_groups_do_not_influence_each_other(self):             # two groups, far apart, different sizes and repeats
    assert groups(mesh)[7][1] == self.count_of(only=7) and groups(mesh)[8][1] == self.count_of(only=8)

def test_group_with_no_rules(self):                            # transforms [ID]
    assert groups(mesh)[7][1] > 0

def test_copies_that_overlap_are_refused(self):                # Rotate 20° × 18 of a 30° sector
    assert "more than two elements" in self.mesher_error

def test_report_names_poor_elements_per_part(self):            # patch POOR to 2.0, so every element counts
    assert "Poor elements  Iron" in self.stdout
```

`count_of`, `element_count`, `node_count`, `element_names`, `z_range`, `volume` and `faces_in_three` are small helpers in the test file that read the `.msh` with gmsh.

- [ ] **Step 2: Run them.** Expected: FAIL (`meshgroups` missing or job refused).

- [ ] **Step 3: Implement `meshgroups.py`.**
  - `mesh_cell`: `gmsh.model.add(f"cell_{name}")`, `build(dict(group["job"]), folder)`, `meshsym._periodic([group], dim)`, `generate(dict(group["job"], options=job["options"]), dim)`, `read_model`, `copy_mesh`, patches as today. A cell with several rows sorts each entity into a row: take the first, middle and last element centres (`meshsym._entity`), and test `isInside` against the row's BREP in a temporary model, as `_land` does. Remove the model at the end.
  - `mesh`: for each group, `mesh_cell`, refuse if `boundary(...).over_used` ("the copies of {group} do not fit: a face has more than two elements near (x, y, z)"), then emit into model `"full"`: all nodes once, one discrete entity per `(side, mat_id)`, `addElementsByType`, physical groups, then `removeDuplicateNodes`, `renumberNodes`, `renumberElements` as `_copy` does. Node numbers of different groups are offset so no two groups share a node.
  - Excitation patches copied with `meshsym._land_surfaces([group], [patches], folder, dim)` and written with their SMAT_IDs.
  - `run` and `check` follow `meshsym.run` and `check` line for line, using `mesh`. `report` prints today's MAT_ID and SMAT_ID lines, then `Poor elements  <name>  <count> of <total>` for each part with min SICN below `POOR`.

- [ ] **Step 4: Point `run_job` and `check_job` of both meshers at `meshgroups` when `"groups" in job["symmetric"]`.**

- [ ] **Step 5: Run `test_meshgroups.py`, `test_meshsym.py`, `test_meshsym3d.py`.** Expected: PASS.

- [ ] **Step 6: Commit:** `Symmetric rules: mesh group jobs, parts per copy`.

### Task 3: Sliding with groups and a Z mirror

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py`, `freecad_addon/emsolution/meshsym.py:93-139` (`_slide_faces_sym`)
- Test: `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Consumes: `meshsym._slide_arcs`, `_slide_faces_sym`, `_marker`, `_marker_line`, `_on_circle`, `_on_cylinder`.
- Produces: `_slide_faces_sym(slide, sides)` honouring `slide["z_range"]` and `side["turns"]`, both optional; absent, it behaves as today.

- [ ] **Step 1: Write the failing tests.**

```python
def test_sliding_2d_two_sides(self):                    # today's stator and rotor as two groups, 144 divisions
    assert sorted(nodes_on_circle(fixed)) == sorted(nodes_on_circle(moving))

def test_sliding_3d_with_z_mirror(self):                # cells over z 0..5, Mirror z = 0, Rotate, z_range [-5, 5], cross 4
    assert len(nodes_on_cylinder(fixed)) == 144 * 5 and sorted(nodes_on_cylinder(fixed)) == sorted(nodes_on_cylinder(moving))

def test_cross_divisions_off_the_mirror_are_refused(self):  # cross 3 with the mirror at the middle
    assert "off the grid" in mesher_error

def test_two_groups_on_a_side_only_one_reaches(self):   # a coil group that stays clear of the cylinder
    assert slide nodes as above and groups(fixed) holds both groups' parts

def test_side_that_does_not_reach_is_refused(self):
    assert "must reach it" in mesher_error
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.** In `_slide_faces_sym`: `need = 2πr / side.get("turns", len(transforms)) × cell_height` (the cell's own z extent), and take `z0, z1` from `slide["z_range"]` when present. In `meshgroups.mesh_cell`: before `_periodic`, a group that has an arc (2D) or a face (3D) on the interface gets `_slide_arcs` / `_slide_faces_sym`; one with none is skipped. Those functions raise when called with a group that has none, so test reach first with `meshsym._cylinder_faces` or the arc test. After all groups, each side must have at least one group that reached; if not, raise today's "both sides must reach it" text. Then `_on_circle` / `_on_cylinder` and the marker as in `meshsym._mesh` and `run`.

- [ ] **Step 4: Run `test_meshgroups.py`, `test_meshsym.py`, `test_meshsym3d.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: sliding with groups and a Z mirror`.

### Task 4: Contact between copies

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py`
- Test: `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Produces: `meshgroups.contact_table(group, job, folder, dim) -> list[Contact]`, a namedtuple of `a` and `b` (cell ids), `transform`, `area`, `count` (how many ordered copy pairs have this relative transform, counted once per unordered pair of copies), `seam: bool`; `meshgroups.prepare_images(group, contacts, folder, dim) -> group` (a new group dict with split cell BREPs and image bodies added to its `job`), `meshgroups.pair_images(group, images, dim)`.

- [ ] **Step 1: Write the failing tests.** Geometry: an S-shaped bar A made of two boxes, x 0..1 with z 0..1 and x 1..2 with z 1..2, all y 0..1. A plate B: x 0..1, y 1..2, z 0..2. Transforms: translate +1 in x, × 4. B's wall y = 1 touches the lower half of A (identity) and the upper half of the previous copy of A.

```python
def test_plate_shares_nodes_with_two_copies_of_the_bar(self):
    shared = shared_area(mesh, part_a, part_b)
    assert shared == pytest.approx(2.0 * 4 - 1.0)       # every plate wall, minus the end where no previous bar exists

def test_seam_of_identical_wedges_needs_no_image(self):  # the Task 2 sector
    assert all(c.seam for c in contact_table(...))

def test_seam_that_does_not_match_is_refused(self):      # T-06: a yoke sector with a seam split on one side only
    assert "do not match" in mesher_error
```

`shared_area` reads the mesh with `meshfrozen.read_model` and `boundary` per part, comparing with the two parts together.

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.**
  - `contact_table`: relative transforms `T_i⁻¹ T_j` for i < j, deduplicated by rounded key with a count; for each and each cell pair (a, b) with intersecting bounding boxes, in a temporary gmsh model fragment `T(a)` with `b`. Shared faces (curves in 2D) give `area`. `seam` is true when the shared faces are whole faces of both, so `_same` holds for them; those are handled by `_periodic`.
  - `prepare_images`: for each non-seam contact, gather the shared faces, bring them back with the inverse of T and fragment a with them (all of a's contacts first); write the split cell BREP; write `T(split a)` as a new body with an id above every cell id; return the group with its job updated. `cells` is unchanged, so images are never copied.
  - `pair_images`, called after `build`: faces of each image are paired with those of its source by centre of mass and `setPeriodic(dim - 1, image_faces, source_faces, T)`, skipping faces belonging to both (as the spike did).
  - Area check in `mesh`: `boundary(...).shared_area` must equal `Σ c.area × c.count` within 1e-6 relative, else `JobError` "the copies of {group} do not match near ...", with the place taken from a free facet lying on a contact face.

- [ ] **Step 4: Run `test_meshgroups.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: contact between copies, whole objects included`.

### Task 5: Free objects around frozen copies

**Files:**
- Modify: `freecad_addon/emsolution/meshfrozen.py`, `freecad_addon/emsolution/meshgroups.py`
- Test: `tests/freecad_addon/test_meshfrozen.py`, `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Produces, in `meshfrozen`:
  - `shells(facets: ndarray) -> list[ndarray of facet indexes]`, connected components over shared edges (nodes in 2D); raises `FrozenError` when an edge is not used exactly twice (a node not exactly twice in 2D).
  - `nest(V, facets, shells) -> list[(outer: int, inner: list[int])]`: even-depth shells are outer boundaries, each odd-depth shell a hole of its parent. Winding-number test with numpy.
  - `mesh_region(V, facets, outer, inners, size, dim) -> (V2, {etype: ndarray})`: nodes 0..len(V)-1 unchanged, new nodes appended.
  - `FrozenError(Exception)`.
- Produces, in `meshgroups`: `mesh_free(free, side_boundary, V, job, folder, build, dim) -> {mat_id: (name, V additions, elements)}`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_shells_of_two_separate_tetrahedra():            # meshfrozen: 8 triangles in 2 components
def test_open_surface_is_refused():                      # one triangle removed: FrozenError
def test_cube_inside_a_cube_nests():                     # nest == [(outer, [inner])]
def test_ring_gives_two_regions():                       # 3 nested squares: [(0, [1]), (2, [])]

def test_box_of_air_around_rotated_copies(self):         # 3D: copied solids, free box drawn right over them
    assert all_frozen_kept and inverted == 0 and groups(mesh)[20][0] == "Air"
def test_hex_copies_get_pyramids(self):                  # transfinite recombined cell in a free box
    assert types(mesh, "Air") >= {"tet", "pyramid"} and all_frozen_kept and no_face_in_3_elements
def test_shell_outside_the_free_body_is_left_out(self):  # a second group far from the air
    assert count(mesh, "Air") == count_without_second_group
def test_free_object_and_excitation_on_its_face(self):
    assert surface_group(mesh, 50) == ("Outer", n, pytest.approx(box_face_area))
def test_two_free_bodies_touching(self):                 # two boxes side by side around the copies
    assert shared_area(mesh, "AirA", "AirB") == pytest.approx(contact) and no_face_in_3_elements
def test_free_size_is_used(self):                        # size 1 against size 4
    assert count_fine > count_coarse
def test_2d_disc_with_holes(self):                       # 2D copies inside a drawn disc
    assert area(mesh) == pytest.approx(disc_area, rel=1e-3) and free_edges_only_on_disc
def test_2d_ring_of_copies_gives_bore_and_outside(self): # copies form an annulus: two regions, one Air group
    assert area(mesh, "Air") == pytest.approx(disc_area - annulus_area, rel=1e-3)
def test_zx_copies_in_free_air(self):                    # 2D ZX job: Mirror z = 0, a drawn rectangle of air
    assert y_range(mesh) == (0, 0) and area(mesh) == pytest.approx(drawn_area, rel=1e-3)
def test_sliding_with_free_air_outside_the_band(self):   # Task 3's motor with a Z mirror, plus a free ring outside the band
    assert sorted(nodes_on_cylinder(fixed)) == sorted(nodes_on_cylinder(moving)) and "Air" in names(fixed)
```

`all_frozen_kept` compares the frozen facets (from a run with no free object) with the boundary of the air elements. Tests needing it read the msh with `read_model`.

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement the three array functions and `mesh_region`.** 3D recipe: new model, frozen nodes added on discrete surface 1 with tags kept (node index + 1); `addElementsByType`; `gmsh.model.mesh.createTopology()`; map each surface entity to its shell by its first element's node; `gmsh.model.geo.addSurfaceLoop` with the outer shell's surfaces first, then each hole's; `gmsh.model.geo.addVolume`; `geo.synchronize()`; `Mesh.Algorithm3D = 1`, `Mesh.Renumber = 0`, `Mesh.MeshSizeMax = size`, `Mesh.MeshSizeExtendFromBoundary = 1`, `Mesh.Optimize = 1`; `generate(3)`. Node coordinates for tags up to `len(V)` come from `V`, not from gmsh. 2D recipe: an OCC plane surface per region, with each shell a polygon curve loop through the nodes' real coordinates (all three, so a ZX Study works), each polygon line `setTransfiniteCurve(l, 2)`, and new nodes joined afterwards with `join_nodes`.

- [ ] **Step 4: Implement `mesh_free`.** In model `free_<side>`: `build(free["job"], folder)` (so sizes, fragments of touching bodies and physical groups work as in an ordinary Study), `generate(job, 2)` in 3D or `generate(job, 1)` in 2D. For each free OCC volume (face in 2D) gather its own facets with those frozen facets whose centroid lies inside it, add pyramids on frozen quads (`quad_pyramids`; the pyramids join that free object's elements and their four triangles replace the quad), join coincident nodes, `shells`, `nest`, drop shells that lie outside it (only frozen facets, and a point outside the body), `mesh_region` for each. Refuse unless every frozen facet inside the object is on the boundary of the new elements. Excitation surfaces on free faces keep the 2D elements of that face.

- [ ] **Step 5: Call `mesh_free` from `mesh`, for each entry of `symmetric.free`,** after all groups, passing the boundary of that side's groups.

- [ ] **Step 6: Run `test_meshfrozen.py`, `test_meshgroups.py`.** Expected: PASS.

- [ ] **Step 7: Commit:** `Symmetric rules: mesh free objects around frozen copies`.

### Task 6: Copies meeting the free object's own surface

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py`, `freecad_addon/emsolution/meshfrozen.py`
- Test: `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Produces: `meshfrozen.on_surface(V, facets, owners, face_tags, dim) -> OnFaces`, which for each frozen facet lying on a face of the free object gives that face's tag and whether the owning element is inside the free object.

- [ ] **Step 1: Write the failing tests.**

```python
def test_strands_ending_on_the_air_end_planes(self):      # straight cylinders from z = 0 to z = 10, air box z 0..10
    assert all lateral frozen faces kept and end faces of strands are not air faces and no_face_in_3_elements
def test_air_ring_flush_against_the_copies(self):         # air drawn with its inner face exactly on the copies' outer face
    assert shared_area(mesh, "Iron", "Air") == pytest.approx(2 * math.pi * r * h, rel=1e-3)
def test_stator_running_the_full_height_splits_the_air(self):  # bore and outside, both in the Air group
    assert count(mesh, "Air") > 0 and two connected air regions and no_face_in_3_elements
def test_copy_crossing_a_curved_face_is_refused(self):
    assert "limit of the tool" in mesher_error and "curved face" in mesher_error
def test_copy_passing_through_a_planar_face_is_refused(self):  # a copy that does not end on the plane
    assert "limit of the tool" in mesher_error
def test_2d_copies_reaching_a_straight_edge_of_the_air(self):
    assert area(mesh) == pytest.approx(drawn_area, rel=1e-3) and no_edge_in_3_elements
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.** A frozen facet on a free face is **kept** when its owning element lies outside the free object (the copy is flush against it) and **removed** when the owner lies inside (an end cap, which the air cannot touch). Either way the face must leave room: a face entirely covered is dropped (areas equal within 1e-6). A partly covered planar face is rebuilt before meshing with one hole per loop of the covered region's outer edges: `occ.remove` the free volume non-recursively, `addCurveLoop` from the polygon through the exact end-edge nodes (each line transfinite with 2 nodes), `addPlaneSurface([outer loop, holes...])` on that plane, carrying over the face's physical groups. A partly covered curved face raises `JobError` containing "limit of the tool" and "curved face". `shells` raising `FrozenError` for anything still open becomes the same kind of `JobError`. In 2D the same logic works on lines: an edge partly covered is split at the end nodes.

- [ ] **Step 4: Run `test_meshgroups.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: copies flush with or ending on a free object`.

### Task 7: Checkpoint: the user solves the first meshes

**Files:**
- Create: `experiments/symmetric_rules/gate_meshes.py`, `experiments/symmetric_rules/data/distributed_half.brep`, `experiments/symmetric_rules/data/double_skew_opposite.brep` (copied from `C:\Users\hamed\Desktop\delme\curved_end_windings\` and `...\double_skew_litz\`)

- [ ] **Step 1: Write `gate_meshes.py`.** It writes job files and runs `mesher.py` on them, into `C:\Users\hamed\Desktop\delme\rules_gate`: (a) a 3D motor with Mirror z = 0, sliding and a free air ring outside a copied band; (b) hexahedral coils pressed on tetrahedral iron in free air (pyramids against frozen hexahedra).

- [ ] **Step 2: Run:** `pixi run -e addon python experiments/symmetric_rules/gate_meshes.py`. Expected: both jobs write `.msh` and `mesh.unv`, `Poor elements` lines printed.

- [ ] **Step 3: Commit:** `Symmetric rules: gate meshes for an EMSolution solve`.

- [ ] **Step 4: Stop and ask the user to solve both meshes in EMSolution.** Do not start Task 8 until the user reports the result. If EMSolution refuses pyramids against frozen hexahedra or the sliding mesh, bring the error to the user; the design changes.

---

## Part 2: The add-on

### Task 8: Rule engine and part names

**Files:**
- Modify: `freecad_addon/emsolution/symmetry.py`
- Test: `tests/freecad_addon/test_rules.py`

**Interfaces:**
- Produces, in `symmetry` (rules are plain dicts, JSON-serialisable):
  - `{"kind": "mirror", "point": [x, y, z], "normal": [x, y, z]}`, `{"kind": "rotate", "point": ..., "axis": ..., "step": deg, "count": n}`, `{"kind": "translate", "vector": ..., "count": n}`, `{"kind": "motion", "matrix": [16], "count": n}`.
  - `rule_matrix(rule) -> list[float]`, `rule_count(rule) -> int`, `copy_count(rules) -> int`.
  - `copies(rules) -> list[tuple[int, ...]]`: indices per rule, last rule slowest, all-zero first.
  - `transforms(rules) -> list[list[float]]`, same order.
  - `rule_problems(rules, plane: str) -> list[str]`, plane `""` (3D), `"XY"` or `"ZX"`.
  - `rule_warnings(rules) -> list[str]`.
  - `part_names(row: dict, rules, label: str) -> list[str]`, with row `{"mode": "one"|"each"|"across"|"table", "across": [rule indexes], "table": [names]}`.
  - constant `MAX_DRAWN = 5000`.

- [ ] **Step 1: Write the failing tests.**

```python
MIRROR_X0 = {"kind": "mirror", "point": [0, 0, 0], "normal": [1, 0, 0]}
TWO_24 = {"kind": "translate", "vector": [24, 0, 0], "count": 2}
ROT = lambda step, n, axis=(0, 0, 1), point=(0, 0, 0): {"kind": "rotate", "point": list(point), "axis": list(axis), "step": step, "count": n}

def xs(rules, x=5.0):
    return [round(apply(t, [x, 0, 0])[0], 6) for t in transforms(rules)]

def test_mirror_then_translate():                       # T-01
    assert xs([MIRROR_X0, TWO_24]) == [5, -5, 29, 19]

def test_translate_then_mirror():                       # T-02
    assert xs([TWO_24, MIRROR_X0]) == [5, 29, -5, -29]

def test_numbering_has_the_last_rule_slowest():
    assert copies([MIRROR_X0, ROT(90, 2)]) == [(0, 0), (1, 0), (0, 1), (1, 1)]

def test_identity_first():
    assert transforms([MIRROR_X0, ROT(90, 4)])[0] == ID

def test_no_rules_is_one_copy():
    assert transforms([]) == [ID]

def test_rotation_about_an_oblique_axis_through_a_point():
    t = rule_matrix(ROT(120, 3, axis=(1, 1, 1), point=(1, 0, 0)))
    assert apply(t, [2, 0, 0]) == pytest.approx([1, 1, 0])

def test_mirror_normal_need_not_be_unit():
    m = rule_matrix({"kind": "mirror", "point": [0, 0, 2], "normal": [0, 0, 5]})
    assert apply(m, [1, 1, 3]) == pytest.approx([1, 1, 1]) and det(m) == pytest.approx(-1)

def test_a_screw_step_goes_through_the_engine():
    screw = compose(translation([0, 0, 4]), rotation_about([0, 0, 0], [0, 0, 1], 6))
    assert apply(transforms([{"kind": "motion", "matrix": screw, "count": 3}])[2], [1, 0, 0])[2] == pytest.approx(8)

@pytest.mark.parametrize("rule,plane,text", [
    (ROT(30, 2, axis=(1, 0, 0)), "XY", "axis"),
    ({"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 1]}, "XY", "normal"),
    (ROT(30, 2, axis=(0, 1, 0)), "ZX", "rotation"),
    ({"kind": "mirror", "point": [0, 0, 0], "normal": [1, 0, 0]}, "ZX", "normal"),
    ({"kind": "translate", "vector": [1, 0, 0], "count": 2}, "ZX", "translation"),
    (ROT(30, 1), "", "count"),
    ({"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 0]}, "", "normal"),
])
def test_rule_problems(rule, plane, text):
    assert text in " ".join(rule_problems([rule], plane))

def test_identical_copies_are_refused():
    assert "identical" in " ".join(rule_problems([MIRROR_X0, MIRROR_X0], ""))
    assert "identical" in " ".join(rule_problems([ROT(90, 5)], ""))

def test_any_3d_axis_is_accepted():
    assert rule_problems([ROT(45, 8, axis=(1, 2, 3))], "") == []

def test_rotation_that_does_not_close_warns():
    assert "360" in " ".join(rule_warnings([ROT(30, 11)])) and rule_warnings([ROT(30, 12)]) == []

def test_part_names():
    rules = [MIRROR_X0, ROT(120, 3)]
    assert part_names({"mode": "one"}, rules, "Iron") == ["Iron"] * 6
    assert len(set(part_names({"mode": "each"}, rules, "S"))) == 6
    assert part_names({"mode": "across", "across": [0]}, rules, "C") == ["C_1", "C_1", "C_2", "C_2", "C_3", "C_3"]
    assert part_names({"mode": "table", "table": list("abcdef")}, rules, "x") == list("abcdef")

def test_huge_count_is_a_problem():
    assert "copies" in " ".join(rule_problems([ROT(0.001, 100000)], ""))
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.** Add also `rotation_about(point, axis, deg)` and `translation(v)`. Axes and normals are normalised. A rule problem past `MAX_DRAWN` copies is reported first, and the identical-copies check is skipped then. The engine treats every rule as G and count; `kind` matters only in `rule_matrix` and `rule_problems`.

- [ ] **Step 4: Run `test_rules.py`, `test_symmetry.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: rule engine and part names`.

### Task 9: Winding generator

**Files:**
- Create: `freecad_addon/emsolution/winding.py`
- Test: `tests/freecad_addon/test_winding.py`

**Interfaces:**
- Produces: `two_layer(slots, pole_pairs, span, per_coil=False) -> (top: list[str], bottom: list[str])` (by slot), `whole_coils(slots, pole_pairs, per_coil=False) -> list[str]`, `slot_of(centres, point, axis, slots) -> list[int]` (slot of each copy, from the angle of its centre about the axis, counted from the first copy in the rotation direction), `by_copy(names_by_slot, slots_of_copies) -> list[str]`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_36_slots_4_poles_span_8():                      # M2-15
    top, bottom = two_layer(36, 2, 8)
    assert top[:8] == ["A+", "A+", "C-", "C-", "C-", "B+", "B+", "B+"]
    assert bottom[:3] == ["A+", "C-", "C-"]

def test_27_slots_6_poles_fractional():                  # M2-16: q = 1.5
    top, _ = two_layer(27, 3, 4)
    assert top[:9] == ["A+", "C-", "C-", "B+", "A-", "A-", "C+", "B-", "B-"]
    assert Counter(n[0] for n in top) == {"A": 9, "B": 9, "C": 9}

def test_bottom_layer_is_the_top_moved_by_the_span_and_reversed():
    top, bottom = two_layer(30, 2, 7)
    flip = {"+": "-", "-": "+"}
    assert all(bottom[k] == top[k - 7][0] + flip[top[k - 7][1]] for k in range(30))

def test_span_one_gives_concentrated():                  # M2-08
    top, bottom = two_layer(9, 4, 1)
    assert all(bottom[k][0] == top[k - 1][0] for k in range(9))

def test_per_coil_names():
    top, bottom = two_layer(36, 2, 8, per_coil=True)
    assert top[0] == "Coil01" and bottom[0] == "Coil29"

def test_slot_of_a_mirrored_half_cell():                 # centres at ±2.5° about each slot axis, 30° pitch
    assert slot_of(centres, (0, 0, 0), (0, 0, 1), 12) == [0, 0, 1, 1, 2, 2]

def test_names_stay_different_in_the_mesh():             # objects.clean maps + to _, keeps -
    assert len({re.sub(r"[^A-Za-z0-9_-]", "_", n) for n in two_layer(36, 2, 8)[0]}) == 6
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement** with `sector = ((k * p * 360 + 30 * Ns) % (360 * Ns)) // (60 * Ns)` and names `["A+", "C-", "B+", "A-", "C+", "B-"]`; bottom of slot k = sector of coil `(k - y) % Ns`, plus 3, mod 6. Per coil: top of slot k is coil k, bottom is coil `(k - y) % Ns`, named `Coil{c + 1:02d}`.

- [ ] **Step 4: Run them.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: winding table generator`.

### Task 10: The Symmetric Group item and its drawing

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`, `freecad_addon/emsolution/geometry.py:159-176,225-242`
- Test: `tests/freecad_addon/test_symmetric_groups.py`, `tests/freecad_addon/symcases.py`

**Interfaces:**
- Consumes: Task 8; `geometry.global_shape`.
- Produces, in `objects`:
  - `class SymmetricGroup(_Proxy)`: a `Part::FeaturePython` in `MeshSizesGroup` (as `AirRegion` is), properties `Cells` (`App::PropertyLinkListGlobal`), `Rules` and `Rows` (`App::PropertyString`, JSON), `Side` (`App::PropertyEnumeration`: `Fixed`, `Moving`). `execute` sets `Shape` to the compound of copies, one solid (face in 2D) per row per copy, in `(copy, row)` order; an empty compound past `symmetry.MAX_DRAWN` or when a cell is gone.
  - `make_symmetric_group(study, cells, rules=(), name="Symmetric Group", side="Fixed") -> obj`
  - `symmetric_groups(study) -> list`, `is_grouped(study) -> bool`, `rules_of(item) -> list[dict]`, `rows_of(item) -> list[dict]`, `set_rules(item, rules)`, `set_rows(item, rows)`.
  - Each row dict: `{"cell": Name, "solid": index, "mode": ..., "across": [...], "table": [...], "material": lib Name or ""}`. `sync_rows(item)` gives each solid (face) of each cell a row, keeping existing ones.
  - `group_transforms(item) -> list`, `row_shape(item, row)`, `row_label(item, row) -> str`, `row_parts(item, row) -> list[str]`.
  - `element_owner(item, sub) -> (row, copy)` for `"SolidN"` or `"FaceN"`; 3D faces go through `face_solids`.
- `cell_bodies(study)` includes groups' cells. `to_cells` treats a group as a chain: `{item.Name: (cells, group_transforms(item))}`. `geometry.region` and `setup` accept an empty Main when `objects.is_grouped(study)`. `_main_bodies`-based gates in `assignment_problem` pass when grouped, and `assignable` includes the groups.

- [ ] **Step 1: Add `symcases.group_motor_doc(doc, height=0)` and write the failing tests.** The builder reuses `motor_doc`'s cell faces with no chain objects.

```python
def test_drawing_has_a_solid_per_row_per_copy(study):
    assert len(stator.Shape.Faces) == 3 * 24

def test_empty_rules_draw_the_cell(study):
def test_the_drawing_follows_the_rules(study):           # set_rules with count 6 -> faces = 3 * 12
def test_order_of_rules_is_visible_in_the_drawing(study):  # T-01 against T-02: different BoundBox
def test_huge_count_leaves_the_drawing_empty(study):     # Review Focus 2
    assert stator.Shape.isNull() or not stator.Shape.Faces
def test_deleted_cell_does_not_raise_on_recompute(study):  # Review Focus 3
def test_cell_in_a_moved_part_is_copied_from_where_it_shows(study):  # Review Focus 4
    assert stator.Shape.BoundBox.ZMin == pytest.approx(5)
def test_group_survives_save_and_reopen(study, tmp_path):  # Review Focus 1
    assert rules, rows, tables equal and reopened.Shape.Faces count equal
def test_fragments_cell_has_one_row_per_face(study):     # split_coil
    assert len([r for r in rows_of(stator) if r["cell"] == "CoilFragments"]) == 2
def test_element_owner(study):
    assert element_owner(stator, f"Face{3 * 2 + 2}") == (1, 2)
def test_empty_main_is_fine_with_groups(study):
    assert geometry.setup(study)[2] == []
def test_to_cells_moves_a_pick_on_the_drawing_to_the_cell(study):
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.** Mirrored copies use `shape.transformGeometry` or `shape.transformed(matrix)` as `_overlaps` does. `onDocumentRestored` adds nothing yet. `attach_view_provider` picks it up through `_Proxy`. Add `SymmetricGroup` to the proxies tuple at `objects.py:1272` and `_size_text`.

- [ ] **Step 4: Run `test_symmetric_groups.py`, `test_symmetric_study.py`, `test_study.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: Symmetric Group item and its drawing`.

### Task 11: A Material per part

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`
- Test: `tests/freecad_addon/test_symmetric_groups.py`

**Interfaces:**
- Consumes: Task 10.
- Produces:
  - `Material.add_part(obj)` adds `PartKey` (`App::PropertyString`, `"fixed|A+"`), called from `__init__` and `onDocumentRestored`.
  - `study_parts(study) -> {key: [(item, row index, copy), ...]}`; a part name is per side.
  - `sync_parts(study) -> list[str]`: creates an assignment for each new key (named after the part, library material from the row), removes those whose key is gone, returns the removed names.
  - `part_assignments(study) -> list`, `part_refs(m) -> [(item, "SolidN")]` (`item_refs` returns these for a part assignment).
  - `set_row_material(study, item, row, lib)`: sets the library material on the row and on every part of that row.
- `volume_keys`: when grouped, part assignment names, then free bodies' names (`study_bodies`), then interfaces. `material_rows`: when grouped, free-body rows as usual followed by `(assignment, refs, [name, material, MAT_ID, POTENTIAL])` rows. `surface_keys`: when grouped, excitations on groups and on free bodies. `is_symmetric` stays for the old path until Task 16.

- [ ] **Step 1: Write the failing tests.**

```python
def test_each_part_has_one_assignment(study):
def test_same_name_on_two_rows_is_one_part(study):       # both layers table with "A+"
    assert len(study_parts(study)["fixed|A+"]) == 2 * 6
def test_same_name_on_the_two_sides_is_two_parts(study):
def test_parts_gone_remove_their_assignment_and_are_reported(study):
    assert sync_parts(study) == ["Coil_2"]
def test_rename_keeps_key_and_changes_mesh_name(study):
def test_set_row_material_covers_all_its_parts(study):
def test_one_mat_id_per_part(study):
    objects.update_ids(study); assert set(study.MatIds) == {m.Name for m in part_assignments(study)} | {iface.Name}
def test_material_rows_list_free_bodies_and_parts(study):
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.** `make_symmetric_group`, `set_rules` and `set_rows` do not sync by themselves; panels and tests call `sync_parts` when they finish, so one edit does not churn the tree.

- [ ] **Step 4: Run `test_symmetric_groups.py`, `test_symmetric_study.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: one Material per part`.

### Task 12: Validate Study

**Files:**
- Modify: `freecad_addon/emsolution/validation.py:70-106,646-787`
- Test: `tests/freecad_addon/test_symmetric_groups.py`

**Interfaces:**
- Consumes: Tasks 8, 10, 11.
- Produces: `validation._groups(study, main, moving, r)`, called when `objects.is_grouped(study)`, followed by `_air`-free handling: free bodies go through `_materials`, `_coarse` and `_transfinite` as ordinary bodies, part assignments through `_part_materials`.

- [ ] **Step 1: Write the failing tests.** One per line of spec section 6: each builds a Study from `symcases`, breaks it, and asserts a phrase in the errors.

```python
@pytest.mark.parametrize("name,breaks,phrase", [
    ("zero_normal", ..., "normal"),
    ("2d_axis", ..., "axis"),
    ("same_mirror_twice", ..., "identical"),
    ("coil_past_the_line", ..., "overlaps"),                     # T-04
    ("step_smaller_than_cell", ..., "overlaps"),                 # T-05
    ("groups_touch", ..., "one group, or draw"),
    ("part_without_material", ..., "no Material"),
    ("name_on_both_sides", ..., "both sides"),
    ("table_wrong_length", ..., "table"),
    ("empty_table_name", ..., "table"),
    ("cell_without_solid", ..., "solid"),
    ("body_in_two_groups", ..., "two groups"),
    ("cell_also_in_main", ..., "Main"),
    ("air_region", ..., "Air Region"),
    ("sliding_axis_x", ..., "about Z"),                          # T-07
    ("free_crosses_sliding", ..., "Sliding Interface"),
    ("free_transfinite", ..., "Transfinite"),
    ("deleted_cell", ..., "was deleted"),                        # Review Focus 3
    ("names_equal_in_mesh", ..., "in the mesh"),                 # Review Focus 5
    ("old_item", ..., "older version"),                          # after Task 16 only: mark skip until then
])
def test_refused(...): ...

def test_rotation_that_does_not_close_is_a_warning(study):
def test_translation_through_any_axis_validates(study):
def test_free_air_and_copies_validate(study):
def test_x_axis_rules_validate_without_sliding(study):
def test_z_mirror_with_sliding_validates(study):
def test_zx_study_with_a_z_mirror_validates(study):
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement `_groups`.** Reuse `_overlaps(item, cells, transforms, r, three)`: pass row shapes. Across groups of a side: `common` of the two drawings, bounding boxes first, and touching tested by the distance between the two compounds being zero with a contact of positive area ("put them in one group, or draw a normally meshed body between them"). Sliding: for a group whose drawing reaches the interface radius, each rule must be a rotation about Z through the origin, a mirror containing Z, or a mirror of z = const; else error on the interface naming the rule; `Divisions % turns` uses the product of Z rotation counts. A free body must not cross the interface. An unknown cell name in `Rows` gives "was deleted".

- [ ] **Step 4: Run `test_symmetric_groups.py`, `test_symmetric_study.py`, `test_symmetric_study3d.py`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: Validate Study for groups and free objects`.

### Task 13: Writing the job

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py:40-64,243-350`
- Test: `tests/freecad_addon/test_symmetric_groups.py`

**Interfaces:**
- Consumes: Tasks 10, 11, 12; the job format above.
- Produces: `jobwriter.write_groups(study, folder) -> dict`, the `symmetric` block; `write_job` calls it when grouped and writes no top-level bodies. Mini-jobs come from one helper, `_body_job(study, folder, bodies, prefix) -> dict`, factored out of today's `write_job` lines 259-291, 312-334, 342-350, so sizes, transfinite and recombine are written the same way for cells and free bodies.

- [ ] **Step 1: Write the failing tests.**

```python
def test_job_holds_a_mini_job_per_group(study, tmp_path):
    assert [g["name"] for g in block["groups"]] == ["Stator", "Rotor"] and len(g["transforms"]) == 24
def test_row_parts_index_the_group_parts(study, tmp_path):
def test_free_bodies_go_to_free_with_final_mat_ids(study, tmp_path):
def test_z_range_and_turns_with_sliding(study, tmp_path):
    assert block["slide"]["z_range"] == [-10, 10] and block["groups"][0]["turns"] == 12
def test_mesh_settings_go_with_their_cell(study, tmp_path):
def test_group_motor_runs_end_to_end(study, tmp_path):   # meshes through the real runner path, 2D and 3D
    assert groups(msh) has every part and mesh_check inverted == 0
def test_excitation_on_the_drawing_is_copied(study, tmp_path):
```

- [ ] **Step 2: Run them.** Expected: FAIL.

- [ ] **Step 3: Implement.** Cells get local ids 1..n per group. A row BREP is written only when its cell has several rows. Excitations on a group's faces go into that group's `excitations` as `write_symmetric` does; on a free body into its `FREE` job's surfaces.

- [ ] **Step 4: Run `test_symmetric_groups.py` and the whole suite.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: write group jobs`.

### Task 14: The group panel, table dialog and reading helper

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py`, `freecad_addon/emsolution/commands.py:346-363,414`, `freecad_addon/emsolution/symmetry.py`, `freecad_addon/emsolution/labels.py:27`
- Test: `tests/freecad_addon/test_rules.py`, `tests/freecad_addon/test_symmetric_groups.py`, `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: Tasks 8 to 11.
- Produces:
  - `symmetry.rules_from_chain(top) -> list[Proposal]`, a namedtuple of `cells`, `rules`; one proposal per distinct set of copies. Raises `SymmetryError` with an explanation if a set of copies cannot be written as an ordered rule list (compare `transforms(rules)` with the chain's set). Mirror normals and polar axes may point anywhere: `_walk`, `_array` and `read_chain` take `any_axis=False`, which this helper sets to True, using `rotation_about` and a 3D mirror, so the old item's refusals still hold until Task 16.
  - `taskpanels.SymmetricGroupPanel(obj, new=False)`: widgets `name`, `side` (combo, hidden without Sliding motion), `rows` (QTableWidget: object, mode, ticked rules), `rules` (QListWidget), buttons `add_mirror`, `add_rotate`, `add_translate`, `remove_rule`, `rule_up`, `rule_down`, `use_selection`, `read_drawing`, `table_button`, editor fields for the selected rule, `summary` (QLabel: "24 copies, 18 parts"), `problem` (QLabel in red). Each edit applies inside an open transaction and recomputes, so the drawing is live. OK commits and calls `objects.sync_parts`, warning with any removed names. Cancel aborts.
  - `taskpanels.TableDialog(item, row)`: one line per copy; `generate` opens slots, pole pairs, coil span, per-coil tick, and fills from `winding`.
  - Command `EMS_SymmetricGroup` (the old command stays until Task 16). Cell objects picked before the command are added to the group, and the group's cells are hidden after OK.

- [ ] **Step 1: Write the failing tests.**

```python
def test_chain_reads_as_rules(motor):                    # test_rules.py
    (p,) = rules_from_chain(info["stator_top"])
    assert [r["kind"] for r in p.rules] == ["mirror", "rotate"] and p.rules[1]["count"] == 12
def test_chain_branches_with_different_copies_are_two_proposals(motor):
def test_mirror_along_z_reads(motor):
def test_chain_that_is_no_rule_list_is_explained(motor):
```

and a block in `gui_smoke.py`: run `EMS_SymmetricGroup` on the stator cells, add a mirror and a rotation through the panel's buttons, assert that `item.Shape.Faces` changes after each and that `summary` reads `24 copies`; set a row to `table`, open `TableDialog`, generate, assert the table is full; Cancel leaves no item (`UndoNames` unchanged); OK leaves part assignments; double-click reopens; `read_drawing` fills rules from a chain.

- [ ] **Step 2: Run:** the pytest file, then the smoke test. Expected: FAIL.

- [ ] **Step 3: Implement.** Follow `SymmetricMeshPanel`, `ItemPanel` and `ViewProviderItem`. The double-click dispatch at `taskpanels.py:673` and `:1022` gains the new class. The drawing's view provider is the shape's own, so clicks land on it.

- [ ] **Step 4: Run both.** Expected: PASS, last line `PASS`.

- [ ] **Step 5: Commit:** `Symmetric rules: group panel, table dialog and reading helper`.

### Task 15: Picking on the drawing

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py:1074-1115,1356-1585`, `freecad_addon/emsolution/commands.py:128-163`
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `objects.element_owner`, `objects.study_parts`, `objects.part_refs`, `objects.set_row_material`.
- Produces: `MaterialPanel` on a part assignment (`obj.PartKey` set): name, library material and POTENTIAL are editable; the list shows its copies and Add / Remove are disabled. `AssignMaterial` on a face of a drawing opens the panel of that copy's part. A free body behaves as in any Study. `FolderView.edit_row_material` already handles a row that is a Material; `assign_rows` refuses several rows only when any is a Material. Mesh setting panels and `ItemGate.main` accept the groups' names, and picks move to the cell through `to_cells`. `Excitation` picks stay on faces of the drawing.

- [ ] **Step 1: Add to `gui_smoke.py`.** Click a coil face on the drawing and run `EMS_Material`: the panel's `obj` is that part's assignment; change the library material and OK; a free air body gets the ordinary panel; a Mesh Size picked on the drawing's face references the cell; an Excitation on a drawing face keeps `(item, "FaceN")`; "All parts of this object" sets the material on every part of the row.

- [ ] **Step 2: Run the smoke test.** Expected: FAIL at the first new assert.

- [ ] **Step 3: Implement.**

- [ ] **Step 4: Run the smoke test and `test-addon`.** Expected: PASS.

- [ ] **Step 5: Commit:** `Symmetric rules: Materials and mesh settings picked on the drawing`.

### Task 16: Cutover

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`, `validation.py`, `jobwriter.py`, `taskpanels.py`, `commands.py`, `meshsym.py`, `mesher.py`, `mesher2d.py`, `tests/freecad_addon/symcases.py`, `test_symmetry.py`, `test_meshsym.py`, `test_meshsym3d.py`, `test_symmetric_study.py`, `test_symmetric_study3d.py`, `gui_smoke.py`, `experiments/symmetric_examples/build_examples.py`, `experiments/symmetric_examples/README.md`

- [ ] **Step 1: Remove the skip from the `old_item` validation test and run it.** Expected: FAIL.

- [ ] **Step 2: Remove the old path.** Gone: `SymmetricMeshPanel`, `make_symmetric_mesh`, `AddSymmetricMesh`, `assign_pieces`, `piece_assignments`, the `Pieces` branches of `apply_material` and `MaterialPanel`, `selected_piece_solids`, `validation._symmetric`, `_pieces`, `_moved`, `write_symmetric`; in `meshsym`: `_land`, `_outline`, `_conform`, `_copy`, `_mesh`, `run`, `check`, `report`, and the `sides` dispatch in both meshers. `is_symmetric` becomes `is_grouped`. Kept: `read_chain` and `steps` for the reading helper, with the `any_axis` parameter dropped so any axis always reads, and the class `SymmetricMesh` as a stub, so old documents open and Validate reports: "Symmetric Mesh {label} is from an older version. Add a Symmetric Group; Read from drawing fills it from {top}." `Material.Pieces` stays as a property on old objects and is ignored. `EMS_SymmetricGroup`'s menu text is "Symmetric Group", icon `symmetricmesh`.

- [ ] **Step 3: Move the tests.** `symcases.motor_study` and `motor_study_3d` build groups (same cells, same rules as the chains). `test_symmetric_study*.py`: port every test whose behaviour still exists. `test_meshsym*.py`: port seam, sliding, excitation and copy-mismatch tests to group jobs; delete landing and coverage tests, since landing no longer exists. `test_symmetry.py`: Z-limit tests become acceptance tests. `gui_smoke.py`: the old Symmetric Mesh block goes.

- [ ] **Step 4: Rebuild the examples.** `build_examples.py` makes groups with no chain objects, and the README's workflow text matches. Run: `pixi run -e addon python experiments/symmetric_examples/build_examples.py --challenges`. Expected: every example meshes, 0 inverted, 0 gaps.

- [ ] **Step 5: Run the suite and the smoke test:** `pixi run -e addon test-addon`, `pixi run lint`. Expected: all pass, `PASS`.

- [ ] **Step 6: Commit:** `Symmetric rules: replace the chain-based Symmetric Mesh`.

### Task 17: Success list and an arrangement from no catalogue

**Files:**
- Create: `tests/freecad_addon/test_rules_end_to_end.py`, `experiments/symmetric_rules/success_list.py`
- Modify: `tests/freecad_addon/symcases.py`

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Write the failing test for the arrangement from no catalogue.**

```python
def test_arbitrary_solids_oblique_rules_groups_and_free_body(tmp_path):
    """Group 1: a box and a touching wedge, Mirror about the plane through (1, 2, 3) with normal (1, 1, 2), then
    Rotate 72° × 5 about the axis (1, 2, 2) through (0, 3, 0). Group 2: a sphere, Translate (40, 7, 9) × 3.
    Free: one big box. Mirrored and rotated cells are chosen so that nothing overlaps."""
    assert not validation.errors(validation.validate(study))
    report = mesh_and_read(study)
    assert report.inverted == 0 and report.faces_in_three == 0 and report.frozen_kept
```

Add the second generality check, by grep, in the same file:

```python
def test_core_code_knows_no_device():
    for name in ("meshfrozen.py", "meshgroups.py", "symmetry.py", "validation.py"):
        assert not re.search(r"\b(motor|slot|stator|rotor|strand|litz|winding)\b", source(name), re.I), name
```

Where these files still use one of those words in a comment or message, reword it.

- [ ] **Step 2: Run it.** Expected: FAIL only where code is missing. If the mesher refuses the arrangement, fix the method and do not change the test.

- [ ] **Step 3: Write `success_list.py`.** It builds in FreeCAD, validates, meshes and prints a table for: the sliding motor redone with rules (`experiments/symmetric_examples/1_motor_sliding`), M2-15 (table from the generator), M3-02 with sliding, M3-07 (drawn air gap ring), M3-10 with drawn air (from `data/distributed_half.brep`, its coil pressed in slots as in spec section 9, case 7), M3-12, R-07, L-06 and L-07 (from `data/double_skew_opposite.brep`: the straight strand on the axis is a group with no rules; the 8 strands whose centre angle lies in a 60° window are the cells of `Rotate Z 60° × 6`; L-07 only changes the tables), D-07, D-08. The checks are spec section 8 item 2: 0 inverted, no facet in 3 or more elements, every frozen face kept. Meshes go to `C:\Users\hamed\Desktop\delme\rules_success`.

- [ ] **Step 4: Run:** `pixi run -e addon python experiments/symmetric_rules/success_list.py`. Expected: every row OK. Poor-element counts are reported, not failed; M3-10 will show the known ruled-loft weakness (spec section 9). Try `gmsh.model.mesh.setCompound` over the strips as the spec suggests; keep it only if it lowers the count with no other change.

- [ ] **Step 5: Run the suite and the smoke test.** Expected: PASS, `PASS`.

- [ ] **Step 6: Commit:** `Symmetric rules: success list and a general arrangement`.

- [ ] **Step 7: Ask the user to solve one mesh of each family from `rules_success` in EMSolution** (spec section 8 item 5).
