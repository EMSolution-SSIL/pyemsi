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
