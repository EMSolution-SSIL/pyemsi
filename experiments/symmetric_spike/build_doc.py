"""SPIKE (throwaway): build a 2D 12-slot / 8-pole motor in FreeCAD the way a user would, from cells.

    stator cell 0..15 deg:   half tooth + half slot: StatorIronCell, CoilCell, StatorAirCell (air gap 35..36)
    rotor cell  0..22.5 deg: half pole: RotorIronCell, MagnetCell, RotorAirCell (30..35 around the magnet)

    chain per part:  cell compound -> Part Mirror -> compound (cell + mirror) -> Draft Polar Array
                     -> Boolean Fragments -> Explode compound: one object per piece

Each exploded piece gets a string property "Material" (stand-in for the add-on's Material, which today links one
body: here many bodies can share one name). Two groups SymMesh_Stator / SymMesh_Rotor stand in for the new
"Symmetric Mesh" item: Cell (the cell bodies) and Steps (one line per step, applied in order).

    pixi run -e addon python experiments/symmetric_spike/build_doc.py   -> experiments/symmetric_spike/motor2d.FCStd
"""

import math
import os

import FreeCAD as App
import Part
import Draft
import BOPTools.SplitFeatures
import CompoundTools.Explode

HERE = os.path.dirname(os.path.abspath(__file__))
V = App.Vector


def sector(r1, r2, a1, a2):
    """Annular sector face, radii r1..r2, angles a1..a2 deg."""
    p = lambda r, a: V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0)  # noqa: E731
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
    """Cell compound -> mirror about the line at mirror_deg -> compound -> polar array -> fragments -> explode."""
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
    # finding: one Explode only splits off the array copies (each still a compound of cell + mirror). A user has
    # to explode again, level by level, until each object is one face.
    todo, pieces = [frag], []
    while todo:
        obj = todo.pop(0)
        if len(obj.Shape.Faces) == 1:
            pieces.append(obj)
            continue
        todo += CompoundTools.Explode.explodeCompound(obj)[1]
        doc.recompute()
    return pieces


def main():
    doc = App.newDocument("motor2d")
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
    stator = chain(doc, "Stator", stator_cells, 15, 12)
    rotor = chain(doc, "Rotor", rotor_cells, 22.5, 8)

    kinds = {round(c.Shape.Area, 6): c.Name.replace("Cell", "") for c in stator_cells + rotor_cells}
    for obj in stator + rotor:  # what the user would do by hand: give every piece its material
        obj.addProperty("App::PropertyString", "Material", "SPIKE")
        c = obj.Shape.Faces[0].CenterOfMass
        a = math.degrees(math.atan2(c.y, c.x)) % 360
        kind = kinds[round(obj.Shape.Area, 6)]  # every piece is a copy of one cell body
        if kind == "Coil":
            kind = f"Coil{int(a // 30) + 1:02d}"  # the two halves of slot k lie in 30k..30k+30 deg
        elif kind == "Magnet":
            kind += "NS"[int(a // 45) % 2]
        obj.Material = kind
        obj.Label = f"{obj.Material}_{obj.Name}"

    for part, cells, steps in (
        ("Stator", stator_cells, ["mirror 0 0 15", "rotate 0 0 30 12"]),
        ("Rotor", rotor_cells, ["mirror 0 0 22.5", "rotate 0 0 45 8"]),
    ):
        sym = doc.addObject("App::FeaturePython", f"SymMesh_{part}")
        sym.addProperty("App::PropertyLinkList", "Cell", "SPIKE", "Cell bodies: the only ones meshed")
        sym.addProperty("App::PropertyStringList", "Steps", "SPIKE", "mirror x y deg | rotate x y deg count")
        sym.Cell, sym.Steps = cells, steps
    doc.recompute()
    path = os.path.join(HERE, "motor2d.FCStd")
    doc.saveAs(path)
    for o in doc.Objects:
        print(f"{o.Name:24s} {o.TypeId:28s} faces={len(o.Shape.Faces) if hasattr(o, 'Shape') else '-':>3}  {o.Label}")
    print("saved", path)


main()
