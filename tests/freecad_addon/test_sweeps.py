"""Swept body recognition tests.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_sweeps.py"""

import math
import unittest
from unittest import mock

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

    def test_helix_pipe_is_a_helix(self):
        sweep = sweeps.recognise(helix_pipe(10, 25, 20, ("circle", 2)))
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(len(sweep.pieces), 1)
        self.assertAlmostEqual(sweep.pieces[0].angle, 900, places=4)
        self.assertAlmostEqual(abs(sweep.pieces[0].advance), 25, places=5)

    def test_whole_turn_helix_is_a_helix(self):
        for height in (20, 30):  # ends exactly opposite: a translation matches them too
            with self.subTest(height=height):
                sweep = sweeps.recognise(helix_pipe(10, height, 20, ("circle", 2)))
                self.assertIsInstance(sweep, sweeps.Sweep)
                self.assertAlmostEqual(sweep.pieces[0].angle, 36 * height, places=4)
                self.assertAlmostEqual(abs(sweep.pieces[0].advance), height, places=5)

    def test_bulged_wire_keeps_side_face(self):
        pts = [V(0, 0, 0), V(3, 0, 0), V(5, 0, 10), V(3, 0, 20), V(0, 0, 20), V(0, 0, 0)]
        barrel = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), V(0, 0, 1), 360)
        self.assertEqual(sweeps.recognise(barrel), "a side face does not run straight from one end to the other")


def helix_pipe(pitch, height, radius, profile, frenet=True, left=False):
    """A PartDesign pipe along a Part Helix about z from (radius, 0, 0), made as litz1 was: the profile sketch
    attached FrenetNB to the helix start. profile: ("circle", r) or ("rect", w, h). frenet False: PartDesign's default
    Standard mode, whose profile turns about the path."""
    import Sketcher  # noqa: F401 - registers Sketcher::SketchObject
    import PartDesign  # noqa: F401 - registers PartDesign::AdditivePipe

    doc = App.newDocument("HelixPipe")
    try:
        helix = doc.addObject("Part::Helix", "Helix")
        helix.Pitch, helix.Height, helix.Radius = pitch, height, radius
        helix.LocalCoord = "Left-handed" if left else "Right-handed"
        body = doc.addObject("PartDesign::Body", "Body")
        body.BaseFeature = helix
        doc.recompute()
        base = body.Group[0]
        sketch = body.newObject("Sketcher::SketchObject", "Sketch")
        sketch.AttachmentSupport = [(base, ("Edge1",))]
        sketch.MapMode = "FrenetNB"
        if profile[0] == "circle":
            sketch.addGeometry(Part.Circle(V(0, 0, 0), V(0, 0, 1), profile[1]))
        else:
            w, h = profile[1] / 2, profile[2] / 2
            corners = [V(-w, -h, 0), V(w, -h, 0), V(w, h, 0), V(-w, h, 0)]
            for p, q in zip(corners, corners[1:] + corners[:1]):
                sketch.addGeometry(Part.LineSegment(p, q))
        pipe = body.newObject("PartDesign::AdditivePipe", "Pipe")
        pipe.Profile = sketch
        pipe.Spine = (base, ["Edge1"])
        pipe.Mode = "Frenet" if frenet else "Standard"
        pipe.Refine = True
        doc.recompute()
        return pipe.Shape.Solids[0].copy()
    finally:
        App.closeDocument(doc.Name)


def padded_busbar():
    """A bent busbar made as a Pad is: the plan of a band 10 wide along line 30 + arc r 20, 90 deg + line 30,
    extruded 4. Its top and bottom are single flat faces across all three pieces."""
    outline = Part.Wire(
        [
            Part.makeLine(V(0, -5, 0), V(30, -5, 0)),
            Part.Arc(V(30, -5, 0), V(30 + 25 * math.sqrt(0.5), 20 - 25 * math.sqrt(0.5), 0), V(55, 20, 0)).toShape(),
            Part.makeLine(V(55, 20, 0), V(55, 50, 0)),
            Part.makeLine(V(55, 50, 0), V(45, 50, 0)),
            Part.makeLine(V(45, 50, 0), V(45, 20, 0)),
            Part.Arc(V(45, 20, 0), V(30 + 15 * math.sqrt(0.5), 20 - 15 * math.sqrt(0.5), 0), V(30, 5, 0)).toShape(),
            Part.makeLine(V(30, 5, 0), V(0, 5, 0)),
            Part.makeLine(V(0, 5, 0), V(0, -5, 0)),
        ]
    )
    return Part.Face(outline).extrude(V(0, 0, 4))


def end_faces(solid):
    """(start, end) face names: the planar faces, the one nearer the origin first."""
    flat = [(f.CenterOfMass.Length, k) for k, f in enumerate(solid.Faces, 1) if isinstance(f.Surface, Part.Plane)]
    return tuple(f"Face{k}" for _, k in sorted(flat))


class HelixAndChainTest(unittest.TestCase):
    def assertHelix(self, sweep, angle, advance):
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(len(sweep.pieces), 1)
        piece = sweep.pieces[0]
        self.assertAlmostEqual(piece.angle, angle, places=4)
        self.assertAlmostEqual(piece.advance, advance, places=5)
        self.assertAlmostEqual(abs(piece.axis[2]), 1, places=6)  # along the helix axis z
        self.assertAlmostEqual(math.hypot(piece.origin[0], piece.origin[1]), 0, places=5)  # on it
        return piece

    def assertScrewsOnto(self, sweep, solid):
        """Each piece's screw motion maps its start section onto the next; the last one lands on the end face."""
        face = sweep.face.copy()
        for piece in sweep.pieces:
            face.rotate(V(*piece.origin), V(*piece.axis), piece.angle)
            face.translate(V(*piece.axis) * piece.advance)
        end = solid.getElement(sweep.end)
        self.assertLess(face.CenterOfMass.distanceToPoint(end.CenterOfMass), 1e-5)

    def test_helix_strand_is_a_helix(self):
        strand = helix_pipe(10, 15, 1.2, ("circle", 0.45))
        start, _ = end_faces(strand)
        sweep = sweeps.recognise(strand, start_face=start)
        piece = self.assertHelix(sweep, 540, 15)
        self.assertGreater(piece.axis[2], 0)  # right-handed: turns positively about +z while it rises
        self.assertFalse(sweep.rebuild)  # a Frenet pipe's seam follows the screw
        self.assertScrewsOnto(sweep, strand)

    def test_left_handed_helix(self):
        strand = helix_pipe(10, 15, 1.2, ("circle", 0.45), left=True)
        start, _ = end_faces(strand)
        sweep = sweeps.recognise(strand, start_face=start)
        self.assertIsInstance(sweep, sweeps.Sweep)
        piece = sweep.pieces[0]
        self.assertAlmostEqual(piece.angle, 540, places=4)
        self.assertAlmostEqual(piece.axis[2], -1, places=6)  # a positive turn about -z
        self.assertAlmostEqual(piece.advance, -15, places=5)  # the rise is along -axis
        self.assertScrewsOnto(sweep, strand)

    def test_whole_turn_coil_is_a_helix(self):
        coil = helix_pipe(6, 6, 20, ("rect", 2, 4))
        start, _ = end_faces(coil)
        sweep = sweeps.recognise(coil, start_face=start)
        self.assertHelix(sweep, 360, 6)
        self.assertScrewsOnto(sweep, coil)
        self.assertAlmostEqual(sweeps.recognise(coil).pieces[0].angle, 360, places=4)  # without a start face

    def test_bent_busbar_is_a_chain(self):
        path = Part.Wire(
            [
                Part.makeLine(V(0, 0, 0), V(30, 0, 0)),
                Part.Edge(Part.ArcOfCircle(Part.Circle(V(30, 20, 0), V(0, 0, 1), 20), -math.pi / 2, 0)),
                Part.makeLine(V(50, 20, 0), V(50, 50, 0)),
            ]
        )
        profile = Part.makePolygon([V(0, y, z) for y, z in ((-5, -2), (5, -2), (5, 2), (-5, 2), (-5, -2))])
        bar = path.makePipeShell([profile], True, True)
        start = face_name(bar, lambda c: abs(c.x) < 1e-9)
        sweep = sweeps.recognise(bar, start_face=start)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(sweep.end, face_name(bar, lambda c: abs(c.y - 50) < 1e-9))
        self.assertFalse(sweep.rebuild)
        first, arc, last = sweep.pieces
        self.assertEqual((first.angle, last.angle), (0, 0))
        self.assertAlmostEqual(first.advance, 30)
        self.assertAlmostEqual(last.advance, 30)
        for p, q in zip(first.axis + last.axis, (1, 0, 0, 0, 1, 0)):
            self.assertAlmostEqual(p, q, places=6)
        self.assertAlmostEqual(arc.angle, 90, places=6)
        self.assertEqual(arc.advance, 0.0)
        for p, q in zip(arc.origin, (30, 20, 0)):
            self.assertAlmostEqual(p, q, places=6)
        self.assertScrewsOnto(sweep, bar)
        both = sweeps.recognise(bar)  # without a start face: the same chain, from either end
        self.assertEqual(len(both.pieces), 3)

    def test_spline_path_is_refused(self):
        spline = Part.BSplineCurve()
        spline.interpolate([V(0, 0, 0), V(10, 5, 0), V(20, 0, 5), V(30, 8, 3)])
        edge = spline.toShape()
        circle = Part.Wire(Part.makeCircle(1, edge.valueAt(edge.FirstParameter), edge.tangentAt(edge.FirstParameter)))
        bent = Part.Wire(edge).makePipeShell([circle], True, True)
        self.assertEqual(sweeps.recognise(bent), "its path is not made of straight, arc and helical pieces")

    def test_non_frenet_strand(self):
        """A round strand along a helix in PartDesign's Standard mode: its side surface follows the screw but its seam
        twists, so the solid is exported rebuilt."""
        strand = helix_pipe(10, 15, 1.2, ("circle", 0.45), frenet=False)
        start, _ = end_faces(strand)
        sweep = sweeps.recognise(strand, start_face=start)
        self.assertHelix(sweep, 540, 15)
        self.assertTrue(sweep.rebuild)

    def test_twisting_rectangle_is_refused(self):
        coil = helix_pipe(6, 6, 20, ("rect", 2, 4), frenet=False)
        self.assertEqual(sweeps.recognise(coil), "the profile twists along the path; make the pipe with Frenet mode")

    def test_loft_is_still_refused(self):
        def square(z, turn):
            c, s = math.cos(turn), math.sin(turn)
            corners = ((-5, -5), (5, -5), (5, 5), (-5, 5), (-5, -5))
            return Part.makePolygon([V(c * x - s * y, s * x + c * y, z) for x, y in corners])

        twisted = Part.makeLoft([square(0, 0), square(10, math.pi / 4)], True, True)  # equal ends, a screw apart
        self.assertIsInstance(sweeps.recognise(twisted), str)

    def test_plain_pipe_helix_is_a_helix(self):
        """A Part workbench pipe (makePipeShell, Frenet) along Part.makeHelix: its volume is a few 1e-6 off the fitted
        helix's, within the helical tolerance."""
        helix = Part.Wire(Part.makeHelix(6, 6, 20))
        edge = helix.Edges[0]
        p0, t = edge.valueAt(edge.FirstParameter), edge.tangentAt(edge.FirstParameter).normalize()
        u = V(1, 0, 0) - t * t.x
        u.normalize()
        w = t.cross(u)
        rect = Part.makePolygon([p0 + u * x + w * y for x, y in ((-1, -2), (1, -2), (1, 2), (-1, 2), (-1, -2))])
        coil = helix.makePipeShell([rect], True, True)
        with mock.patch.object(sweeps, "HELIX_VOLUME", 1e-6):  # the straight and revolved tolerance refuses it
            self.assertEqual(sweeps.recognise(coil), "its volume is not the start face swept to the end face")
        sweep = sweeps.recognise(coil)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertAlmostEqual(sweep.pieces[0].angle, 360, places=3)
        self.assertAlmostEqual(abs(sweep.pieces[0].advance), 6, places=4)

    def test_padded_bent_busbar_is_a_chain(self):
        bar = padded_busbar()
        start = face_name(bar, lambda c: abs(c.x) < 1e-9)
        for sweep in (sweeps.recognise(bar, start_face=start), sweeps.recognise(bar)):
            self.assertIsInstance(sweep, sweeps.Sweep)
            first, arc, last = sweep.pieces
            self.assertEqual((first.angle, last.angle), (0, 0))
            self.assertAlmostEqual(first.advance, 30)
            self.assertAlmostEqual(last.advance, 30)
            self.assertAlmostEqual(arc.angle, 90, places=6)
            self.assertEqual(arc.advance, 0.0)
            self.assertAlmostEqual(math.hypot(arc.origin[0] - 30, arc.origin[1] - 20), 0, places=6)
        sweep = sweeps.recognise(bar, start_face=start)
        self.assertEqual(sweep.end, face_name(bar, lambda c: abs(c.y - 50) < 1e-9))
        self.assertScrewsOnto(sweep, bar)

    def test_padded_bent_busbar_start_face_top_is_straight(self):
        bar = padded_busbar()
        top = face_name(bar, lambda c: abs(c.z - 4) < 1e-9)
        sweep = sweeps.recognise(bar, start_face=top)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertEqual(len(sweep.pieces), 1)
        self.assertEqual(sweep.pieces[0].angle, 0)
        self.assertAlmostEqual(sweep.pieces[0].advance, 4)

    def test_stage_1_and_2_sweeps_do_not_rebuild(self):
        for solid in (Part.makeBox(10, 4, 40), Part.makeCylinder(0.45, 20), Part.makeTorus(20, 3)):
            self.assertFalse(sweeps.recognise(solid).rebuild)


if __name__ == "__main__":
    unittest.main()
