"""Labels for the mesh items of a Study, drawn over the 3D view.

An item on edges, faces or vertices gets a tag on each of its elements (the element count, the size, the name).
An item on whole bodies gets a badge on each body; items on the same body share one row of badges.
Hovering a badge lists its items. Nothing is added to the document or to the scene graph.

show() labels the given items, and with others=True the other items of their group too (materials, excitations or
mesh items), fainter. clear() removes the
labels. The selection and the task panels call these."""

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore, QtGui, QtWidgets

from . import objects
from .geometry import global_shape

# class name -> (colour, badge letter, name)
KINDS = {
    "Material": ("#3366cc", "M", "Material"),
    "MeshSize": ("#2e9e44", "S", "Mesh size"),
    "TransfiniteEdges": ("#e8590c", "E", "Transfinite edges"),
    "TransfiniteBody": ("#7b3fb3", "T", "Transfinite body"),
    "Recombine": ("#0b9eb3", "Q", "Recombine"),
    "Excitation": ("#d6249f", "X", "Excitation"),
    "SymmetricMesh": ("#8d6e3f", "Y", "Symmetric mesh"),
}
# the other items shown with an item are those of its group: materials with materials, mesh items with mesh items
GROUPS = {"Material": "material", "Excitation": "excitation"}
BORDER = "#1a237e"  # as the Measure label's
FAINT = 120  # alpha of the labels of the other items
PREFS = "User parameter:BaseApp/Preferences/Mod/EMSolution"
_overlays = {}  # view widget -> Overlay


def kind_of(item):
    kind = type(getattr(item, "Proxy", None)).__name__
    return kind if kind in KINDS else None


def anchors(body, sub):
    """Points of the body's 3D shape where a label of (body, sub) goes: one per solid (or face, in 2D) for a whole
    body, else the middle of the element."""
    shape = global_shape(body)
    if not sub:
        parts = shape.Solids or shape.Faces
        return [p.CenterOfMass for p in parts] if len(parts) > 1 else [shape.CenterOfMass]
    element = shape.getElement(sub)
    if sub.startswith("Vertex"):
        return [element.Point]
    if sub.startswith("Edge"):
        return [element.valueAt((element.FirstParameter + element.LastParameter) / 2)]
    return [Part.Vertex(element.CenterOfMass).distToShape(element)[1][0][1]]  # on the face, not off a hole


def tag_text(item, values):
    """The text of the tags of an item; values: what a panel has typed in but not saved ({property: value})."""
    kind = kind_of(item)
    if kind == "TransfiniteEdges":
        elements, distribution = values.get("Elements", item.Elements), values.get("Distribution", item.Distribution)
        return f"{elements} bump" if distribution == "Bump" else str(elements)
    if kind == "MeshSize":
        return f"{values.get('Size', item.Size.Value):g} mm"
    if kind == "Material":
        return values.get("Material", item.LibraryMaterial.Label if item.LibraryMaterial else objects.NO_MATERIAL)
    if kind == "TransfiniteBody":
        return "corner"
    return values.get("Name", objects.display_name(item))


def description(item, values):
    """Hover text of an item: "Mesh size: 2 mm"."""
    kind = kind_of(item)
    name = KINDS[kind][2]
    if kind == "Excitation":
        return f"{name}: {values.get('Name', objects.display_name(item))}"
    if kind == "Material":
        return f"{name}: {item.Label}"
    if kind == "MeshSize":
        return f"{name}: {tag_text(item, values)}"
    if kind == "TransfiniteEdges":
        return f"{name}: {values.get('Elements', item.Elements)} el, {values.get('Distribution', item.Distribution)}"
    return name


def shown(obj):
    """Whether obj is visible in the 3D view: neither it nor a Part or Group holding it is hidden."""
    while obj is not None:
        if not obj.Visibility:
            return False
        obj = obj.getParentGeoFeatureGroup() or obj.getParentGroup()
    return True


def build(focus, others, refs, values):
    """(tags, badges) of the items in focus, and of the other items of their group if others. refs: {item Name:
    [(body, sub)]} where an item is shown with other references than it has (a panel's unsaved list), values: {item Name:
    {property: value}} likewise for the texts.
    A tag is {"point", "text", "color"}; a badge is {"point", "items"}, the items being (letter, color, description)
    for the items on the whole body at that point. The labels of the other items are fainter."""
    study = objects.owner_study(focus[0])
    names = {o.Name for o in focus}
    tags, badges = [], {}
    # a symmetric Study's cell bodies are hidden: the drawing built from them shows their place
    cells = {c.Name: i.Top for i in objects.symmetric_items(study) if i.Top is not None for c in i.Cells}
    group = GROUPS.get(kind_of(focus[0]), "mesh")
    items = [
        o
        for o in focus[0].Document.Objects
        if kind_of(o) and objects.owner_study(o) is study and GROUPS.get(kind_of(o), "mesh") == group
    ]
    for item in sorted((o for o in items if o.Name in names or others), key=lambda o: o.Name not in names):
        color = QtGui.QColor(KINDS[kind_of(item)][0])
        if item.Name not in names:
            color.setAlpha(FAINT)
        for body, sub in refs.get(item.Name, objects.item_refs(item)):
            if not (shown(cells[body.Name]) if body.Name in cells else shown(body)):
                continue
            try:
                points = anchors(body, sub)
            except Exception:  # a sub-element the body no longer has
                continue
            for point in points:
                if sub:
                    tags.append({"point": point, "text": tag_text(item, values.get(item.Name, {})), "color": color})
                else:
                    key = tuple(round(c, 3) for c in point)
                    badges.setdefault(key, {"point": point, "items": []})["items"].append(
                        (KINDS[kind_of(item)][1], color, description(item, values.get(item.Name, {})))
                    )
    return tags, list(badges.values())


class Overlay(QtWidgets.QWidget):
    """Transparent widget over a 3D view that repaints when the camera moves or the Study changes."""

    def __init__(self, view_widget, doc):
        super().__init__(view_widget)
        self.doc, self.view = doc, Gui.getDocument(doc.Name).activeView()
        self.focus, self.others, self.refs, self.values = [], False, {}, {}
        self.tags, self.badges, self.dirty, self.signature, self.hits, self.placed = [], [], True, None, [], []
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setGeometry(view_widget.rect())
        for w in [view_widget] + view_widget.findChildren(QtWidgets.QWidget):  # the mouse moves arrive at a child
            if w is not self:
                w.installEventFilter(self)
                w.setMouseTracking(True)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(80)
        self.show()
        self.raise_()

    def project(self, point):
        """Pixel of a 3D point in this widget. The view counts y from the bottom."""
        x, y = self.view.getPointOnScreen(point)
        return QtCore.QPointF(x, self.height() - y)

    def tick(self):
        try:
            self.refresh()
        except RuntimeError:  # the view is gone
            clear()

    def refresh(self):
        if self.dirty:
            self.dirty = False
            try:
                self.tags, self.badges = build(self.focus, self.others, self.refs, self.values)
            except ReferenceError:  # an item was deleted
                return clear()
            self.signature = None
        signature = (
            self.project(App.Vector(0, 0, 0)).toTuple(),
            self.project(App.Vector(1000, 0, 0)).toTuple(),
            self.project(App.Vector(0, 1000, 0)).toTuple(),
            self.size().toTuple(),
        )
        if signature != self.signature:
            self.signature = signature
            self.update()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize and obj is self.parentWidget():
            self.setGeometry(obj.rect())
        elif event.type() == QtCore.QEvent.MouseMove:
            pos = self.mapFromGlobal(event.globalPosition().toPoint())
            text = next(("\n".join(lines) for rect, lines in self.hits if rect.contains(pos)), None)
            if text:
                QtWidgets.QToolTip.showText(event.globalPosition().toPoint(), text, self)
        return False

    def font(self, px, bold=True):
        font = QtGui.QFont("Segoe UI")
        font.setPixelSize(px)
        font.setBold(bold)
        return font

    def free(self, rect, step):
        """Move rect down until it overlaps no label placed so far."""
        for _ in range(40):
            if not any(rect.intersects(other) for other in self.placed):
                break
            rect.translate(0, step)
        self.placed.append(QtCore.QRectF(rect))
        return rect

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        self.placed, self.hits = [], []
        view = QtCore.QRectF(self.rect())
        for badge in self.badges:
            at = self.project(badge["point"])
            if view.contains(at):
                self.paint_badges(p, at, badge["items"])
        for tag in self.tags:
            at = self.project(tag["point"])
            if view.contains(at):
                self.paint_tag(p, at, tag["text"], tag["color"])
        p.end()

    def paint_badges(self, p, at, items, radius=11):
        width = len(items) * (2 * radius + 3) + 3
        rect = self.free(QtCore.QRectF(at.x() - width / 2, at.y() - radius - 3, width, 2 * radius + 6), 2 * radius + 8)
        p.setPen(QtGui.QPen(QtGui.QColor(BORDER), 1))
        p.setBrush(QtGui.QColor("white"))
        p.drawRoundedRect(rect, radius + 3, radius + 3)
        p.setFont(self.font(12))
        for i, (letter, color, _) in enumerate(items):
            c = QtCore.QPointF(rect.left() + 3 + radius + i * (2 * radius + 3), rect.center().y())
            p.setPen(QtCore.Qt.NoPen)
            p.setBrush(color)
            p.drawEllipse(c, radius, radius)
            p.setPen(QtGui.QColor("white") if color.alpha() == 255 else QtGui.QColor(60, 60, 60))
            p.drawText(
                QtCore.QRectF(c.x() - radius, c.y() - radius, 2 * radius, 2 * radius), QtCore.Qt.AlignCenter, letter
            )
        self.hits.append((rect, [text for _, _, text in items]))

    def paint_tag(self, p, at, text, color, px=13):
        p.setFont(self.font(px))
        width, height = QtGui.QFontMetrics(p.font()).horizontalAdvance(text) + 12, px + 9
        rect = self.free(QtCore.QRectF(at.x() - width / 2, at.y() - height / 2, width, height), height / 2 + 1)
        p.setPen(QtGui.QPen(QtGui.QColor("white"), 1.5))
        p.setBrush(color)
        p.drawRoundedRect(rect, height / 2, height / 2)
        p.setPen(QtGui.QColor("white") if color.alpha() == 255 else QtGui.QColor(60, 60, 60))
        p.drawText(rect, QtCore.Qt.AlignCenter, text)


class _Watcher:
    """Marks the overlays of a document dirty when its items or shapes change."""

    def dirty(self, doc):
        for overlay in _overlays.values():
            if overlay.doc is doc:
                overlay.dirty = True

    def slotChangedObject(self, obj, prop):
        if prop in (
            "References",
            "Corners",
            "Elements",
            "Size",
            "Distribution",
            "Label",
            "Body",
            "Pieces",
            "Shape",
            "Visibility",
        ):
            self.dirty(obj.Document)

    def slotCreatedObject(self, obj):
        self.dirty(obj.Document)

    def slotDeletedObject(self, obj):
        self.dirty(obj.Document)

    def slotRecomputedDocument(self, doc):
        self.dirty(doc)

    def slotDeletedDocument(self, doc):
        for widget, overlay in list(_overlays.items()):
            try:
                gone = overlay.doc.Name == doc.Name
            except ReferenceError:
                gone = True
            if gone:
                _drop(widget)


_watcher = None


def view_widget():
    """The 3D view widget of the active document, or None."""
    sub = Gui.getMainWindow().centralWidget().activeSubWindow()
    if sub is None or Gui.ActiveDocument is None or not hasattr(Gui.ActiveDocument.activeView(), "getPointOnScreen"):
        return None
    widget = sub.widget()
    return widget if widget.metaObject().className() == "Gui::View3DInventor" else None


def others_wanted():
    return App.ParamGet(PREFS).GetBool("LabelsOfOthers", False)


def show(items, others=False, refs=None, values=None):
    """Label items in the active 3D view, replacing the labels shown before. others: the other items of their group too.
    refs: {item Name: [(body, sub)]}, references to show an item with instead of its own.
    values: {item Name: {property: value}}, what a panel has typed in but not saved (see tag_text)."""
    global _watcher
    items = [i for i in items if kind_of(i)]
    widget = view_widget()
    if not items or widget is None or items[0].Document is not Gui.ActiveDocument.Document:
        return clear()
    if _watcher is None:
        _watcher = _Watcher()
        App.addDocumentObserver(_watcher)
    overlay = _overlays.get(widget)
    if overlay is not None and overlay.doc is not items[0].Document:  # a view of a closed document, its address reused
        _drop(widget)
        overlay = None
    if overlay is None:
        overlay = _overlays[widget] = Overlay(widget, items[0].Document)
        overlay.destroyed.connect(lambda *_: _overlays.pop(widget, None))
    overlay.focus, overlay.others, overlay.refs, overlay.values = items, others, dict(refs or {}), dict(values or {})
    overlay.dirty = True


def set_refs(item, refs):
    """A panel's unsaved reference list of the item it edits."""
    for overlay in _overlays.values():
        overlay.refs[item.Name] = list(refs)
        overlay.dirty = True


def set_values(item, values):
    """A panel's unsaved values of the item it edits."""
    for overlay in _overlays.values():
        overlay.values[item.Name] = dict(values)
        overlay.dirty = True


def set_others(flag):
    for overlay in _overlays.values():
        overlay.others, overlay.dirty = flag, True


def _drop(widget):
    overlay = _overlays.pop(widget)
    overlay.timer.stop()
    overlay.setParent(None)
    overlay.deleteLater()


def clear():
    for widget in list(_overlays):
        _drop(widget)


def others_checkbox():
    """The task panels' check box for the labels of the other items; it keeps the choice for the next panel."""
    box = QtWidgets.QCheckBox("Show the labels of the other items")
    box.setToolTip("Label the other mesh items of the Study in the 3D view too, fainter")
    box.setChecked(others_wanted())

    def changed(on):
        App.ParamGet(PREFS).SetBool("LabelsOfOthers", on)
        App.saveParameter()  # now: FreeCAD may not get to save it on quit
        set_others(on)

    box.toggled.connect(changed)
    return box
