"""Swept body recognition tests.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_sweeps.py"""

import math
import unittest

import FreeCAD as App
import Part

from emsolution import sweeps


def face_name(shape, test):
    """The FaceN of shape whose centre of mass passes test."""
    return next(f"Face{k}" for k, f in enumerate(shape.Faces, 1) if test(f.CenterOfMass))


class StraightSweepTest(unittest.TestCase):
    def assertVector(self, a, b):
        for p, q in zip(a, b):
            self.assertAlmostEqual(p, q, places=6)

    def test_box_is_a_straight_sweep(self):
        box = Part.makeBox(10, 4, 40)
        bottom = face_name(box, lambda c: abs(c.z) < 1e-9)
        sweep = sweeps.recognise(box, start_face=bottom)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(sweep.profile, bottom)
        self.assertEqual(sweep.end, face_name(box, lambda c: abs(c.z - 40) < 1e-9))
        self.assertFalse(sweep.closed)
        self.assertEqual(len(sweep.pieces), 1)
        piece = sweep.pieces[0]
        self.assertVector(piece.axis, (0, 0, 1))
        self.assertVector(piece.origin, (5, 2, 0))
        self.assertEqual(piece.angle, 0)
        self.assertAlmostEqual(piece.advance, 40)

    def test_box_without_start_face(self):
        sweep = sweeps.recognise(Part.makeBox(10, 4, 40))
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertAlmostEqual(sweep.pieces[0].advance, 40)  # the longest of the three ways

    def test_round_wire_is_a_straight_sweep(self):
        wire = Part.makeCylinder(0.45, 20)
        sweep = sweeps.recognise(wire)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertAlmostEqual(sweep.pieces[0].advance, 20)
        self.assertEqual(sweep.profile, face_name(wire, lambda c: abs(c.z) < 1e-9))
        self.assertVector(sweep.pieces[0].axis, (0, 0, 1))

    def test_oblique_extrusion(self):
        rect = Part.Face(
            Part.makePolygon([App.Vector(*p) for p in ((0, 0, 0), (6, 0, 0), (6, 4, 0), (0, 4, 0), (0, 0, 0))])
        )
        solid = rect.extrude(App.Vector(3, 0, 40))
        bottom = face_name(solid, lambda c: abs(c.z) < 1e-9)
        sweep = sweeps.recognise(solid, start_face=bottom)
        self.assertIsInstance(sweep, sweeps.Sweep)
        length = math.sqrt(3**2 + 40**2)
        self.assertAlmostEqual(sweep.pieces[0].advance, length)
        self.assertVector(sweep.pieces[0].axis, (3 / length, 0, 40 / length))

    def test_ring_is_not_straight_yet(self):
        ring = Part.makeTorus(10, 2, App.Vector(0, 0, 0), App.Vector(0, 0, 1), 0, 360, 90)
        self.assertEqual(sweeps.recognise(ring), "only straight sweeps are made so far")

    def test_loft_is_refused(self):
        def square(a, z):
            pts = [App.Vector(x, y, z) for x, y in ((-a, -a), (a, -a), (a, a), (-a, a), (-a, -a))]
            return Part.makePolygon(pts)

        loft = Part.makeLoft([square(5, 0), square(2.5, 10)], True, True)
        self.assertEqual(sweeps.recognise(loft), "it has no flat end face that matches another end face moved")

    def test_notched_bar_is_refused(self):
        bar = Part.makeBox(10, 4, 40).cut(Part.makeBox(2, 2, 10, App.Vector(8, 1, 15)))
        self.assertIn(
            sweeps.recognise(bar),
            (
                "a side face does not run straight from one end to the other",
                "its volume is not the start face swept to the end face",
            ),
        )

    def test_two_solids(self):
        boxes = Part.makeCompound([Part.makeBox(10, 4, 40), Part.makeBox(2, 2, 5, App.Vector(20, 0, 0))])
        result = sweeps.recognise_body(boxes)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0].pieces[0].advance, 40)
        self.assertAlmostEqual(result[1].pieces[0].advance, 5)
        mixed = Part.makeCompound([Part.makeBox(10, 4, 40), Part.makeSphere(3, App.Vector(30, 0, 0))])
        self.assertTrue(sweeps.recognise_body(mixed).startswith("solid 2: "))

    def test_start_faces_of_a_compound(self):
        boxes = Part.makeCompound([Part.makeBox(10, 4, 40), Part.makeBox(2, 2, 5, App.Vector(20, 0, 0))])
        side = face_name(boxes, lambda c: c.x > 15 and abs(c.y) < 1e-9)  # the second box's y = 0 face
        result = sweeps.recognise_body(boxes, start_faces=[side])
        self.assertAlmostEqual(result[0].pieces[0].advance, 40)
        self.assertVector(result[1].pieces[0].axis, (0, 1, 0))
        self.assertAlmostEqual(result[1].pieces[0].advance, 2)

    def test_start_face_not_an_end(self):
        wire = Part.makeCylinder(0.45, 20)
        side = next(f"Face{k}" for k, f in enumerate(wire.Faces, 1) if not isinstance(f.Surface, Part.Plane))
        self.assertEqual(sweeps.recognise(wire, start_face=side), f"the start face {side} is not a flat end face of it")
        self.assertEqual(
            sweeps.recognise_body(wire, start_faces=[side]), f"the start face {side} is not a flat end face of it"
        )


if __name__ == "__main__":
    unittest.main()
