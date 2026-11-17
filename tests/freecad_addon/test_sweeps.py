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
        self.assertTrue(sweep.face.isSame(box.getElement(bottom)))
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

    def test_ring_quarter_is_revolved(self):
        ring = Part.makeTorus(10, 2, App.Vector(0, 0, 0), App.Vector(0, 0, 1), 0, 360, 90)
        sweep = sweeps.recognise(ring)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertAlmostEqual(sweep.pieces[0].angle, 90)

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


V = App.Vector


def rect_xz(x0, x1, z0, z1):
    """A rectangle in the xz plane."""
    return Part.Face(Part.makePolygon([V(x0, 0, z0), V(x1, 0, z0), V(x1, 0, z1), V(x0, 0, z1), V(x0, 0, z0)]))


class RevolvedSweepTest(unittest.TestCase):
    def assertRevolved(self, sweep, angle):
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(len(sweep.pieces), 1)
        piece = sweep.pieces[0]
        self.assertAlmostEqual(piece.angle, angle, places=6)
        self.assertEqual(piece.advance, 0.0)
        self.assertAlmostEqual(abs(piece.axis[2]), 1, places=6)  # about z
        self.assertAlmostEqual(math.hypot(piece.origin[0], piece.origin[1]), 0, places=6)  # on the z axis
        return piece

    def assertTurnsOnto(self, sweep, solid):
        """The piece's turn by a positive angle maps the start face onto the end face."""
        piece = sweep.pieces[0]
        moved = sweep.face.copy()
        moved.rotate(V(*piece.origin), V(*piece.axis), piece.angle)
        self.assertLess(moved.CenterOfMass.distanceToPoint(solid.getElement(sweep.end).CenterOfMass), 1e-6)
        half = sweep.face.copy()  # half way round is inside the body
        half.rotate(V(*piece.origin), V(*piece.axis), piece.angle / 2)
        self.assertTrue(solid.isInside(half.CenterOfMass, 1e-6, False))

    def test_quarter_ring_is_revolved(self):
        ring = Part.makeTorus(20, 3, V(0, 0, 0), V(0, 0, 1), -180, 180, 90)
        sweep = sweeps.recognise(ring)
        self.assertRevolved(sweep, 90)
        self.assertFalse(sweep.closed)
        self.assertAlmostEqual(sweep.face.Area, math.pi * 9, places=6)
        self.assertTurnsOnto(sweep, ring)

    def test_rect_bend_is_revolved(self):
        bend = rect_xz(20, 30, -2, 2).revolve(V(0, 0, 0), V(0, 0, 1), 90)
        sweep = sweeps.recognise(bend)
        self.assertRevolved(sweep, 90)
        self.assertAlmostEqual(sweep.face.Area, 40, places=6)
        self.assertTurnsOnto(sweep, bend)

    def test_long_way_round(self):
        for angle in (180, 270):
            with self.subTest(angle=angle):
                bend = rect_xz(20, 30, -2, 2).revolve(V(0, 0, 0), V(0, 0, 1), angle)
                sweep = sweeps.recognise(bend)
                self.assertRevolved(sweep, angle)
                self.assertTurnsOnto(sweep, bend)

    def test_start_face_of_a_bend(self):
        bend = rect_xz(20, 30, -2, 2).revolve(V(0, 0, 0), V(0, 0, 1), 90)
        end = face_name(bend, lambda c: abs(c.x) < 1e-9)  # the face at 90 degrees
        sweep = sweeps.recognise(bend, start_face=end)
        self.assertEqual(sweep.profile, end)
        self.assertRevolved(sweep, 90)
        self.assertTurnsOnto(sweep, bend)

    def test_closed_torus_is_a_ring(self):
        sweep = sweeps.recognise(Part.makeTorus(20, 3))
        piece = self.assertRevolved(sweep, 360)
        self.assertTrue(sweep.closed)
        self.assertIsNone(sweep.profile)
        self.assertIsNone(sweep.end)
        self.assertAlmostEqual(sweep.face.Area, math.pi * 9, places=4)
        self.assertAlmostEqual(piece.origin[2], 0, places=6)

    def test_closed_rect_ring(self):
        ring = rect_xz(20, 30, -2, 2).revolve(V(0, 0, 0), V(0, 0, 1), 360)
        sweep = sweeps.recognise(ring)
        self.assertRevolved(sweep, 360)
        self.assertTrue(sweep.closed)
        face = sweep.face
        self.assertAlmostEqual(face.Area, 40, places=6)
        u0, u1, v0, v1 = face.ParameterRange
        normal = face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)  # in a plane through the axis
        self.assertAlmostEqual(normal.z, 0, places=6)
        self.assertAlmostEqual(normal.dot(face.CenterOfMass), 0, places=6)
        seam = [e for e in ring.Edges if isinstance(e.Curve, Part.Line)]  # the cut holds a seam vertex
        self.assertTrue(seam)
        corner = seam[0].Vertexes[0].Point
        self.assertTrue(any(v.Point.distanceToPoint(corner) < 1e-6 for v in face.Vertexes))

    def test_l_block_is_not_revolved(self):
        outline = [V(0, 0, 0), V(10, 0, 0), V(10, 4, 0), V(4, 4, 0), V(4, 10, 0), V(0, 10, 0), V(0, 0, 0)]
        block = Part.Face(Part.makePolygon(outline)).extrude(V(0, 0, 30))
        sweep = sweeps.recognise(block)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(sweep.pieces[0].angle, 0)
        self.assertAlmostEqual(sweep.pieces[0].advance, 30)
        cube = sweeps.recognise(Part.makeBox(10, 10, 10))  # equal faces at right angles everywhere
        self.assertEqual(cube.pieces[0].angle, 0)

    def test_cone_frustum_ring(self):
        pts = [V(20, 0, -2), V(30, 0, -1), V(30, 0, 1), V(20, 0, 2), V(20, 0, -2)]
        ring = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), V(0, 0, 1), 360)
        self.assertTrue(any(isinstance(f.Surface, Part.Cone) for f in ring.Faces))
        sweep = sweeps.recognise(ring)
        self.assertRevolved(sweep, 360)
        self.assertTrue(sweep.closed)
        self.assertAlmostEqual(sweep.face.Area, 30, places=6)

    def test_sphere_is_refused(self):
        self.assertIsInstance(sweeps.recognise(Part.makeSphere(5)), str)

    def test_faces_not_about_one_axis(self):
        crossed = Part.makeTorus(20, 3).fuse(Part.makeTorus(20, 3, V(0, 0, 0), V(1, 0, 0)))  # two rings, two axes
        self.assertEqual(len(crossed.Solids), 1)
        self.assertEqual(sweeps.recognise(crossed.Solids[0]), "its faces do not all turn about one axis")

    def test_helix_still_refused(self):
        helix = Part.makeHelix(10, 25, 20)
        circle = Part.Wire(Part.makeCircle(2, V(20, 0, 0), V(0, 1, 0)))
        pipe = Part.Wire(helix).makePipeShell([circle], True, True)
        self.assertEqual(pipe.ShapeType, "Solid")
        self.assertEqual(sweeps.recognise(pipe), "only straight and revolved sweeps are made so far")


if __name__ == "__main__":
    unittest.main()
