# Structured mesh on chosen faces of a body (2D)

Status: implemented on feature/freecad-addon. Scope: 2D Studies of the FreeCAD add-on. Builds on
`2026-10-15-transfinite-mesh-design.md` and `2026-10-16-recombine-design.md`.

## 1. Intent

To get a structured (transfinite) mesh, a region has to be cut into blocks with 3 or 4 corners. In FreeCAD the user
does this with Part tools: a divider sketch plus Boolean Fragments (or Slice) on the face. The result is one body
with several faces.

Today the transfinite items work on whole bodies only. Transfinite Body on a Fragments body structures every face of
it, and Recombine recombines every face of it. The user cannot structure some blocks and leave the rest to the normal
unstructured mesher, or recombine only some blocks.

The user wants to structure every block of a cut body in the usual case, and to keep the freedom to leave some blocks
unstructured.

Sample: `C:\Users\hamed\Desktop\delme\multiface-test\multiface-test.FCStd` (the user's file, outside the repository).
A half stator slot:

- `stator_cell_fragments` = Boolean Fragments of `core_cell` and `core_div` (two arcs): 3 faces. Face2 (21.0 mm², the
  block under the coil) has 4 edges; Face1 (yoke, 49.1 mm²) and Face3 (tooth tip, 16.3 mm²) have 5.
- `stator_air_fragments` = Boolean Fragments of `stator_air_cell` and `stator_air_div` (one arc): 2 faces. Face1
  (slot opening, 4.5 mm²) has 4 edges, Face2 (6.4 mm²) has 5.
- `coil_cell`: one face, 5 edges.

The dividers end on existing vertices, so the Fragments leave no loose edge.

## 2. Goals

- G1. Transfinite Body takes picked faces of a body as well as whole bodies. A picked face is structured; the other
  faces of the body are meshed as today (unstructured, with Mesh Size and Transfinite Edges as set).
- G2. Recombine takes picked faces of a body in the same way.
- G3. Validate Study checks the rules per structured face and names the body and face in its messages
  (`stator_cell_fragments Face2`), never a BREP file or Gmsh tag.
- G4. Old documents mesh exactly as before: a whole-body reference keeps its meaning.

## 3. Non-goals

- Materials per face. A body keeps one Material and one MAT_ID however many faces it has. Fragments are for meshing
  only (user's decision).
- Tracking faces when the user edits a sketch. FreeCAD may renumber `FaceN`; the user knows this and re-picks. No
  detection or warning is required (user's decision).
- 3D. The data model and job format must not block solids picked from a 3D Fragments body later, but nothing in 3D
  is built or tested now. In 3D Studies the panels keep today's whole-body behaviour.
- Symmetric mesh (`feature/symmetric-mesh`). It will be rebased onto this work later.
- Mesh Size and Transfinite Edges: they already take faces, edges and vertices. No change.

## 4. Anti-goals

- An Explode step, or drawing each block as its own face, to get per-block settings.
- A setting that silently spreads to faces the user did not pick, or silently drops a picked face.
- Any change in the mesh of an existing document that uses only whole-body references.

## 5. Behaviour

### 5.1 References

`TransfiniteBody.References` and `Recombine.References` are `App::PropertyLinkSubListGlobal` already. Today the
sub-element is always empty (whole body). From now on, in 2D Studies:

- `(body, "")`: every face of the body (today's meaning).
- `(body, "FaceN")`: that face only.

One item may mix both kinds and may hold several faces of one body.

`TransfiniteBody.Corners` keeps its property, but a corner now belongs to its item (builder's call, made here): it
counts only for the structured faces of that same item that it lies on. So when Face1 of a body is in item A and Face3
in item B, a vertex shared by both faces and picked in A does not change Face3. Today corners are gathered per body;
the job and `apply_transfinite` must carry and look them up per item and body instead.

### 5.2 Picking in the task panels (2D only)

- Clicking a face in the 3D view adds that face (`FaceN`).
- Selecting a body in the tree adds the whole body.
- Clicking a vertex adds a corner (Transfinite Body), as today.
- Builder's call (made here): when the body has exactly one face, a face click is stored as the whole body
  (`(body, "")`), so single-face bodies behave and save as today.
- The panel's hint text for 2D says this (face = that block; tree = whole body; vertex = corner).

3D panels are unchanged.

### 5.3 Validation (Validate Study)

Today's rules from `validation._transfinite`, applied per structured face instead of per body. The structured faces
of a body are all its faces for a whole-body reference, or the picked faces.

- V1. A face is in at most one Transfinite Body item. A whole-body reference in one item and a face reference to the
  same body in another item is a conflict on the shared faces. Message names the body, the face(s) and both items.
- V2. Every edge of a structured face is in some Transfinite Edges item. Edges of unpicked faces are not required.
  Message lists the missing edges, as today.
- V3. The body's faces share their edges (`loose_pieces` check), as today, when any face of it is structured.
- V4. A face reference that does not exist on the body (`Face7` on a 3-face body) is an error naming the item, body
  and face.
- V5. Recombine: a face reference that does not exist is an error, as V4. A face or body in two Recombine items stays
  allowed, as today (builder's call, made here): Recombine has no settings, so a duplicate is harmless, and refusing it
  would break old documents (G4).
- V6. A corner that lies on none of its item's structured faces is an error naming the item, the body and the vertex
  (builder's call, made here: a corner that does nothing is a mistake the user should see).

The 3- or 4-corner and opposite-sides checks stay in the mesher (they need the final Gmsh topology). For a picked
face, their messages name the body and the face (`stator_cell_fragments Face2`). For a whole-body reference they stay
as today, body plus centre point (builder's call, made here: naming every face would add a BREP file per face to old
jobs, against G4).

### 5.4 Job and mesher

The job keys and BREP file prefixes were built as recommended here (they match).

The mesher must find the final Gmsh faces of a picked face. The existing pattern for this is the sub-element files:
`export_subs` writes `geometry/<prefix>_<n>.brep` and the mesher maps each file through the fragment
(`transfinite_files`, corner and edge files). Picked faces use the same pattern.

Recommended job shape (builder may adjust, keeping G4):

```json
"transfinite": {
  "bodies": [
    {"name": "stator_cell_fragments", "mat_id": 3, "corner_files": [...],
     "faces": [{"face": "Face2", "file": "geometry/tface_3_1.brep"}]}
  ],
  "edges": [...]
},
"recombine": [5],
"recombine_faces": [{"name": "stator_cell_fragments", "mat_id": 3, "face": "Face2", "file": "geometry/rface_3_1.brep"}]
```

- A body entry without `"faces"` is a whole body (today's meaning).
- One body entry per (Transfinite Body item, body), each with its own `corner_files`, so corners stay with their item
  (section 5.1).
- `apply_transfinite` structures the mapped faces of a body that has `"faces"`, all its faces otherwise.
- `apply_recombine` recombines whole bodies from `"recombine"` and the mapped faces from `"recombine_faces"`. The
  full-quad check (`_check_full_quad`) treats a recombined face that is not structured as today's non-structured
  case.
- A picked face file must map to faces of that body only; if it does not (it did not merge), that is a `JobError`
  naming the body and face, as for the corner and edge files.

## 6. Acceptance

- A1. A document like the sample (built in a test, not loaded from the user's file): all five blocks structured
  (two whole Fragments bodies, corners picked on the 5-edge faces) meshes with 0 inverted elements (signed area)
  and quads where recombined.
  As built, A1 is tested on one three-block body (whole body, corners on the pentagon) rather than on two whole
  Fragments bodies.
- A2. The same document with only `stator_cell_fragments Face2` structured: Face2 is a structured grid, Face1 and
  Face3 are meshed unstructured, and the shared edges are conformal.
- A3. Recombine on one face only: that face has quads, the other faces of the body triangles.
- A4. Validation: V1, V2, V4, V5 and V6 each have a unit test that triggers the message and checks it names body and face.
- A5. Old documents: the existing transfinite and recombine tests pass unchanged.
- A6. GUI smoke (`tests/freecad_addon/gui_smoke.py`): in a 2D Study, a face click on a multi-face body in the
  Transfinite Body and Recombine panels stores `(body, "FaceN")`; a tree pick stores the whole body.

## 7. Left to the builder

- The exact job keys and BREP file prefixes (section 5.4 is a recommendation).
- How face-to-edge names are found for V2 (for example `isSame` between the face's edges and `body.Shape.Edges`).
- How the item list in the panel shows a face reference (for example `stator_cell_fragments.Face2`).
- Wording of messages, within G3.
