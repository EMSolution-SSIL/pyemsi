"""The spike motor as FreeCAD objects, for the Symmetric Group tests: a stator cell (0..15 deg) and a rotor cell
(0..22.5 deg), as Studies of Symmetric Groups (motor_study), or built up to the full circle the way a user draws it
(Mirror, Polar Array, Boolean Fragments: motor_doc) for the reading helper."""

import math

import FreeCAD as App
import Part
import Draft
import BOPTools.SplitFeatures

V = App.Vector


def sector(r1, r2, a1, a2):
    """Annular sector face, radii r1..r2, angles a1..a2 deg."""

    def p(r, a):
        return V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0)

    am = (a1 + a2) / 2
    edges = [
        Part.Arc(p(r2, a1), p(r2, am), p(r2, a2)).toShape(),
        Part.LineSegment(p(r2, a2), p(r1, a2)).toShape(),
        Part.Arc(p(r1, a2), p(r1, am), p(r1, a1)).toShape(),
        Part.LineSegment(p(r1, a1), p(r2, a1)).toShape(),
    ]
    return Part.Face(Part.Wire(edges))


def feature(doc, name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def chain(doc, part, cells, mirror_deg, count):
    """Cell compound -> mirror about the line at mirror_deg -> compound -> polar array -> fragments."""
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
    frag = BOPTools.SplitFeatures.makeBooleanFragments(name=f"{part}Fragments")
    frag.Objects = [array]
    doc.recompute()
    return frag


def motor_cells(doc, height=0):
    """The stator and rotor cell objects, no chain objects. height > 0 extrudes every cell face 0..height in z."""

    def cell(name, face):
        return feature(doc, name, face.extrude(V(0, 0, height)) if height else face)

    stator_cells = [
        cell("StatorIronCell", sector(36, 60, 0, 15).cut(sector(37, 50, 10, 15)).Faces[0]),
        cell("CoilCell", sector(37, 50, 10, 15)),
        cell("StatorAirCell", sector(35, 36, 0, 15)),
    ]
    rotor_cells = [
        cell("RotorIronCell", sector(10, 30, 0, 22.5)),
        cell("MagnetCell", sector(30, 34, 4.5, 22.5)),
        cell("RotorAirCell", sector(30, 35, 0, 22.5).cut(sector(30, 34, 4.5, 22.5)).Faces[0]),
    ]
    return stator_cells, rotor_cells


def group_motor_doc(doc, height=0):
    """motor_doc's cell objects with no chain objects: the cells a Symmetric Group is made of."""
    stator_cells, rotor_cells = motor_cells(doc, height)
    doc.recompute()
    return {"stator_cells": stator_cells, "rotor_cells": rotor_cells}


def motor_doc(doc, height=0):
    """Build the stator and rotor cells and their full-circle chains in doc. height > 0 extrudes every cell face
    0..height in z, so the cells are solids (a 3D drawing)."""
    stator_cells, rotor_cells = motor_cells(doc, height)
    stator_top = chain(doc, "Stator", stator_cells, 15, 12)
    rotor_top = chain(doc, "Rotor", rotor_cells, 22.5, 8)
    return {
        "stator_cells": stator_cells,
        "rotor_cells": rotor_cells,
        "stator_top": stator_top,
        "rotor_top": rotor_top,
    }


def motor_doc_3d(doc, height=10):
    """motor_doc with every cell face extruded 0..height in z: the same chains, built from solids."""
    return motor_doc(doc, height)


def coil_fragments(doc, radius=43):
    """A Boolean Fragments of CoilCell and an arc across it at radius: the coil cut into an inner and an outer block."""

    def p(a):
        return V(radius * math.cos(math.radians(a)), radius * math.sin(math.radians(a)), 0)

    coil = doc.getObject("CoilCell")
    divider = feature(doc, "CoilDivider", Part.Arc(p(10), p(12.5), p(15)).toShape())
    frag = BOPTools.SplitFeatures.makeBooleanFragments(name="CoilFragments")
    frag.Objects = [coil, divider]
    frag.Mode = "Standard"
    doc.recompute()
    return frag


def split_coil(doc, radius=43):
    """Cut motor_doc's CoilCell into an inner and an outer block at radius, the way a user does: a Boolean Fragments
    of the coil face and an arc across it, put in the stator cell in the coil's place. Returns the Fragments."""
    coil = doc.getObject("CoilCell")
    frag = coil_fragments(doc, radius)
    cell = doc.getObject("StatorCell")
    cell.Links = [frag if o.Name == coil.Name else o for o in cell.Links]
    doc.recompute()
    return frag


def _polygon(*points):
    return Part.Face(Part.makePolygon([V(x, y, 0) for x, y in points + points[:1]]))


TRANSFORMER_RULES = [
    {"kind": "mirror", "point": [0, 0, 0], "normal": [0, 1, 0]},
    {"kind": "mirror", "point": [0, 0, 0], "normal": [1, 0, 0]},
]  # the quarter x, y >= 0 mirrored at y = 0, then at x = 0


def transformer_doc(doc):
    """A quarter of a transformer drawn as a user did (D-01): the core is a Boolean Fragments of its face (x 0..42,
    y 0..32, the window x 13..32, y 0..22 cut out) and two lines from the window's top corners to the outer corners, so
    one object of three faces, each with four corners; the coil x 15..30, y 0..20 and the air of the window around
    it. Returns {"core", "coil", "air"}; copy them with TRANSFORMER_RULES."""
    core = feature(doc, "CoreFace", _polygon((0, 0), (13, 0), (13, 22), (32, 22), (32, 0), (42, 0), (42, 32), (0, 32)))
    lines = [Part.LineSegment(V(0, 32, 0), V(13, 22, 0)), Part.LineSegment(V(32, 22, 0), V(42, 32, 0))]
    cuts = feature(doc, "CoreCuts", Part.makeCompound([line.toShape() for line in lines]))
    frag = BOPTools.SplitFeatures.makeBooleanFragments(name="CoreCell")
    frag.Objects = [core, cuts]
    frag.Mode = "Standard"
    coil = feature(doc, "CoilCell", _polygon((15, 0), (30, 0), (30, 20), (15, 20)))
    window = _polygon((13, 0), (32, 0), (32, 22), (13, 22))
    air = feature(doc, "AirCell", window.cut(coil.Shape).Faces[0])
    for obj in (core, cuts):
        obj.Visibility = False
    doc.recompute()
    return {"core": frag, "coil": coil, "air": air}


def _piece_name(face, part):
    """The assignment a face of the full stator or rotor belongs to, from where its centre lies (radius, angle)."""
    c = face.CenterOfMass
    r, a = math.hypot(c.x, c.y), math.degrees(math.atan2(c.y, c.x)) % 360
    if part == "Stator":  # air 35..36, coil 37..50 (a slot is 30 deg wide), iron outside
        if r < 36:
            return "StatorAir"
        return f"Coil{int(a // 30) + 1:02d}" if r < 46 else "StatorIron"
    if r < 30:  # iron to 30, magnet 30..34 (a pole is 45 deg wide), air outside
        return "RotorIron"
    return "Magnet" + "NS"[int(a // 45) % 2] if r < 32.5 else "RotorAir"


def mirror_rule(deg):
    """Mirror in the plane through Z at deg degrees, as Part Mirror does with the normal (-sin, cos, 0)."""
    return {
        "kind": "mirror",
        "point": [0, 0, 0],
        "normal": [-math.sin(math.radians(deg)), math.cos(math.radians(deg)), 0],
    }


def rotate_rule(step, count):
    return {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": step, "count": count}


STATOR_RULES = [mirror_rule(15), rotate_rule(30, 12)]  # the rules of chain(doc, "Stator", ..., 15, 12)
ROTOR_RULES = [mirror_rule(22.5), rotate_rule(45, 8)]


def name_parts(item, part):
    """Every row of group item becomes a table: each copy is named as _piece_name names its place in the drawing."""
    from emsolution import objects

    rows = []
    for row in objects.rows_of(item):
        shape = objects.row_shape(item, row)
        names = [_piece_name(shape.transformed(App.Matrix(*t)), part) for t in objects.group_transforms(item)]
        rows.append({**row, "mode": "table", "table": names})
    objects.set_rows(item, rows)


def _groups_study(doc, dimension, height=0):
    """motor_cells in a Study with sliding motion: the stator and the rotor each a Symmetric Group with the rules of
    their chain (motor_doc), parts named as the old piece groups were, a Rotational Sliding Interface at R 35 (144
    divisions, no Air Region) and the library material Steel on every part."""
    import json

    from emsolution import objects

    from .materialdata import STEEL, record

    stator_cells, rotor_cells = motor_cells(doc, height)
    doc.recompute()
    study = objects.make_study(doc, dimension)
    study.Movement = "Sliding motion"
    lib = objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL)))
    for part, cells, rules, side in (
        ("Stator", stator_cells, STATOR_RULES, "Fixed"),
        ("Rotor", rotor_cells, ROTOR_RULES, "Moving"),
    ):
        item = objects.make_symmetric_group(study, cells, rules=rules, name=part, side=side)
        name_parts(item, part)
        for r in range(len(cells)):
            objects.set_row_material(study, item, r, lib)
    objects.sync_parts(study)
    doc.recompute()
    return study


def motor_study(doc):
    """A 2D Study with sliding motion: the stator and rotor cells as two Symmetric Groups (Fixed and Moving) with the
    rules of their chains, a Rotational Sliding Interface at R 35 (144 divisions, no Air Region) and a Material per
    part."""
    from emsolution import objects

    study = _groups_study(doc, "2D")
    objects.make_sliding_interface(study, "Rotational", Radius=35, Divisions=144)
    doc.recompute()
    return study


def motor_study_3d(doc, height=10):
    """motor_study with every cell extruded 0..height in z: a 3D Study, and the Excitation Coil01Ends on the two faces
    of the drawing at z = height of the Coil01 copies."""
    from emsolution import objects

    study = _groups_study(doc, "3D", height)
    study.MeshSizesGroup.DefaultMeshSize = 1.5  # finer than the thinnest cell (air, 1.7 mm): no coarse-mesh warning
    objects.make_sliding_interface(study, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    stator = objects.symmetric_groups(study)[0]
    ends = [
        (stator, f"Face{i + 1}")
        for i, face in enumerate(stator.Shape.Faces)
        if abs(face.CenterOfMass.z - height) < 1e-6 and _piece_name(face, "Stator") == "Coil01"
    ]
    objects.make_excitation(study, "Coil01Ends", ends)
    doc.recompute()
    return study


# ---- Studies built from code and meshed: the success list and test_rules_end_to_end


def extruded(face, z0, z1):
    """face (drawn at z = 0) as a solid from z0 to z1."""
    return face.translated(V(0, 0, z0)).extrude(V(0, 0, z1 - z0))


def libraries(study):
    """Steel, Copper and Air in the Study's library: {name: library material}."""
    import json

    from emsolution import objects

    from .materialdata import AIR, COPPER, STEEL, record

    out = {}
    for key, name, family, props in (
        ("steel", "Steel", "electrical_steel", STEEL),
        ("copper", "Copper", "conductor", COPPER),
        ("air", "Air", "fluid_or_gas", AIR),
    ):
        out[name] = objects.make_library_material(study, json.dumps(record(f"user:{key}", name, family, props)))
    return out


def group(study, name, cells, rules, rows=None, side="Fixed", lib=None):
    """A Symmetric Group of cells copied by rules. rows: {cell Name: row changes} (such as {"mode": "each"}, or a
    function of the item and the row's index giving them); lib: {cell Name: library material}. The cells are hidden."""
    from emsolution import objects

    study.Document.recompute()
    item = objects.make_symmetric_group(study, cells, rules=rules, name=name, side=side)
    out = []
    for r, row in enumerate(objects.rows_of(item)):
        change = (rows or {}).get(row["cell"], {})
        out.append({**row, **(change(item, r) if callable(change) else change)})
    objects.set_rows(item, out)
    for r, row in enumerate(out):
        if lib and row["cell"] in lib:
            objects.set_row_material(study, item, r, lib[row["cell"]])
    for cell in cells:
        cell.Visibility = False
    study.Document.recompute()
    return item


def add_free(study, name, shape, lib=None):
    """A body meshed normally, beside the copies, with a Material of lib. It moves when it is on the moving side of
    the Sliding Interface."""
    from emsolution import objects

    body = feature(study.Document, name, shape)
    if lib is not None:
        objects.assign(study, [body], lib, 0)
    study.Document.recompute()
    return body


def add_air_region(study, lib=None, shape=None, **props):
    """The Study's Air Region. With shape: a feature AirShape (in no geometry) and a Custom Air Region on it; else an
    AirShape (props, default Box) Air Region sized by props. With lib, a Material of lib named Air."""
    from emsolution import objects

    if shape is not None:
        source = feature(study.Document, "AirShape", shape)
        air = objects.make_air_region(study, "Custom", Source=source, **props)
    else:
        air = objects.make_air_region(study, props.pop("AirShape", "Box"), **props)
    if lib is not None:
        objects.assign(study, [air], lib, 0, name="Air")
    study.Document.recompute()
    return air


def transfinite_layer(study, body, arcs, ups, across=1):
    """Make body (an annular sector solid about Z) structured and recombined: arcs elements along its arcs, across
    elements from radius to radius, ups along Z."""
    from emsolution import objects

    by = {"arc": [], "across": [], "up": []}
    for i, e in enumerate(body.Shape.Edges, 1):
        d = e.Vertexes[-1].Point - e.Vertexes[0].Point
        kind = "arc" if isinstance(e.Curve, Part.Circle) else "up" if abs(d.z) > 1e-9 else "across"
        by[kind].append((body, f"Edge{i}"))
    for kind, n in (("arc", arcs), ("across", across), ("up", ups)):
        objects.make_transfinite_edges(study, n, by[kind]).Label = f"{body.Label} {kind} {n}"
    objects.make_transfinite_body(study, [body])
    objects.make_recombine(study, [body])


def finish(study, path):
    """Give every part its Material (sync_parts) and save the document at path."""
    import os

    from emsolution import objects

    objects.sync_parts(study)
    study.Document.recompute()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    study.Document.saveAs(path)


def mesh_and_read(study, timeout=None):
    """Write the job, run the mesher on it and read the mesh files back (read_mesh). Returns read_mesh's namespace
    with ok, refused (the mesher's last error line when it stopped), poor [(part, poor, elements)] as the mesher
    reports them, and seconds."""
    import os
    import subprocess
    import sys
    import time
    import types

    from emsolution import jobwriter

    start = time.time()
    path = jobwriter.write_job(study)
    mesher = "mesher2d.py" if study.Dimension == "2D" else "mesher.py"
    r = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(jobwriter.__file__), mesher), path],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if r.returncode:
        lines = [x for x in r.stderr.splitlines() if x.strip()]
        refused = lines[-1] if lines else f"the mesher stopped with {r.returncode}"
        return types.SimpleNamespace(ok=False, refused=refused, seconds=time.time() - start)
    out = read_mesh(study)
    out.ok, out.refused, out.poor = True, "", []
    for line in r.stderr.splitlines():
        if line.startswith("NOTE: Poor elements"):
            name, poor, _, total = line[len("NOTE: Poor elements") :].split()[:4]
            out.poor.append((name, int(poor), int(total)))
    out.seconds = time.time() - start
    return out


def read_mesh(study):
    """The mesh files of a meshed Study read back (meshreport.quality), as a namespace: types {type name: count},
    inverted, faces_in_three, kept (facets of the copies' surface that the elements of free objects share), lost
    (facets of the copies' surface that face the inside of a free object or the Air Region but no element of it: a
    frozen face not kept) and frozen_kept (none lost)."""
    import collections
    import types

    import numpy as np

    from emsolution import geometry, jobwriter, objects, sides

    from . import meshreport

    out = types.SimpleNamespace(types={}, inverted=0, faces_in_three=0, kept=0, lost=0)
    sliding = study.Movement == "Sliding motion"
    files = {"fixed": jobwriter.mesh_file(study)}
    if sliding:
        files["moving"] = jobwriter.rotor_file(study)
    on_moving = sides.moving(study)
    free = geometry.study_geometry(study)[0]
    copied = collections.defaultdict(set)  # side -> MAT_IDs of the parts of the copies
    for m in objects.part_assignments(study):
        copied[m.PartKey.partition("|")[0]].add(int(study.MatIds[m.Name]))
    found = collections.Counter()
    for side, msh in files.items():
        q = meshreport.quality(msh, copied[side])
        found.update(q["types"])
        out.inverted += q["inverted"]
        out.faces_in_three += q["faces_in_three"]
        out.kept += q["kept"]
        shapes = [geometry.global_shape(b) for b in free if (b.Name in on_moving) == (side == "moving")]
        # the Air Region is meshed in the fixed side's free job. Its shape holds the copies, so its probe goes half a
        # facet out: a facet of a copy on the air's curved outer boundary (a chord) lies inside it by the sagitta
        airs = [geometry.global_shape(a) for a in objects.air_regions(study)] if side == "fixed" else []
        mats, centres, normals, sizes = q["boundary"]
        mine = np.isin(mats, sorted(copied[side])) if len(mats) else np.zeros(0, dtype=bool)
        for c, n, h in zip(centres[mine], normals[mine], sizes[mine]):
            probe, far = V(*(c + 1e-3 * h * n)), V(*(c + 0.5 * h * n))
            out.lost += any(_inside(s, probe) for s in shapes) or any(_inside(s, far) for s in airs)
    out.types = dict(found)
    out.frozen_kept = out.lost == 0
    return out


def _inside(shape, p, tol=1e-9):
    """True when p lies strictly inside the solids of shape (3D), or on its faces (2D)."""
    box = shape.BoundBox
    if not (box.XMin - tol <= p.x <= box.XMax + tol and box.YMin - tol <= p.y <= box.YMax + tol):
        return False
    if not box.ZMin - tol <= p.z <= box.ZMax + tol:
        return False
    if shape.Solids:
        return any(s.isInside(p, tol, False) for s in shape.Solids)
    return shape.distToShape(Part.Vertex(p))[0] < tol
