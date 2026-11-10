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
