# Python source module `DraftGeomUtils`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/DraftGeomUtils.py`. Import path is source-routed; installed availability is unverified.

Define geometry functions for manipulating shapes in the Draft Workbench.

These functions are used by different object creation functions
of the Draft Workbench, both in `Draft.py` and `DraftTools.py`.
They operate on the internal shapes (`Part::TopoShape`) of different objects
and on their subelements, that is, vertices, edges, and faces.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from draftgeoutils.linear_algebra import linearFromPoints, determinant

Facade reexport declaration.

Bound source name `DraftGeomUtils.linearFromPoints` -> `draftgeoutils.linear_algebra.linearFromPoints`.

Bound source name `DraftGeomUtils.determinant` -> `draftgeoutils.linear_algebra.determinant`.

[Source module `draftgeoutils.linear_algebra`](../draftgeoutils/linear_algebra/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:46`.

### from draftgeoutils.general import NORM

Facade reexport declaration.

Bound source name `DraftGeomUtils.NORM` -> `draftgeoutils.general.NORM`.

[Source module `draftgeoutils.general`](../draftgeoutils/general/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:49`.

### from draftgeoutils.general import precision, vec, edg, getVerts, v1, isNull, isPtOnEdge, hasCurves, isAligned, getQuad, areColinear, hasOnlyWires, geomType, isValidPath, findClosest, getBoundaryAngles

Facade reexport declaration.

Bound source name `DraftGeomUtils.precision` -> `draftgeoutils.general.precision`.

Bound source name `DraftGeomUtils.vec` -> `draftgeoutils.general.vec`.

Bound source name `DraftGeomUtils.edg` -> `draftgeoutils.general.edg`.

Bound source name `DraftGeomUtils.getVerts` -> `draftgeoutils.general.getVerts`.

Bound source name `DraftGeomUtils.v1` -> `draftgeoutils.general.v1`.

Bound source name `DraftGeomUtils.isNull` -> `draftgeoutils.general.isNull`.

Bound source name `DraftGeomUtils.isPtOnEdge` -> `draftgeoutils.general.isPtOnEdge`.

Bound source name `DraftGeomUtils.hasCurves` -> `draftgeoutils.general.hasCurves`.

Bound source name `DraftGeomUtils.isAligned` -> `draftgeoutils.general.isAligned`.

Bound source name `DraftGeomUtils.getQuad` -> `draftgeoutils.general.getQuad`.

Bound source name `DraftGeomUtils.areColinear` -> `draftgeoutils.general.areColinear`.

Bound source name `DraftGeomUtils.hasOnlyWires` -> `draftgeoutils.general.hasOnlyWires`.

Bound source name `DraftGeomUtils.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `DraftGeomUtils.isValidPath` -> `draftgeoutils.general.isValidPath`.

Bound source name `DraftGeomUtils.findClosest` -> `draftgeoutils.general.findClosest`.

Bound source name `DraftGeomUtils.getBoundaryAngles` -> `draftgeoutils.general.getBoundaryAngles`.

[Source module `draftgeoutils.general`](../draftgeoutils/general/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:51`.

### from draftgeoutils.geometry import findPerpendicular, findDistance, getSplineNormal, get_spline_normal, getNormal, get_normal, get_shape_normal, getRotation, isPlanar, is_planar, calculatePlacement, mirror, are_coplanar, is_straight_line, mirror_matrix, uv_vectors_from_face, placement_from_face, placement_from_points, distance_to_plane, project_point_on_plane

Facade reexport declaration.

Bound source name `DraftGeomUtils.findPerpendicular` -> `draftgeoutils.geometry.findPerpendicular`.

Bound source name `DraftGeomUtils.findDistance` -> `draftgeoutils.geometry.findDistance`.

Bound source name `DraftGeomUtils.getSplineNormal` -> `draftgeoutils.geometry.getSplineNormal`.

Bound source name `DraftGeomUtils.get_spline_normal` -> `draftgeoutils.geometry.get_spline_normal`.

Bound source name `DraftGeomUtils.getNormal` -> `draftgeoutils.geometry.getNormal`.

Bound source name `DraftGeomUtils.get_normal` -> `draftgeoutils.geometry.get_normal`.

Bound source name `DraftGeomUtils.get_shape_normal` -> `draftgeoutils.geometry.get_shape_normal`.

Bound source name `DraftGeomUtils.getRotation` -> `draftgeoutils.geometry.getRotation`.

Bound source name `DraftGeomUtils.isPlanar` -> `draftgeoutils.geometry.isPlanar`.

Bound source name `DraftGeomUtils.is_planar` -> `draftgeoutils.geometry.is_planar`.

Bound source name `DraftGeomUtils.calculatePlacement` -> `draftgeoutils.geometry.calculatePlacement`.

Bound source name `DraftGeomUtils.mirror` -> `draftgeoutils.geometry.mirror`.

Bound source name `DraftGeomUtils.are_coplanar` -> `draftgeoutils.geometry.are_coplanar`.

Bound source name `DraftGeomUtils.is_straight_line` -> `draftgeoutils.geometry.is_straight_line`.

Bound source name `DraftGeomUtils.mirror_matrix` -> `draftgeoutils.geometry.mirror_matrix`.

Bound source name `DraftGeomUtils.uv_vectors_from_face` -> `draftgeoutils.geometry.uv_vectors_from_face`.

Bound source name `DraftGeomUtils.placement_from_face` -> `draftgeoutils.geometry.placement_from_face`.

Bound source name `DraftGeomUtils.placement_from_points` -> `draftgeoutils.geometry.placement_from_points`.

Bound source name `DraftGeomUtils.distance_to_plane` -> `draftgeoutils.geometry.distance_to_plane`.

Bound source name `DraftGeomUtils.project_point_on_plane` -> `draftgeoutils.geometry.project_point_on_plane`.

[Source module `draftgeoutils.geometry`](../draftgeoutils/geometry/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:71`.

### from draftgeoutils.edges import findEdge, orientEdge, isSameLine, isLine, is_line, invert, findMidpoint, getTangent, get_referenced_edges

Facade reexport declaration.

Bound source name `DraftGeomUtils.findEdge` -> `draftgeoutils.edges.findEdge`.

Bound source name `DraftGeomUtils.orientEdge` -> `draftgeoutils.edges.orientEdge`.

Bound source name `DraftGeomUtils.isSameLine` -> `draftgeoutils.edges.isSameLine`.

Bound source name `DraftGeomUtils.isLine` -> `draftgeoutils.edges.isLine`.

Bound source name `DraftGeomUtils.is_line` -> `draftgeoutils.edges.is_line`.

Bound source name `DraftGeomUtils.invert` -> `draftgeoutils.edges.invert`.

Bound source name `DraftGeomUtils.findMidpoint` -> `draftgeoutils.edges.findMidpoint`.

Bound source name `DraftGeomUtils.getTangent` -> `draftgeoutils.edges.getTangent`.

Bound source name `DraftGeomUtils.get_referenced_edges` -> `draftgeoutils.edges.get_referenced_edges`.

[Source module `draftgeoutils.edges`](../draftgeoutils/edges/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:94`.

### from draftgeoutils.faces import concatenate, getBoundary, isCoplanar, is_coplanar, bind, cleanFaces, removeSplitter

Facade reexport declaration.

Bound source name `DraftGeomUtils.concatenate` -> `draftgeoutils.faces.concatenate`.

Bound source name `DraftGeomUtils.getBoundary` -> `draftgeoutils.faces.getBoundary`.

Bound source name `DraftGeomUtils.isCoplanar` -> `draftgeoutils.faces.isCoplanar`.

Bound source name `DraftGeomUtils.is_coplanar` -> `draftgeoutils.faces.is_coplanar`.

Bound source name `DraftGeomUtils.bind` -> `draftgeoutils.faces.bind`.

Bound source name `DraftGeomUtils.cleanFaces` -> `draftgeoutils.faces.cleanFaces`.

Bound source name `DraftGeomUtils.removeSplitter` -> `draftgeoutils.faces.removeSplitter`.

[Source module `draftgeoutils.faces`](../draftgeoutils/faces/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:106`.

### from draftgeoutils.arcs import isClockwise, isWideAngle, arcFrom2Pts, arcFromSpline

Facade reexport declaration.

Bound source name `DraftGeomUtils.isClockwise` -> `draftgeoutils.arcs.isClockwise`.

Bound source name `DraftGeomUtils.isWideAngle` -> `draftgeoutils.arcs.isWideAngle`.

Bound source name `DraftGeomUtils.arcFrom2Pts` -> `draftgeoutils.arcs.arcFrom2Pts`.

Bound source name `DraftGeomUtils.arcFromSpline` -> `draftgeoutils.arcs.arcFromSpline`.

[Source module `draftgeoutils.arcs`](../draftgeoutils/arcs/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:116`.

### from draftgeoutils.cuboids import isCubic, getCubicDimensions

Facade reexport declaration.

Bound source name `DraftGeomUtils.isCubic` -> `draftgeoutils.cuboids.isCubic`.

Bound source name `DraftGeomUtils.getCubicDimensions` -> `draftgeoutils.cuboids.getCubicDimensions`.

[Source module `draftgeoutils.cuboids`](../draftgeoutils/cuboids/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:118`.

### from draftgeoutils.circle_inversion import pointInversion, polarInversion, circleInversion

Facade reexport declaration.

Bound source name `DraftGeomUtils.pointInversion` -> `draftgeoutils.circle_inversion.pointInversion`.

Bound source name `DraftGeomUtils.polarInversion` -> `draftgeoutils.circle_inversion.polarInversion`.

Bound source name `DraftGeomUtils.circleInversion` -> `draftgeoutils.circle_inversion.circleInversion`.

[Source module `draftgeoutils.circle_inversion`](../draftgeoutils/circle_inversion/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:121`.

### from draftgeoutils.sort_edges import sortEdges, sortEdgesOld

Facade reexport declaration.

Bound source name `DraftGeomUtils.sortEdges` -> `draftgeoutils.sort_edges.sortEdges`.

Bound source name `DraftGeomUtils.sortEdgesOld` -> `draftgeoutils.sort_edges.sortEdgesOld`.

[Source module `draftgeoutils.sort_edges`](../draftgeoutils/sort_edges/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:124`.

### from draftgeoutils.intersections import findIntersection, wiresIntersect, connect, angleBisection

Facade reexport declaration.

Bound source name `DraftGeomUtils.findIntersection` -> `draftgeoutils.intersections.findIntersection`.

Bound source name `DraftGeomUtils.wiresIntersect` -> `draftgeoutils.intersections.wiresIntersect`.

Bound source name `DraftGeomUtils.connect` -> `draftgeoutils.intersections.connect`.

Bound source name `DraftGeomUtils.angleBisection` -> `draftgeoutils.intersections.angleBisection`.

[Source module `draftgeoutils.intersections`](../draftgeoutils/intersections/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:126`.

### from draftgeoutils.wires import findWires, findWiresOld, findWiresOld2, flattenWire, superWire, isReallyClosed, curvetowire, curvetosegment, rebaseWire, removeInterVertices, cleanProjection, tessellateProjection, get_placement_perpendicular_to_wire, get_extended_wire

Facade reexport declaration.

Bound source name `DraftGeomUtils.findWires` -> `draftgeoutils.wires.findWires`.

Bound source name `DraftGeomUtils.findWiresOld` -> `draftgeoutils.wires.findWiresOld`.

Bound source name `DraftGeomUtils.findWiresOld2` -> `draftgeoutils.wires.findWiresOld2`.

Bound source name `DraftGeomUtils.flattenWire` -> `draftgeoutils.wires.flattenWire`.

Bound source name `DraftGeomUtils.superWire` -> `draftgeoutils.wires.superWire`.

Bound source name `DraftGeomUtils.isReallyClosed` -> `draftgeoutils.wires.isReallyClosed`.

Bound source name `DraftGeomUtils.curvetowire` -> `draftgeoutils.wires.curvetowire`.

Bound source name `DraftGeomUtils.curvetosegment` -> `draftgeoutils.wires.curvetosegment`.

Bound source name `DraftGeomUtils.rebaseWire` -> `draftgeoutils.wires.rebaseWire`.

Bound source name `DraftGeomUtils.removeInterVertices` -> `draftgeoutils.wires.removeInterVertices`.

Bound source name `DraftGeomUtils.cleanProjection` -> `draftgeoutils.wires.cleanProjection`.

Bound source name `DraftGeomUtils.tessellateProjection` -> `draftgeoutils.wires.tessellateProjection`.

Bound source name `DraftGeomUtils.get_placement_perpendicular_to_wire` -> `draftgeoutils.wires.get_placement_perpendicular_to_wire`.

Bound source name `DraftGeomUtils.get_extended_wire` -> `draftgeoutils.wires.get_extended_wire`.

[Source module `draftgeoutils.wires`](../draftgeoutils/wires/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:128`.

### from draftgeoutils.fillets import fillet, filletWire

Facade reexport declaration.

Bound source name `DraftGeomUtils.fillet` -> `draftgeoutils.fillets.fillet`.

Bound source name `DraftGeomUtils.filletWire` -> `draftgeoutils.fillets.filletWire`.

[Source module `draftgeoutils.fillets`](../draftgeoutils/fillets/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:146`.

### from draftgeoutils.offsets import pocket2d, offset, offsetWire

Facade reexport declaration.

Bound source name `DraftGeomUtils.pocket2d` -> `draftgeoutils.offsets.pocket2d`.

Bound source name `DraftGeomUtils.offset` -> `draftgeoutils.offsets.offset`.

Bound source name `DraftGeomUtils.offsetWire` -> `draftgeoutils.offsets.offsetWire`.

[Source module `draftgeoutils.offsets`](../draftgeoutils/offsets/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:149`.

### from draftgeoutils.circles import findClosestCircle, getCircleFromSpline, circlefrom1Line2Points, circlefrom2Lines1Point, circleFrom2LinesRadius, circleFrom3LineTangents, circleFromPointLineRadius, circleFrom2PointsRadius, findHomotheticCenterOfCircles, findRadicalAxis, findRadicalCenter

Facade reexport declaration.

Bound source name `DraftGeomUtils.findClosestCircle` -> `draftgeoutils.circles.findClosestCircle`.

Bound source name `DraftGeomUtils.getCircleFromSpline` -> `draftgeoutils.circles.getCircleFromSpline`.

Bound source name `DraftGeomUtils.circlefrom1Line2Points` -> `draftgeoutils.circles.circlefrom1Line2Points`.

Bound source name `DraftGeomUtils.circlefrom2Lines1Point` -> `draftgeoutils.circles.circlefrom2Lines1Point`.

Bound source name `DraftGeomUtils.circleFrom2LinesRadius` -> `draftgeoutils.circles.circleFrom2LinesRadius`.

Bound source name `DraftGeomUtils.circleFrom3LineTangents` -> `draftgeoutils.circles.circleFrom3LineTangents`.

Bound source name `DraftGeomUtils.circleFromPointLineRadius` -> `draftgeoutils.circles.circleFromPointLineRadius`.

Bound source name `DraftGeomUtils.circleFrom2PointsRadius` -> `draftgeoutils.circles.circleFrom2PointsRadius`.

Bound source name `DraftGeomUtils.findHomotheticCenterOfCircles` -> `draftgeoutils.circles.findHomotheticCenterOfCircles`.

Bound source name `DraftGeomUtils.findRadicalAxis` -> `draftgeoutils.circles.findRadicalAxis`.

Bound source name `DraftGeomUtils.findRadicalCenter` -> `draftgeoutils.circles.findRadicalCenter`.

[Source module `draftgeoutils.circles`](../draftgeoutils/circles/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:151`.

### from draftgeoutils.circles_apollonius import outerSoddyCircle, innerSoddyCircle, circleFrom3CircleTangents

Facade reexport declaration.

Bound source name `DraftGeomUtils.outerSoddyCircle` -> `draftgeoutils.circles_apollonius.outerSoddyCircle`.

Bound source name `DraftGeomUtils.innerSoddyCircle` -> `draftgeoutils.circles_apollonius.innerSoddyCircle`.

Bound source name `DraftGeomUtils.circleFrom3CircleTangents` -> `draftgeoutils.circles_apollonius.circleFrom3CircleTangents`.

[Source module `draftgeoutils.circles_apollonius`](../draftgeoutils/circles_apollonius/index.md).

Evidence: `src/Mod/Draft/DraftGeomUtils.py:165`.

## Internal definitions not expanded

`DraftGeomUtils.__title__`, `DraftGeomUtils.__author__`, `DraftGeomUtils.__url__`. These are source internals unless an explicit export establishes otherwise.

