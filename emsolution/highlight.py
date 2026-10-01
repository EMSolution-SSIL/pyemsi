"""Temporary highlight of bodies, faces, edges and vertices in the 3D view.

Drawn on top of the model, without touching the selection or the document."""
import FreeCADGui as Gui
from pivy import coin

from .jobwriter import global_shape

COLOR = (1.0, 0.5, 0.0)  # orange: neither selection green nor preselection yellow
_shown = None  # (view, node)


def _part(coords, shape_node, transparency=0.0):
    sep = coin.SoSeparator()
    mat = coin.SoMaterial()
    mat.diffuseColor = COLOR
    mat.transparency = transparency
    pts = coin.SoCoordinate3()
    pts.point.setValues(0, len(coords), coords)
    for n in (mat, pts, shape_node):
        sep.addChild(n)
    return sep


def node(refs):
    """Coin node drawing refs = [(body, sub)]; sub "" draws the body's faces."""
    faces, edges, vertices = [], [], []
    for body, sub in refs:
        shape = global_shape(body)
        try:
            el = shape.getElement(sub) if sub else shape
        except Exception:  # a sub-element the body no longer has
            continue
        if sub.startswith("Edge"):
            edges.append(el)
        elif sub.startswith("Vertex"):
            vertices.append(el)
        else:
            faces += el.Faces
    root = coin.SoAnnotation()  # drawn after, and over, the model
    light = coin.SoLightModel()
    light.model = coin.SoLightModel.BASE_COLOR
    style = coin.SoDrawStyle()
    style.lineWidth = 4
    style.pointSize = 10
    root.addChild(light)
    root.addChild(style)
    if faces:
        coords, index = [], []
        for f in faces:
            pts, tris = f.tessellate(max(f.BoundBox.DiagonalLength / 200, 1e-3))
            base = len(coords)
            coords += [tuple(p) for p in pts]
            for a, b, c in tris:
                index += [base + a, base + b, base + c, -1]
        mesh = coin.SoIndexedFaceSet()
        mesh.coordIndex.setValues(0, len(index), index)
        root.addChild(_part(coords, mesh, 0.5))
    if edges:
        lines = [[tuple(p) for p in e.discretize(Deflection=max(e.Length / 200, 1e-3))]
                 for e in edges]
        line_set = coin.SoLineSet()
        line_set.numVertices.setValues(0, len(lines), [len(ln) for ln in lines])
        root.addChild(_part([p for ln in lines for p in ln], line_set))
    if vertices:
        root.addChild(_part([tuple(v.Point) for v in vertices], coin.SoPointSet()))
    return root


def show(refs):
    """Highlight refs in their document's active 3D view, replacing any earlier highlight."""
    global _shown
    clear()
    if not refs:
        return
    view = Gui.getDocument(refs[0][0].Document.Name).activeView()
    if not hasattr(view, "getSceneGraph"):  # not a 3D view
        return
    n = node(refs)
    view.getSceneGraph().addChild(n)
    _shown = (view, n)


def clear():
    global _shown
    if _shown is not None:
        view, n = _shown
        _shown = None
        try:
            view.getSceneGraph().removeChild(n)
        except Exception:  # the view was closed
            pass


def shown():
    """The highlight node in the 3D view, or None."""
    return _shown[1] if _shown else None
