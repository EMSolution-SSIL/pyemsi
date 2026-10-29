"""Build the Symmetric Mesh example files, one folder each, and mesh them headless.
Run from the repo root: pixi run -e addon python experiments/symmetric_examples/build_examples.py [--challenges]

It uses the add-on that FreeCAD loads, through the Mod folder link that `pixi run -e addon install-addon` makes. So the
files are built and meshed by the same code you try them with in the GUI. Point the link at the clone that has the
Symmetric Mesh (the pyemsi-sym worktree, or this checkout once feature/symmetric-mesh is checked out here)."""

import json
import math
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADDON = os.path.realpath(os.path.join(os.environ["APPDATA"], "FreeCAD", "v1-1", "Mod", "EMSolution"))
if not os.path.exists(os.path.join(ADDON, "emsolution", "symmetry.py")):
    sys.exit(f"FreeCAD's add-on link points at {ADDON}, which has no Symmetric Mesh. Run install-addon in that clone.")
sys.path.insert(0, ADDON)

import FreeCAD as App  # noqa: E402 - after the add-on path
import Part  # noqa: E402
import Draft  # noqa: E402
from BOPTools import SplitFeatures  # noqa: E402

import gmsh  # noqa: E402
from emsolution import jobwriter, objects, symmetry  # noqa: E402

MESHER2D = os.path.join(ADDON, "emsolution", "mesher2d.py")
V = App.Vector


# --- geometry ------------------------------------------------------------------------------------------------------


def polar(r, a):
    return V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0)


def sector(r1, r2, a1, a2):
    """Annular sector face, radii r1..r2, angles a1..a2 deg."""
    am = (a1 + a2) / 2
    edges = [
        Part.Arc(polar(r2, a1), polar(r2, am), polar(r2, a2)).toShape(),
        Part.LineSegment(polar(r2, a2), polar(r1, a2)).toShape(),
        Part.Arc(polar(r1, a2), polar(r1, am), polar(r1, a1)).toShape(),
        Part.LineSegment(polar(r1, a1), polar(r2, a1)).toShape(),
    ]
    return Part.Face(Part.Wire(edges))


def feature(doc, name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def chain(doc, part, cells, mirror_deg, count):
    """The user's steps: Compound(cell bodies) -> Mirror about the line at mirror_deg -> Compound(cell, mirror) ->
    Draft Polar Array (count x 360/count) -> Boolean Fragments. Only the Fragments (the top) stays visible."""
    cell = doc.addObject("Part::Compound", f"{part}Cell")
    cell.Links = cells
    mirror = doc.addObject("Part::Mirroring", f"{part}Mirror")
    mirror.Source = cell
    mirror.Normal = V(-math.sin(math.radians(mirror_deg)), math.cos(math.radians(mirror_deg)), 0)
    pitch = doc.addObject("Part::Compound", f"{part}Pitch")
    pitch.Links = [cell, mirror]
    doc.recompute()
    array = Draft.make_polar_array(pitch, number=count, angle=360)
    array.Label = f"{part}Array"
    doc.recompute()
    top = SplitFeatures.makeBooleanFragments(name=f"{part}Fragments")
    top.Objects = [array]
    doc.recompute()
    for o in top.OutListRecursive:
        if hasattr(o, "Visibility"):
            o.Visibility = False  # clicks land on the top; the cell bodies are still in the tree
    return top


def stator_cells(doc, split=False):
    """Half a slot pitch, 0..15 deg: iron, a coil (37..50 mm, 10..15 deg) and the stator half of the air gap.
    split: the coil is a Boolean Fragments of the coil face and an arc at r 43 (inner and outer block)."""
    iron = feature(doc, "StatorIronCell", sector(36, 60, 0, 15).cut(sector(37, 50, 10, 15)).Faces[0])
    coil = feature(doc, "CoilCell", sector(37, 50, 10, 15))
    air = feature(doc, "StatorAirCell", sector(35, 36, 0, 15))
    if split:
        divider = feature(doc, "CoilDivider", Part.Arc(polar(43, 10), polar(43, 12.5), polar(43, 15)).toShape())
        coil = SplitFeatures.makeBooleanFragments(name="CoilFragments")
        coil.Objects = [doc.getObject("CoilCell"), divider]
        coil.Mode = "Standard"
        doc.recompute()
    return [iron, coil, air]


def rotor_cells(doc):
    """Half a pole, 0..22.5 deg: iron, half a magnet and the rotor half of the air gap."""
    return [
        feature(doc, "RotorIronCell", sector(10, 30, 0, 22.5)),
        feature(doc, "MagnetCell", sector(30, 34, 4.5, 22.5)),
        feature(doc, "RotorAirCell", sector(30, 35, 0, 22.5).cut(sector(30, 34, 4.5, 22.5)).Faces[0]),
    ]


# --- Study helpers -------------------------------------------------------------------------------------------------


def record(material_id, name, family="generic"):
    return {
        "schema": "ems_material",
        "schema_version": "1.0",
        "material_id": material_id,
        "material_version": "1.0.0",
        "identity": {
            "name": name,
            "family": family,
            "manufacturer": None,
            "grade": None,
            "description": None,
            "aliases": [],
            "tags": [],
        },
        "properties": {},
        "provenance": {"source_type": "USER_INPUT", "reference": None, "date": None, "notes": None},
        "version_metadata": {"author": "example", "updated_at": "2026-10-28T00:00:00+00:00", "change_note": "example"},
    }


def library(study):
    """Steel, Copper and Air in the Study's library: {name: library material}."""
    out = {}
    for key, name, family in [
        ("steel", "Steel", "electrical_steel"),
        ("copper", "Copper", "conductor"),
        ("air", "Air", "fluid_or_gas"),
    ]:
        out[name] = objects.make_library_material(study, json.dumps(record(f"user:{key}", name, family)))
    return out


def new_doc(name, sliding=False):
    folder = os.path.join(HERE, name)
    os.makedirs(folder, exist_ok=True)
    doc = App.newDocument(name)
    return doc, os.path.join(folder, name + ".FCStd")


def study_on(doc, main, moving=None, size=2.0):
    study = objects.make_study(doc, "2D", "Study")
    study.MainMode, study.MainObjects = "Manual", [main]
    if moving is not None:
        study.MovingMode, study.MovingObjects = "Manual", [moving]
        study.Movement = "Sliding motion"
    else:
        study.Movement = "No movement"
    study.MeshSizesGroup.DefaultMeshSize = size
    for top in [main] + ([moving] if moving is not None else []):
        objects.make_symmetric_mesh(study, top)
    return study


def where(face):
    c = face.CenterOfMass
    return math.hypot(c.x, c.y), math.degrees(math.atan2(c.y, c.x)) % 360


def assign_by(study, top, name_of, lib):
    """One Material per name that name_of(face) gives the faces of top; lib: {Material name: library material}."""
    groups = {}
    for i, face in enumerate(top.Shape.Faces, 1):
        groups.setdefault(name_of(face), []).append((top, f"Face{i}"))
    for name in sorted(groups):
        objects.assign_pieces(study, name, groups[name], lib[name], 0)


def stator_piece(face, split=False):
    """Stator pieces: air gap 35..36, coils 37..50 (one per 30 deg slot), iron. split: a two-layer winding, the
    inner (37..43) and outer (43..50) block of each slot are coils of their own."""
    r, a = where(face)
    if r < 36:
        return "StatorAir"
    if split:
        for r1, r2, layer in [(37, 43, "Inner"), (43, 50, "Outer")]:
            if abs(face.Area - sector(r1, r2, 10, 15).Area) < 1e-6:
                return f"Coil{int(a // 30) + 1:02d}{layer}"
    if abs(face.Area - sector(37, 50, 10, 15).Area) < 1e-6:
        return f"Coil{int(a // 30) + 1:02d}"
    return "StatorIron"


def rotor_piece(face):
    r, a = where(face)
    if r < 30:
        return "RotorIron"
    return "Magnet" + "NS"[int(a // 45) % 2] if r < 32.5 else "RotorAir"


def material_lib(lib, names):
    kind = {"Coil": "Copper", "StatorAir": "Air", "RotorAir": "Air"}
    return {n: lib[next((v for k, v in kind.items() if n.startswith(k)), "Steel")] for n in names}


def edges_of(body, face):
    own = body.Shape.getElement(face).Edges
    return [(body, f"Edge{i}") for i, e in enumerate(body.Shape.Edges, 1) if any(e.isSame(g) for g in own)]


def block(body, r1, r2):
    """FaceN of the face of body that is the sector r1..r2 of the slot."""
    area = sector(r1, r2, 10, 15).Area
    return next(f"Face{i}" for i, f in enumerate(body.Shape.Faces, 1) if abs(f.Area - area) < 1e-6)


def on_top(top, cell_edges):
    """The same edges, picked on the top in the cell's own place (what a click on the Fragments gives)."""
    out = []
    for body, sub in cell_edges:
        e = body.Shape.getElement(sub)
        out += [
            (top, f"Edge{i}")
            for i, f in enumerate(top.Shape.Edges, 1)
            if (f.CenterOfMass - e.CenterOfMass).Length < 1e-6 and abs(f.Length - e.Length) < 1e-6
        ][:1]
    return out


# --- 1: the motor, sliding -----------------------------------------------------------------------------------------


def motor():
    doc, path = new_doc("1_motor_sliding")
    stator = chain(doc, "Stator", stator_cells(doc), 15, 12)
    rotor = chain(doc, "Rotor", rotor_cells(doc), 22.5, 8)
    study = study_on(doc, stator, rotor)
    objects.make_sliding_interface(study, "Rotational", Radius=35, Divisions=144)
    lib = library(study)
    names = {stator_piece(f) for f in stator.Shape.Faces} | {rotor_piece(f) for f in rotor.Shape.Faces}
    mats = material_lib(lib, names)
    assign_by(study, stator, stator_piece, mats)
    assign_by(study, rotor, rotor_piece, mats)
    return doc, study, path


# --- 2: the stator alone, a structured coil set from picks on the Fragments -----------------------------------------


def stator_structured():
    doc, path = new_doc("2_stator_structured")
    cells = stator_cells(doc)
    stator = chain(doc, "Stator", cells, 15, 12)
    study = study_on(doc, stator)
    lib = library(study)
    assign_by(study, stator, stator_piece, material_lib(lib, {stator_piece(f) for f in stator.Shape.Faces}))
    coil = doc.getObject("CoilCell")
    arcs = [(coil, f"Edge{i}") for i, e in enumerate(coil.Shape.Edges, 1) if isinstance(e.Curve, Part.Circle)]
    radials = [(coil, f"Edge{i}") for i, e in enumerate(coil.Shape.Edges, 1) if not isinstance(e.Curve, Part.Circle)]
    # picked on the Fragments, as a click there does: each becomes the edge of every cell body that has it
    objects.make_transfinite_edges(study, 4, objects.to_cells(study, on_top(stator, arcs))).Label = "coil arcs 4 el"
    objects.make_transfinite_edges(study, 8, objects.to_cells(study, on_top(stator, radials))).Label = "coil sides 8 el"
    objects.make_transfinite_body(study, [coil])
    objects.make_recombine(study, [coil])
    return doc, study, path


# --- 3: a cell cut by a Boolean Fragments ---------------------------------------------------------------------------


def split_coil():
    doc, path = new_doc("3_split_coil")
    cells = stator_cells(doc, split=True)
    stator = chain(doc, "Stator", cells, 15, 12)
    study = study_on(doc, stator)
    lib = library(study)
    names = {stator_piece(f, True) for f in stator.Shape.Faces}
    assign_by(study, stator, lambda f: stator_piece(f, True), material_lib(lib, names))
    frag = doc.getObject("CoilFragments")
    outer = block(frag, 43, 50)
    edges = edges_of(frag, outer)
    arcs = [r for r in edges if isinstance(frag.Shape.getElement(r[1]).Curve, Part.Circle)]
    objects.make_transfinite_edges(study, 4, arcs).Label = "outer arcs 4 el"
    objects.make_transfinite_edges(study, 4, [r for r in edges if r not in arcs]).Label = "outer sides 4 el"
    objects.make_transfinite_body(study, []).References = [(frag, outer)]
    objects.make_recombine(study, []).References = [(frag, outer)]
    return doc, study, path


# --- 4: your split-cell drawing from the PRD -----------------------------------------------------------------------


def your_test_file():
    """experiments/symmetric_spike/test.FCStd of feature/symmetric-mesh (the PRD's reproduction), copied."""
    src = os.path.join(ADDON, "..", "experiments", "symmetric_spike", "test.FCStd")
    folder = os.path.join(HERE, "4_prd_test_file")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "4_prd_test_file.FCStd")
    if not os.path.exists(path):
        shutil.copy(src, path)
    doc = App.openDocument(path)
    doc.recompute()
    return doc, objects.studies(doc)[0], path


# --- 5: a cell body past the mirror line (R3 of the split-cell PRD, not done) ---------------------------------------


def coil_past_mirror():
    """The coil is drawn 10..17 deg in a 0..15 deg cell: it reaches 2 deg past the mirror line, so it overlaps its own
    mirrored copy. Validate Study's own checks pass; only the mesher check finds it, with a point and no body name."""
    doc, path = new_doc("5_coil_past_mirror_line")
    coil = feature(doc, "CoilCell", sector(37, 50, 10, 17))
    iron = feature(doc, "StatorIronCell", sector(36, 60, 0, 15).cut(coil.Shape).Faces[0])
    air = feature(doc, "StatorAirCell", sector(35, 36, 0, 15))
    stator = chain(doc, "Stator", [iron, coil, air], 15, 12)
    study = study_on(doc, stator)
    lib = library(study)

    def piece(face):
        if abs(face.Area - coil.Shape.Area) < 1e-6:
            return f"Coil{int((where(face)[1] + 5) // 30) % 12 + 1:02d}"
        return stator_piece(face)

    assign_by(study, stator, piece, material_lib(lib, {piece(f) for f in stator.Shape.Faces}))
    return doc, study, path


# --- 6: 13 copies of a 30 deg slot pitch (R3 again) ----------------------------------------------------------------


def thirteen_copies():
    """The stator of example 2's drawing, but the Polar Array makes 13 copies of the 30 deg pitch: each copy overlaps
    the next by 2.3 deg, and the Fragments cuts the cell bodies there. Materials are set on the 13-copy pieces."""
    doc, path = new_doc("6_thirteen_copies")
    stator = chain(doc, "Stator", stator_cells(doc), 15, 13)
    study = study_on(doc, stator)
    lib = library(study)
    assign_by(study, stator, stator_piece, material_lib(lib, {stator_piece(f) for f in stator.Shape.Faces}))
    return doc, study, path


# --- 7: a cell cut by drawing each block as its own face (R2 of the split-cell PRD) ---------------------------------


def coil_two_faces():
    """Example 3 drawn the other way (R2): the coil is two faces sharing the arc at r 43, both straight in the cell."""
    doc, path = new_doc("7_coil_two_faces")
    iron = feature(doc, "StatorIronCell", sector(36, 60, 0, 15).cut(sector(37, 50, 10, 15)).Faces[0])
    outer = feature(doc, "CoilOuterCell", sector(43, 50, 10, 15))
    inner = feature(doc, "CoilInnerCell", sector(37, 43, 10, 15))
    air = feature(doc, "StatorAirCell", sector(35, 36, 0, 15))
    stator = chain(doc, "Stator", [iron, outer, inner, air], 15, 12)
    study = study_on(doc, stator)
    lib = library(study)
    names = {stator_piece(f, True) for f in stator.Shape.Faces}
    assign_by(study, stator, lambda f: stator_piece(f, True), material_lib(lib, names))
    return doc, study, path


# --- run -----------------------------------------------------------------------------------------------------------


def outline(study):
    """The edges of the tops that bound one face only: the outside of the drawing (and the sliding circle)."""
    out = []
    for item in objects.symmetric_items(study):
        shape = item.Top.Shape
        out += [e for e in shape.Edges if len(shape.ancestorsOfType(e, Part.Face)) == 1]
    return out


def mesh_report(paths, edges_out):
    """{element kind: count}, inverted elements (signed area <= 0) and element edges used by one element that are
    not on edges_out (a gap between copies or blocks), over the .msh files."""
    counts, inverted, edges, xyz = {}, 0, {}, {}
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        for k, path in enumerate(paths):
            gmsh.clear()
            gmsh.open(path)
            tags, coords, _ = gmsh.model.mesh.getNodes()
            pts = {(k, int(t)): coords[3 * i : 3 * i + 3] for i, t in enumerate(tags)}
            xyz.update(pts)
            for typ in gmsh.model.mesh.getElementTypes(2):
                name, _, _, _, _, corners = gmsh.model.mesh.getElementProperties(typ)
                etags, enodes = gmsh.model.mesh.getElementsByType(typ)
                counts[name] = counts.get(name, 0) + len(etags)
                per = len(enodes) // len(etags)
                for e in range(len(etags)):
                    ring = [(k, int(n)) for n in enodes[e * per : e * per + corners]]
                    p = [pts[n] for n in ring]
                    inverted += sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1])) <= 0
                    for a, b in zip(ring, ring[1:] + ring[:1]):
                        key = tuple(sorted((a, b)))
                        edges[key] = edges.get(key, 0) + 1
    finally:
        gmsh.finalize()

    seen = {}

    def on_outline(n):  # nodes, not the element edge's midpoint: a straight edge along an arc is off the arc
        if n not in seen:
            p = Part.Vertex(V(*xyz[n]))
            seen[n] = any(p.distToShape(e)[0] < 1e-6 for e in edges_out)
        return seen[n]

    loose = sum(1 for (a, b), c in edges.items() if c == 1 and not (on_outline(a) and on_outline(b)))
    return counts, inverted, loose


def mesh(study, title):
    try:
        job = jobwriter.write_job(study)
    except jobwriter.StudyError as e:
        print(f"[{title}] Study refused:\n  " + str(e).replace("\n", "\n  "))
        return
    r = subprocess.run([sys.executable, MESHER2D, job], capture_output=True, encoding="utf-8", errors="replace")
    lines = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip() and not ln.startswith("Info")]
    print(f"[{title}] mesher exit {r.returncode}:\n  " + "\n  ".join(lines[-8:]))
    if r.returncode == 0:
        files = [jobwriter.mesh_file(study)] + (
            [jobwriter.rotor_file(study)] if study.Movement == "Sliding motion" else []
        )
        counts, inverted, loose = mesh_report(files, outline(study))
        print(f"  elements: {counts}, inverted: {inverted}, gaps: {loose}")


def challenges():
    """The README's challenges, built and meshed on throwaway copies, to check what it promises."""

    def eleven_slots(doc, study):
        doc.getObjectsByLabel("StatorArray")[0].NumberPolar = 11

    def divisions_100(doc, study):
        objects.sliding_interfaces(study)[0].Divisions = 100

    def no_coil05(doc, study):
        doc.removeObject(next(m for m in objects.materials(study) if m.Label == "Coil05").Name)

    def bolt_hole(doc, study):
        hole = feature(doc, "BoltHole", Part.Face(Part.Wire(Part.makeCircle(1.5, polar(55, 7.5)))))
        top = doc.getObject("StatorFragments")
        top.Objects = list(top.Objects) + [hole]

    def outer_arc_5(doc, study):
        coil = doc.getObject("CoilCell")
        outer = [
            (coil, f"Edge{i}")
            for i, e in enumerate(coil.Shape.Edges, 1)
            if isinstance(e.Curve, Part.Circle) and e.Curve.Radius > 49
        ]
        moved = objects.to_cells(study, on_top(doc.getObject("StatorFragments"), outer))
        item = objects.transfinite_edges(study)[0]
        gone = {(b.Name, s) for b, s in moved}
        item.References = [(b, s) for b, subs in item.References for s in subs if (b.Name, s) not in gone]
        objects.make_transfinite_edges(study, 5, moved)

    def inner_block_too(doc, study):
        frag = doc.getObject("CoilFragments")
        inner = block(frag, 37, 43)
        objects.transfinite_bodies(study)[0].References = list(objects.transfinite_bodies(study)[0].References) + [
            (frag, inner)
        ]

    def inner_block_solved(doc, study):
        inner_block_too(doc, study)
        frag = doc.getObject("CoilFragments")
        have = {s for e in objects.transfinite_edges(study) for _, subs in e.References for s in subs}
        rest = [r for r in edges_of(frag, block(frag, 37, 43)) if r[1] not in have]
        arc = [r for r in rest if isinstance(frag.Shape.getElement(r[1]).Curve, Part.Circle)]
        objects.make_transfinite_edges(study, 4, arc).Label = "inner arc 4 el"
        objects.make_transfinite_edges(study, 3, [r for r in rest if r not in arc]).Label = "inner sides 3 el"

    def divider_in_the_cell(doc, study):
        cell = doc.getObject("StatorCell")
        cell.Links = list(cell.Links) + [doc.getObject("CoilDivider")]

    for build, change, title in [
        (motor, eleven_slots, "1 + StatorArray 11 copies"),
        (motor, divisions_100, "1 + Divisions 100"),
        (motor, no_coil05, "1 + Material Coil05 deleted"),
        (motor, bolt_hole, "1 + a bolt hole in one tooth"),
        (stator_structured, outer_arc_5, "2 + outer coil arc 5 el"),
        (split_coil, inner_block_too, "3 + inner block structured, no edge counts"),
        (split_coil, inner_block_solved, "3 + inner block structured, solved"),
        (split_coil, divider_in_the_cell, "3 + the divider sketch put in the cell"),
    ]:
        doc, study, path = build()
        doc.recompute()
        change(doc, study)
        doc.recompute()
        check = path.replace(".FCStd", "_check.FCStd")
        doc.saveAs(check)
        mesh(study, title)
        App.closeDocument(doc.Name)
        os.remove(check)


if __name__ == "__main__":
    print("add-on:", ADDON)
    for build in (
        motor,
        stator_structured,
        split_coil,
        your_test_file,
        coil_past_mirror,
        thirteen_copies,
        coil_two_faces,
    ):
        doc, study, path = build()
        doc.recompute()
        doc.saveAs(path)
        cells = [c.Label for i in objects.symmetric_items(study) for c in symmetry.read_chain(i.Top)[0]]
        print("saved", path, "| cells:", cells)
        mesh(study, doc.Name)
        App.closeDocument(doc.Name)
    if "--challenges" in sys.argv:
        challenges()
