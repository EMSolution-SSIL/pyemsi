"""The spike motor as FreeCAD objects, for the Symmetric Mesh tests: a stator cell (0..15 deg) and a rotor cell
(0..22.5 deg), each built up to the full circle the way a user would (Mirror, Polar Array, Boolean Fragments)."""

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


def motor_doc(doc):
    """Build the stator and rotor cells and their full-circle chains in doc."""
    stator_cells = [
        feature(doc, "StatorIronCell", sector(36, 60, 0, 15).cut(sector(37, 50, 10, 15)).Faces[0]),
        feature(doc, "CoilCell", sector(37, 50, 10, 15)),
        feature(doc, "StatorAirCell", sector(35, 36, 0, 15)),
    ]
    rotor_cells = [
        feature(doc, "RotorIronCell", sector(10, 30, 0, 22.5)),
        feature(doc, "MagnetCell", sector(30, 34, 4.5, 22.5)),
        feature(doc, "RotorAirCell", sector(30, 35, 0, 22.5).cut(sector(30, 34, 4.5, 22.5)).Faces[0]),
    ]
    stator_top = chain(doc, "Stator", stator_cells, 15, 12)
    rotor_top = chain(doc, "Rotor", rotor_cells, 22.5, 8)
    return {
        "stator_cells": stator_cells,
        "rotor_cells": rotor_cells,
        "stator_top": stator_top,
        "rotor_top": rotor_top,
    }


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


def motor_study(doc):
    """A 2D Study with sliding motion on motor_doc: Main = stator, Moving = rotor, one Symmetric Mesh item each, a
    Rotational Sliding Interface at R 35 (144 divisions, no Air Region) and a Material per piece group."""
    import json

    from emsolution import objects

    from .materialdata import STEEL, record

    info = motor_doc(doc)
    study = objects.make_study(doc, "2D")
    study.MainMode, study.MainObjects = "Manual", [info["stator_top"]]
    study.MovingMode, study.MovingObjects = "Manual", [info["rotor_top"]]
    study.Movement = "Sliding motion"
    for top in (info["stator_top"], info["rotor_top"]):
        objects.make_symmetric_mesh(study, top)
    objects.make_sliding_interface(study, "Rotational", Radius=35, Divisions=144)
    lib = objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL)))
    groups = {}
    for part, top in (("Stator", info["stator_top"]), ("Rotor", info["rotor_top"])):
        for i, face in enumerate(top.Shape.Faces):
            groups.setdefault(_piece_name(face, part), []).append((top, f"Face{i + 1}"))
    for name in sorted(groups):
        objects.assign_pieces(study, name, groups[name], lib, 0)
    doc.recompute()
    return study
