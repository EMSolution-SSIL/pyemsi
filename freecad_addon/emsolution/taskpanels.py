"""View providers, the item edit panel, folder watchers, the ID table dialog, the selection
observer and selection helpers."""

import weakref

import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin
from PySide import QtCore, QtWidgets

from . import airshapes, geometry, highlight, icon, jobwriter, labels, objects, validation
from . import symmetry

_active = {}  # document name -> (document instance, Study Name); GUI state only


def set_active_study(study):
    _active[study.Document.Name] = (study.Document, study.Name)


def active_study():
    """Resolve selected ownership first, then a validated target for this document."""
    docs = App.listDocuments()
    for name, (doc, _) in list(_active.items()):
        if docs.get(name) is not doc:
            del _active[name]
    doc = App.ActiveDocument
    if doc is None:
        return None
    owners = {
        s.Name: s
        for o in Gui.Selection.getSelection()
        if o.Document == doc and (s := objects.owner_study(o)) is not None
    }
    if len(owners) > 1:
        _active.pop(doc.Name, None)
        return None
    if owners:
        study = next(iter(owners.values()))
        set_active_study(study)
        return study
    remembered = _active.get(doc.Name)
    study = doc.getObject(remembered[1]) if remembered else None
    if study not in objects.studies(doc):
        _active.pop(doc.Name, None)
        study = objects.find_study(doc)
    return study


def selected_bodies():
    out = {}
    for sel in Gui.Selection.getSelectionEx():
        body = objects.pick_body(sel.Object)
        if body is not None:
            out.setdefault(body.Name, body)
    return list(out.values())


def selected_subs(kinds, whole_bodies=False):
    """[(body, sub)] for picked sub-elements named kinds[i]N; (body, "") for a whole body."""
    out = []
    for sel in Gui.Selection.getSelectionEx():
        body = objects.pick_body(sel.Object)
        if body is None:
            continue
        if not sel.SubElementNames:
            if whole_bodies:
                out.append((body, ""))
        else:
            out += [(body, s) for s in sel.SubElementNames if s.startswith(kinds)]
    return out


def is_air(body):
    return isinstance(getattr(body, "Proxy", None), objects.AirRegion)


def drawing_names(study):
    """Names of the drawings a click can land on: the Symmetric Groups."""
    return {g.Name for g in objects.symmetric_groups(study)}


def selected_face_picks(study, vertices):
    """[(body, sub)] for a 2D structured item: a body picked as a whole is (body, ""); each clicked FaceN is
    (body, FaceN), or (body, "") when the body has one face (any click on it, an edge or vertex too);
    clicked vertices too when vertices.
    A click on a Symmetric Group's drawing is moved to the cell: a face of a copy is that block of the cell object,
    and a vertex is a corner of the cell objects that have it, those this selection picks if it picks any of them."""
    tops = drawing_names(study)
    out, top_corners = [], []
    for sel in Gui.Selection.getSelectionEx():
        body = objects.pick_body(sel.Object)
        if body is None:
            continue
        if not sel.SubElementNames:
            out.append((body, ""))
            continue
        if body.Name in tops:
            faces = [(body, s) for s in sel.SubElementNames if s.startswith("Face")]
            out += [(b, "" if len(b.Shape.Faces) == 1 else s) for b, s in objects.to_cells(study, faces)]
            if vertices:
                top_corners += objects.to_cells(
                    study, [(body, s) for s in sel.SubElementNames if s.startswith("Vertex")]
                )
            continue
        one_face = len(body.Shape.Faces) == 1
        for sub in sel.SubElementNames:
            if vertices and sub.startswith("Vertex"):
                out.append((body, sub))
            if one_face and sub.startswith(("Face", "Edge", "Vertex")):
                out.append((body, ""))
            elif sub.startswith("Face"):
                out.append((body, sub))
    regions = {b.Name for b, s in out if not s.startswith("Vertex")}
    out += [(b, s) for b, s in top_corners if b.Name in regions] or top_corners
    seen, unique = set(), []
    for body, sub in out:
        if (body.Name, sub) not in seen:
            seen.add((body.Name, sub))
            unique.append((body, sub))
    return unique


def ask_solid(face, names):
    """The solid to take for a face two solids share: one of names, or None on Cancel."""
    name, ok = QtWidgets.QInputDialog.getItem(
        Gui.getMainWindow(), "Which solid?", f"{face} is shared by two solids. Take:", names, 0, False
    )
    return name if ok else None


def selected_group_pieces(study):
    """([(group, SolidN)], cancelled) for the faces clicked on a Symmetric Group's drawing: the solid of each clicked
    face. A face of two solids is decided by the solid behind the click, seen from the 3D view; when that cannot be
    told the user is asked, and a Cancel skips the pick (cancelled is then True). In 2D a click is on a face of the
    drawing, which is a piece itself: ([(group, FaceN)], False)."""
    return _picked_solids({g.Name for g in objects.symmetric_groups(study)})


def _picked_solids(names):
    from . import geometry

    try:
        view = Gui.ActiveDocument.ActiveView.getViewDirection()
    except Exception:  # no 3D view: shared faces are asked about
        view = None
    out, cancelled = [], False
    for sel in Gui.Selection.getSelectionEx():
        body = objects.pick_body(sel.Object)
        if body is None or body.Name not in names:
            continue
        shape = geometry.global_shape(body)
        points = list(sel.PickedPoints)
        subs = list(sel.SubElementNames)
        for k, sub in enumerate(subs):
            if not sub.startswith("Face"):
                continue
            if not shape.Solids:  # 2D: the face is the piece
                if (body, sub) not in out:
                    out.append((body, sub))
                continue
            picked = points[k] if len(points) == len(subs) else None
            solid = objects.piece_solid(shape, sub, picked, view)
            if solid is None:
                candidates = objects.face_solids(shape, sub)
                solid = ask_solid(f"{objects.display_name(body)}.{sub}", candidates) if candidates else None
                cancelled = cancelled or bool(candidates) and solid is None
            if solid is not None and (body, solid) not in out:
                out.append((body, solid))
    return out, cancelled


def selected_faces():
    """Faces of bodies; an Excitation never goes on an Air Region."""
    return [(b, s) for b, s in selected_subs(("Face",)) if not is_air(b)]


def selected_mesh_refs():
    return selected_subs(("Face", "Edge", "Vertex"), whole_bodies=True)


LIBRARY_EMPTY = "The Material Library is empty: import materials from its folder first."


def library_combo(study, current=None):
    """The Study's Material Library entries (data: object Name), current selected, else the first."""
    combo = QtWidgets.QComboBox()
    for lib in objects.library_materials(study):
        combo.addItem(lib.Label, lib.Name)
    if current is not None:
        combo.setCurrentIndex(combo.findData(current.Name))
    return combo


def owned_text(owned, what, target, target_one=None):
    """The move confirmation for owned [((body, sub), Material)]; what: "body" or "face"; target_one: target when
    only one is moved (default: target)."""
    rule = f"\n\nA {what} can have only one Material."
    if len(owned) == 1:
        (((b, s), m),) = owned
        where = f'{objects.ref_label(b, s)} already belongs to the Material "{objects.display_name(m)}".'
        return f"{where}{rule} Move it to {target_one or target}?"
    lines = [f'• {objects.ref_label(b, s)} (in "{objects.display_name(m)}")' for (b, s), m in owned]
    return "These already belong to other Materials:\n" + "\n".join(lines) + f"{rule} Move them to {target}?"


def confirm_move(text):
    box = QtWidgets.QMessageBox(Gui.getMainWindow())
    box.setWindowTitle("Move to this Material?")
    box.setText(text)
    move = box.addButton("Move", QtWidgets.QMessageBox.AcceptRole)
    box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
    box.exec()
    return box.clickedButton() == move


class BulkAssignDialog(QtWidgets.QDialog):
    """Library material and POTENTIAL for several bodies at once: each gets a Material of its own, named after it;
    an Air Region keeps its Material, named after it."""

    def __init__(self, study, bodies, parent=None):
        super().__init__(parent or Gui.getMainWindow())
        self.study, self.bodies = study, list(bodies)
        self.setWindowTitle("Assign Material")
        layout = QtWidgets.QFormLayout(self)
        names = ", ".join(b.Label for b in self.bodies[:5])
        if len(self.bodies) > 5:
            names += f" and {len(self.bodies) - 5} more"
        shown = QtWidgets.QLabel(names)
        shown.setWordWrap(True)
        layout.addRow("Bodies", shown)
        current = objects.assignment_of(study).get(self.bodies[0].Name)
        self.material = library_combo(study, current.LibraryMaterial if current else None)
        self.potential = QtWidgets.QSpinBox()
        self.potential.setRange(0, 1000000)
        if current is not None:
            self.potential.setValue(current.Potential)
        layout.addRow("Material", self.material)
        layout.addRow("POTENTIAL", self.potential)
        if not self.material.count():
            note = QtWidgets.QLabel(LIBRARY_EMPTY)
            note.setWordWrap(True)
            layout.addRow(note)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        name = self.material.currentData()
        lib = self.study.Document.getObject(name) if name else None
        if lib is None:
            return warn("Choose a material from the Material Library.")
        problem = objects.assignment_problem(self.study, self.bodies)
        if problem:
            return warn(problem)
        refs = [(b, "") for b in self.bodies if not is_air(b)]  # an Air Region keeps its own Material
        owned = objects.material_owners(self.study, refs)
        bodies = self.bodies
        if owned and not confirm_move(owned_text(owned, "body", "Materials of their own", "a Material of its own")):
            skipped = {b.Name for (b, _), _ in owned}
            bodies = [b for b in bodies if b.Name not in skipped]
        doc = self.study.Document
        doc.openTransaction("Assign material")
        try:
            objects.assign(self.study, bodies, lib, self.potential.value())
        except Exception:
            doc.abortTransaction()
            raise
        doc.commitTransaction()
        doc.recompute()
        super().accept()


def ask_bulk_assignment(study, bodies):
    BulkAssignDialog(study, bodies).exec()


def open_material_panel(study, refs=()):
    """A new Material in its panel, holding refs [(body, sub)]; the transaction stays open until OK or Cancel."""
    doc = study.Document
    doc.openTransaction("Assign material")
    try:
        panel = MaterialPanel(objects.make_material(study), new=True, refs=refs)
    except Exception:
        Gui.Selection.removeSelectionGate()  # the panel may have set it before failing
        doc.abortTransaction()
        doc.recompute()
        raise
    Gui.Control.showDialog(panel)


class _ViewProvider:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.Object = vobj.Object

    def dumps(self):
        return None

    def loads(self, state):
        return None


class ViewProviderStudy(_ViewProvider):
    def getIcon(self):
        return icon("study")

    def doubleClicked(self, vobj):
        if not Gui.Control.activeDialog():
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(vobj.Object)
        return True

    def onDelete(self, vobj, subelements):
        """Take everything the Study owns along, inside the Delete command's undo step."""
        objects.delete_contents(vobj.Object)
        return True


class ViewProviderFolder(_ViewProvider):
    """No getIcon: the standard folder icon. Its panel shows in the Tasks tab when the folder
    is selected (FolderWatcher). Double-click does nothing, so it does not start a rename."""

    def doubleClicked(self, vobj):
        return True

    def onDelete(self, vobj, subelements):
        folder = vobj.Object
        if objects.owner_study(folder) is not None:
            warn(f"{folder.Label} is part of its Study. Delete the Study to remove it.")
            return False
        for child in list(folder.Group):  # left behind without a Study: take its items along
            folder.Document.removeObject(child.Name)
        return True


def warn(text):
    QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", text)


class ViewProviderLibraryMaterial(_ViewProvider):
    """A Material Library entry: material icon; double-click edits it; deleting a used one is refused."""

    def attach(self, vobj):
        super().attach(vobj)
        vobj.addDisplayMode(coin.SoGroup(), "Default")

    def getDisplayModes(self, vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def getIcon(self):
        return icon("material")

    def doubleClicked(self, vobj):
        from . import materialstandins

        materialstandins.open_editor(objects.owner_study(vobj.Object), vobj.Object.MaterialId)
        return True

    def onDelete(self, vobj, subelements):
        users = objects.material_users(vobj.Object)
        if users:
            warn(f"{vobj.Object.Label} is used by: " + ", ".join(objects.user_labels(vobj.Object)))
            return False
        return True


AIR_COLOR = (0.68, 0.85, 1.0)  # light blue
AIR_LINE_COLOR = (0.30, 0.55, 0.85)  # a blue that keeps the outline visible through the 95 % transparency
AIR_TRANSPARENCY = 95


class ViewProviderAir(_ViewProvider):
    """The Air Region's shape, light blue and almost see-through; double-click edits it."""

    def __init__(self, vobj):
        super().__init__(vobj)
        vobj.ShapeColor = AIR_COLOR
        vobj.LineColor = AIR_LINE_COLOR
        vobj.Transparency = AIR_TRANSPARENCY
        vobj.DisplayMode = "Flat Lines" if objects.owner_study(vobj.Object).Dimension == "3D" else "Wireframe"

    def getIcon(self):
        return icon("airregion")

    def doubleClicked(self, vobj):
        if not Gui.Control.activeDialog():  # the panel's selection must not outlive it
            Gui.Control.showDialog(AirRegionPanel(vobj.Object))
        return True


class ViewProviderSlidingInterface(_ViewProvider):
    """The slide surface, drawn thick; double-click edits it."""

    def __init__(self, vobj):
        super().__init__(vobj)
        vobj.LineWidth = 3
        vobj.LineColor = (0.75, 0.22, 0.17)

    def getIcon(self):
        return icon("slidinginterface")

    def doubleClicked(self, vobj):
        if not Gui.Control.activeDialog():  # the panel's selection must not outlive it
            Gui.Control.showDialog(SlidingInterfacePanel(vobj.Object))
        return True


def _length_box(value, minimum=0.001, no_limit=False):
    box = QtWidgets.QDoubleSpinBox()
    box.setDecimals(3)
    box.setRange(0.0 if no_limit else minimum, 1e6)
    box.setSuffix(" mm")
    if no_limit:
        box.setSpecialValueText("no limit")  # shown for 0
    box.setValue(value)
    return box


class MeshSettings:
    """General mesh controls stored on the owning Study's Mesh Sizes folder."""

    def __init__(self, folder):
        self.folder = folder
        self.box = QtWidgets.QGroupBox("Mesh settings")
        form = QtWidgets.QFormLayout(self.box)
        self.default = _length_box(folder.DefaultMeshSize.Value)
        form.addRow("Default size", self.default)
        self.advanced = QtWidgets.QGroupBox("Advanced mesh settings")
        self.advanced.setCheckable(True)
        self.advanced.setChecked(True)
        self.advanced_form = QtWidgets.QWidget()
        advanced_layout = QtWidgets.QVBoxLayout(self.advanced)
        advanced_layout.addWidget(self.advanced_form)
        form.addRow(self.advanced)
        form = QtWidgets.QFormLayout(self.advanced_form)
        self.advanced_form.setVisible(True)
        self.advanced.toggled.connect(self.advanced_form.setVisible)
        self.algorithms = {}
        for prop, label in (
            ("SurfaceAlgorithm", "Surface algorithm"),
            ("VolumeAlgorithm", "Volume algorithm"),
            ("RecombinationAlgorithm", "Recombination algorithm"),
        ):
            combo = QtWidgets.QComboBox()
            if prop == "RecombinationAlgorithm":
                combo.setToolTip(
                    "Gmsh algorithm for bodies in Recombine items. Full-quad gives only quads but more of them."
                    " Full-quad needs an even number of elements on Transfinite Edges next to recombined bodies."
                )
            combo.addItems(folder.getEnumerationsOfProperty(prop))
            combo.setCurrentText(getattr(folder, prop))
            form.addRow(label, combo)
            self.algorithms[prop] = combo
        self.factor = QtWidgets.QDoubleSpinBox()
        self.factor.setDecimals(3)
        self.factor.setRange(0.01, 100.0)
        self.factor.setSingleStep(0.1)
        self.factor.setValue(folder.SizeFactor)
        form.addRow("Size factor", self.factor)
        self.min_size = _length_box(folder.MinSize.Value, no_limit=True)
        self.max_size = _length_box(folder.MaxSize.Value, no_limit=True)
        form.addRow("Min size", self.min_size)
        form.addRow("Max size", self.max_size)
        self.smoothing = QtWidgets.QSpinBox()
        self.smoothing.setRange(0, 100)
        self.smoothing.setValue(folder.SmoothingSteps)
        form.addRow("Smoothing steps", self.smoothing)
        self.netgen = QtWidgets.QCheckBox("Optimize with Netgen (slower)")
        self.netgen.setChecked(folder.OptimizeNetgen)
        form.addRow(self.netgen)
        for box in (self.default, self.factor, self.min_size, self.max_size, self.smoothing):
            box.setKeyboardTracking(False)  # typed numbers apply on Enter or leaving the box
            box.valueChanged.connect(self.save)
        for combo in self.algorithms.values():
            combo.currentTextChanged.connect(self.save)
        self.netgen.toggled.connect(self.save)

    def values(self):
        out = {prop: combo.currentText() for prop, combo in self.algorithms.items()}
        out.update(
            DefaultMeshSize=self.default.value(),
            SizeFactor=self.factor.value(),
            MinSize=self.min_size.value(),
            MaxSize=self.max_size.value(),
            SmoothingSteps=self.smoothing.value(),
            OptimizeNetgen=self.netgen.isChecked(),
        )
        return out

    def save(self, *_):
        f = self.folder
        changed = {
            p: v for p, v in self.values().items() if getattr(getattr(f, p), "Value", getattr(f, p)) != v
        }  # Value: a length
        if not changed:
            return
        f.Document.openTransaction("Edit mesh settings")
        for prop, value in changed.items():
            setattr(f, prop, value)
        f.Document.commitTransaction()
        f.Document.recompute()


_library_views = weakref.WeakSet()  # open Material Library panels


def refresh_library_views():
    for view in list(_library_views):
        try:
            view.fill()
        except (RuntimeError, ReferenceError):  # its widgets or its Study are gone
            _library_views.discard(view)


class FolderView:
    """Assignment overview, plus general settings for the Mesh Sizes folder."""

    def __init__(self, folder):
        study = objects.owner_study(folder)
        self.study = study
        self.folder_proxy = folder.Proxy
        if isinstance(folder.Proxy, objects.MaterialsFolder):
            objects.sync_labels(study)  # the tree shows "<body>: <material>"
        headers, rows = {
            objects.MaterialLibraryFolder: (["Name", "Family", "Material ID", "Used by"], objects.library_rows),
            objects.MaterialsFolder: (["Body", "Material", "MAT_ID", "POTENTIAL"], objects.material_rows),
            objects.ExcitationsFolder: (["Excitation", "Body", "Faces", "SMAT_ID"], objects.excitation_rows),
            objects.MeshSizesFolder: (["Mesh size", "Size", "Applies to"], objects.mesh_size_rows),
            objects.AirRegionsFolder: (["Air region", "Shape", "MAT_ID"], objects.air_region_rows),
        }[type(folder.Proxy)]
        self.row_source = rows
        self.rows = rows(study)
        self.form = QtWidgets.QWidget()  # the watcher's task box shows the folder name
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("Study: " + study.Label))
        if not isinstance(folder.Proxy, (objects.MaterialLibraryFolder, objects.AirRegionsFolder)):
            if objects.assignment_problem(study, []) == objects.NO_MAIN_GEOMETRY:
                notice = QtWidgets.QLabel(objects.NO_MAIN_GEOMETRY)
                notice.setStyleSheet("color: #c00000")
            else:
                notice = QtWidgets.QLabel("Only assignments on the selected geometry are exported.")
            notice.setWordWrap(True)
            layout.addWidget(notice)
        self.settings = None
        if isinstance(folder.Proxy, objects.MeshSizesFolder):
            self.settings = MeshSettings(folder)
            layout.addWidget(self.settings.box)
        self.table = QtWidgets.QTableWidget(len(self.rows), len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.fill()
        self.table.itemSelectionChanged.connect(self.highlight_rows)
        self.table.cellDoubleClicked.connect(self.open_item)
        layout.addWidget(self.table)
        if isinstance(folder.Proxy, objects.MaterialLibraryFolder):
            buttons = QtWidgets.QHBoxLayout()
            for text, slot in (
                ("Import from Material Manager…", self.import_materials),
                ("Edit…", self.edit_material),
                ("Delete", self.delete_materials),
                ("Change Material Manager root…", self.change_root),
            ):
                button = QtWidgets.QPushButton(text)
                button.clicked.connect(slot)
                buttons.addWidget(button)
            layout.addLayout(buttons)
            _library_views.add(self)
        if isinstance(folder.Proxy, objects.MaterialsFolder):
            assign = QtWidgets.QPushButton("Assign…")
            assign.setToolTip("Give the selected rows' bodies a material (Ctrl/Shift to select several rows)")
            assign.clicked.connect(self.assign_rows)
            layout.addWidget(assign)
            self.missing = QtWidgets.QLabel()
            self.missing.setWordWrap(True)
            self.missing.setStyleSheet("color: #c00000")
            layout.addWidget(self.missing)
            self.show_missing()

    def show_missing(self):
        """The red line naming bodies without a material; hidden when there are none."""
        bodies = objects.bodies_without_material(self.study)
        self.missing.setText(
            "No material (the input file needs one for every body): "
            + ", ".join(objects.display_name(b) for b in bodies)
        )
        self.missing.setVisible(bool(bodies))

    def highlight_rows(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()})
        highlight.show([ref for r in rows for ref in self.rows[r][1]])
        labels.show([self.rows[r][0] for r in rows])

    def fill(self):
        if self.study.Document is None:  # deleted objects raise ReferenceError instead
            raise ReferenceError("the Study's document was closed")
        self.rows = self.row_source(self.study)
        self.table.setRowCount(len(self.rows))
        for r, (_item, _refs, cells) in enumerate(self.rows):
            for c, text in enumerate(cells):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
        if getattr(self, "missing", None) is not None:  # Materials panel; fill() runs once before it exists
            self.show_missing()

    def selected_items(self):
        return [self.rows[r][0] for r in sorted({i.row() for i in self.table.selectedIndexes()})]

    def assign_rows(self):
        items = self.selected_items()
        if not items:
            return warn("Select one or more rows first.")
        if len(items) == 1:
            self.edit_row_material(items[0])
        elif any(isinstance(getattr(i, "Proxy", None), objects.Material) for i in items):  # edited one at a time
            warn("Select one row: the Materials of the parts of Symmetric Groups are edited one at a time.")
        else:
            ask_bulk_assignment(self.study, items)
            self.fill()

    def edit_row_material(self, item):
        """The panel of a row's Material (a symmetric Study's rows are Materials), or of a new one on its body."""
        if Gui.Control.activeDialog():  # the panel's selection gate must not outlive it
            return
        m = (
            item
            if isinstance(getattr(item, "Proxy", None), objects.Material)
            else objects.assignment_of(self.study).get(item.Name)
        )
        if m is None:
            open_material_panel(self.study, [(item, "")])
        else:
            Gui.Control.showDialog(MaterialPanel(m))

    def import_materials(self):
        from . import materialstandins

        if materialstandins.pick_materials(self.study, self.form):
            self.fill()

    def change_root(self):
        from . import materialstandins

        return materialstandins.ask_root(self.form)

    def edit_material(self):
        from . import materialstandins

        selected = self.selected_items()
        materialstandins.open_editor(self.study, selected[0].MaterialId if selected else None)

    def delete_materials(self):
        selected = self.selected_items()
        if not selected:
            return
        used = [lib for lib in selected if objects.material_users(lib)]
        if used:
            return warn("In use, not deleted: " + ", ".join(lib.Label for lib in used))
        doc = self.study.Document
        doc.openTransaction("Delete materials")
        for lib in selected:
            doc.removeObject(lib.Name)
        doc.commitTransaction()
        doc.recompute()
        self.fill()

    def open_item(self, row, _column):
        item = self.rows[row][0]
        if isinstance(getattr(item, "Proxy", None), objects.LibraryMaterial):
            from . import materialstandins

            materialstandins.open_editor(self.study, item.MaterialId)
        elif isinstance(self.folder_proxy, objects.MaterialsFolder):
            self.edit_row_material(item)
        elif Gui.Control.activeDialog():  # the panel's selection gate must not outlive it
            pass
        elif isinstance(item.Proxy, objects.SymmetricMesh):
            warn(validation.old_item_text(item))
        elif isinstance(item.Proxy, objects.SymmetricGroup):
            Gui.Control.showDialog(SymmetricGroupPanel(item))
        elif isinstance(item.Proxy, objects.AirRegion):
            Gui.Control.showDialog(AirRegionPanel(item))
        elif isinstance(item.Proxy, objects.SlidingInterface):
            Gui.Control.showDialog(SlidingInterfacePanel(item))
        else:
            Gui.Control.showDialog(ItemPanel(item))


class StudyView:
    """Overall setup, saved on the selected Study; geometry work stays in geometry.py."""

    def __init__(self, study):
        self.study = study
        set_active_study(study)
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel(f"Study: {study.Label} ({study.Dimension})"))
        form = QtWidgets.QFormLayout()
        layout.addLayout(form)
        self.movement = QtWidgets.QComboBox()
        self.movement.addItems(study.getEnumerationsOfProperty("Movement"))
        self.movement.setCurrentText(study.Movement)
        form.addRow("Movement", self.movement)
        self.slide_hint = QtWidgets.QLabel("Add an Air Region and a Sliding Interface")
        self.slide_hint.setStyleSheet("color: #c00000")
        layout.addWidget(self.slide_hint)
        self.regions, self.pending = {}, set()
        for name in ("Main", "Moving"):
            box = QtWidgets.QGroupBox()
            rows = QtWidgets.QVBoxLayout(box)
            tree = QtWidgets.QTreeWidget()
            tree.setObjectName(name + "Geometry")
            tree.setHeaderHidden(True)
            rows.addWidget(tree)
            count = QtWidgets.QLabel()
            count.setWordWrap(True)
            rows.addWidget(count)
            layout.addWidget(box)
            self.regions[name] = (box, tree, count)
            tree.itemChanged.connect(lambda _item, _col, n=name: self.ticked(n))
            tree.currentItemChanged.connect(lambda item, _prev: self.highlight_item(item))
        refresh = QtWidgets.QPushButton("Refresh geometry")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        self.diagnostics = QtWidgets.QLabel()
        self.diagnostics.setWordWrap(True)
        layout.addWidget(self.diagnostics)
        self.id_button = QtWidgets.QPushButton("Edit IDs…")
        self.id_button.clicked.connect(lambda: IdTableDialog(study).exec())
        layout.addWidget(self.id_button)
        self.validate_button = QtWidgets.QPushButton("Validate…")
        self.validate_button.clicked.connect(lambda: Gui.Control.showDialog(ValidationPanel(study)))
        layout.addWidget(self.validate_button)
        self.run_button = QtWidgets.QPushButton("Generate mesh")
        self.run_button.clicked.connect(self.run_mesh)
        layout.addWidget(self.run_button)
        self.export_notice = QtWidgets.QLabel()
        self.export_notice.setWordWrap(True)
        layout.addWidget(self.export_notice)
        self.movement.currentTextChanged.connect(self.change_movement)
        self.refresh()
        # The background run can finish while this panel stays open.
        self.run_timer = QtCore.QTimer(self.form)
        self.run_timer.timeout.connect(lambda: self.form.isVisible() and self.update_run_button())
        self.run_timer.start(500)

    def save(self, prop, value):
        if getattr(self.study, prop) == value:
            return
        doc = self.study.Document
        doc.openTransaction("Edit Study setup")
        setattr(self.study, prop, value)
        doc.commitTransaction()
        doc.recompute()

    def change_movement(self, value):
        self.save("Movement", value)
        self.refresh()

    def refresh(self):
        study = self.study
        sliding = study.Movement == "Sliding motion"
        self.slide_hint.setVisible(sliding and not (objects.air_regions(study) and objects.sliding_interfaces(study)))
        nodes = geometry.tree(study.Document, study.Dimension)
        for name, (box, tree, count) in self.regions.items():
            box.setTitle("Moving geometry" if name == "Moving" else "Fixed geometry" if sliding else "Main geometry")
            box.setVisible(name == "Main" or sliding)
            self.fill(tree, nodes, geometry.stored(study, name))
            resolved, _ = geometry.region(study, name)
            if study.Dimension == "2D":
                number = sum(len(obj.Shape.Faces) for obj in resolved)
                text = f"Included: {number} face region{'s' if number != 1 else ''} "
            else:
                number = sum(len(obj.Shape.Solids) for obj in resolved)
                text = f"Included: {number} solid{'s' if number != 1 else ''} "
            text += f"({len(resolved)} object{'s' if len(resolved) != 1 else ''})"
            count.setText(text)
        if geometry.export_unavailable(study):
            lines = geometry.setup(study)[2]
        else:  # every problem that stops the mesh; Validate Study also lists the warnings
            lines = [p.text for p in validation.errors(validation.validate(study))]
        self.diagnostics.setText("\n".join(lines))
        notice = geometry.export_unavailable(study)
        if not notice:
            try:
                notice = f"Writes {jobwriter.mesh_file(study)}"
            except jobwriter.StudyError as exc:
                notice = str(exc)
        # A path has no spaces to wrap at, so it would widen the panel: let it break after each separator.
        self.export_notice.setText(notice.replace("\\", "\\​").replace("/", "/​"))
        self.export_notice.setToolTip(notice)
        self.update_run_button()

    def update_run_button(self):
        from . import runner

        if self.study.Document is not None:
            self.run_button.setEnabled(not geometry.export_unavailable(self.study) and not runner.busy())

    def fill(self, tree, nodes, stored):
        """Show nodes with the stored objects ticked; a stored object the tree leaves out is listed last, so a
        tick elsewhere does not drop it."""
        expanded, stack = set(), [tree.invisibleRootItem()]
        while stack:
            item = stack.pop()
            stack += [item.child(i) for i in range(item.childCount())]
            if item.isExpanded():
                expanded.add(item.data(0, QtCore.Qt.UserRole))
        listed, stack = set(), list(nodes)
        while stack:
            obj, children = stack.pop()
            listed.add(obj.Name)
            stack += children or []
        nodes = nodes + [(o, None) for o in stored if o.Name not in listed]
        names = {o.Name for o in stored}

        def add(parent, nodes, ticked):
            for obj, children in nodes:
                item = QtWidgets.QTreeWidgetItem(parent, [obj.Label])
                item.setIcon(0, obj.ViewObject.Icon)
                item.setToolTip(0, obj.Name)
                item.setData(0, QtCore.Qt.UserRole, obj.Name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                if children is None:
                    item.setCheckState(0, QtCore.Qt.Checked if ticked or obj.Name in names else QtCore.Qt.Unchecked)
                else:
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsAutoTristate)
                    add(item, children, ticked or obj.Name in names)
                    item.setExpanded(obj.Name in expanded)

        tree.blockSignals(True)
        tree.clear()
        add(tree.invisibleRootItem(), nodes, False)
        tree.blockSignals(False)

    def ticked(self, name):
        # A container's tick changes each child too: save once, after all of them.
        if name not in self.pending:
            self.pending.add(name)
            QtCore.QTimer.singleShot(0, lambda: self.save_ticks(name))

    def picked(self, parent):
        """The ticked objects under parent; a fully ticked container that can be saved whole is one object."""
        out, doc = [], self.study.Document
        for item in (parent.child(i) for i in range(parent.childCount())):
            obj, state = doc.getObject(item.data(0, QtCore.Qt.UserRole)), item.checkState(0)
            if obj is None or state == QtCore.Qt.Unchecked:
                continue
            if not item.childCount() or (state == QtCore.Qt.Checked and geometry.whole(obj, self.study.Dimension)):
                out.append(obj)
            else:
                out += self.picked(item)
        return out

    def save_ticks(self, name):
        self.pending.discard(name)
        study = self.study
        if study.Document is None:
            return
        picked = self.picked(self.regions[name][1].invisibleRootItem())
        if picked == geometry.stored(study, name):
            return
        doc = study.Document
        doc.openTransaction("Choose Study geometry")
        if not picked:
            setattr(study, name + "Mode", "Unassigned")
        elif len(picked) == 1 and geometry.is_container(picked[0]):
            setattr(study, name + "Mode", "Container")
            setattr(study, name + "Source", picked[0])
        else:
            setattr(study, name + "Mode", "Manual")
            setattr(study, name + "Objects", picked)
        doc.commitTransaction()
        doc.recompute()
        self.refresh()

    def highlight_item(self, item):
        obj = item and self.study.Document.getObject(item.data(0, QtCore.Qt.UserRole))
        bodies = geometry.collect([obj], self.study.Dimension)[0] if obj is not None else []
        highlight.show([(b, "") for b in bodies])

    def run_mesh(self):
        from . import runner

        runner.start(self.study)
        self.refresh()


class StudyWatcher:
    title = "Study setup"

    def __init__(self):
        self.box = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.box)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widgets, self.view = [self.box], None

    def shouldShow(self):
        sel = Gui.Selection.getSelection()
        if len(sel) != 1 or not isinstance(getattr(sel[0], "Proxy", None), objects.Study):
            return False
        if self.view is not None:
            self.view.form.setParent(None)
            self.view.form.deleteLater()
        self.view = StudyView(sel[0])
        self.layout.addWidget(self.view.form)
        return True


class FolderWatcher:
    """Shows a folder's overview in the Tasks tab while that folder is the only selection
    and no edit dialog is open. FreeCAD calls shouldShow on every selection change."""

    def __init__(self, cls):
        self.cls = cls
        self.title = cls.LABEL
        self.box = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.box)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widgets = [self.box]
        self.view = None

    def shouldShow(self):
        sel = Gui.Selection.getSelection()
        if len(sel) != 1 or not isinstance(getattr(sel[0], "Proxy", None), self.cls):
            return False
        if self.view is not None:  # rebuild, so the table shows the latest items
            self.view.form.setParent(None)
            self.view.form.deleteLater()
        self.view = FolderView(sel[0])
        self.layout.addWidget(self.view.form)
        return True


def folder_watchers():
    return [StudyWatcher()] + [FolderWatcher(cls) for _prop, cls in objects.FOLDERS]


WORKBENCH = "EMSolutionWorkbench"


class SelectionObserver:
    """After each selection change:
    - a single selected item highlights its bodies, faces, edges and vertices;
    - selecting a study object while another workbench is active switches to EMSolution,
      so its panel can show. Bodies and faces do not switch.
    Neither happens during an edit."""

    def __init__(self):
        self.pending = False

    def addSelection(self, doc, obj, sub, pnt):
        self.later()

    def removeSelection(self, doc, obj, sub):
        self.later()

    def setSelection(self, doc):
        self.later()

    def clearSelection(self, doc):
        self.later()

    def later(self):
        if not self.pending:  # one update for a burst of events
            self.pending = True
            QtCore.QTimer.singleShot(0, self.update)  # acting inside the selection event is unsafe

    def update(self):
        self.pending = False
        sel = Gui.Selection.getSelection()
        editing = Gui.Control.activeDialog()
        if not editing:
            active_study()  # remember a Study when its tree item is selected
        if editing:
            pass  # an open item panel highlights its own selected rows
        elif len(sel) == 1 and objects.is_item(sel[0]):
            highlight.show(objects.item_refs(sel[0]))
            labels.show(sel)
        else:
            highlight.clear()
            labels.clear()
        if editing or Gui.activeWorkbench().name() == WORKBENCH:
            return
        if any(objects.is_study_object(o) for o in sel):
            Gui.activateWorkbench(WORKBENCH)


_observer = None


def install_selection_observer():
    global _observer
    if _observer is None:
        _observer = SelectionObserver()
        Gui.Selection.addObserver(_observer)


class ViewProviderItem(_ViewProvider):
    """Draws nothing, but needs a display mode: without one the tree greys the item out
    as hidden. Hiding is undone, as there is nothing to hide."""

    def attach(self, vobj):
        super().attach(vobj)
        vobj.addDisplayMode(coin.SoGroup(), "Default")

    def getDisplayModes(self, vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def onChanged(self, vobj, prop):
        if prop == "Visibility" and not vobj.Visibility:  # later: FreeCAD hides after this call
            QtCore.QTimer.singleShot(0, vobj.show)

    def getIcon(self):
        obj = getattr(self, "Object", None)
        return icon(type(obj.Proxy).__name__.lower()) if obj else icon("emsolution")

    def doubleClicked(self, vobj):
        obj = vobj.Object
        if Gui.Control.activeDialog():  # the panel's selection gate must not outlive it
            pass
        elif isinstance(obj.Proxy, objects.Material):
            Gui.Control.showDialog(MaterialPanel(obj))
        elif isinstance(obj.Proxy, objects.SymmetricMesh):  # an older version's item: nothing to edit
            warn(validation.old_item_text(obj))
        elif isinstance(obj.Proxy, objects.SymmetricGroup):  # saved with this view provider before it had its own
            Gui.Control.showDialog(SymmetricGroupPanel(obj))
        else:
            Gui.Control.showDialog(ItemPanel(obj))
        return True


class ViewProviderGroup(_ViewProvider):
    """A Symmetric Group: its drawing is shown by the shape's own view provider, so clicks land on its faces."""

    def getIcon(self):
        return icon("symmetricmesh")

    def doubleClicked(self, vobj):
        if not Gui.Control.activeDialog():  # another panel's selection gate must not outlive it
            Gui.Control.showDialog(SymmetricGroupPanel(vobj.Object))
        return True


def attach_view_provider(obj):
    """Give an EMSolution object the view provider it gets at creation. Returns it, or None for any other object."""
    proxy = getattr(obj, "Proxy", None)
    if isinstance(proxy, objects.Study):
        return ViewProviderStudy(obj.ViewObject)
    if isinstance(proxy, objects.Folder):
        return ViewProviderFolder(obj.ViewObject)
    if isinstance(proxy, objects.LibraryMaterial):
        return ViewProviderLibraryMaterial(obj.ViewObject)
    if isinstance(proxy, objects.AirRegion):
        return ViewProviderAir(obj.ViewObject)
    if isinstance(proxy, objects.SlidingInterface):
        return ViewProviderSlidingInterface(obj.ViewObject)
    if isinstance(proxy, objects.SymmetricGroup):
        return ViewProviderGroup(obj.ViewObject)
    if isinstance(proxy, objects._Proxy):  # Material, Excitation and the mesh items
        return ViewProviderItem(obj.ViewObject)
    return None


class OpenObserver:
    """A document a script built without the GUI has no view providers (no GuiDocument.xml), so when one is opened,
    its EMSolution objects get theirs. A document saved from the GUI keeps its own.

    The Python observers get no restore signal. A document is activated twice while it opens, the second time once
    its objects exist, and activating one later finds nothing missing."""

    def slotActivateDocument(self, doc):
        if doc.Restoring:
            return
        for obj in doc.Objects:
            view = getattr(obj, "ViewObject", None)
            if view is not None and isinstance(getattr(obj, "Proxy", None), objects._Proxy):
                if not isinstance(view.Proxy, _ViewProvider):  # an int until set
                    attach_view_provider(obj)


_open_observer = None


def install_open_observer():
    global _open_observer
    if _open_observer is None:
        _open_observer = OpenObserver()
        App.addDocumentObserver(_open_observer)


class ItemGate:
    """While an item panel is open, the 3D view and tree can only pick what it takes, on the main geometry."""

    def __init__(self, study, kinds, whole, air=True, regions=False):
        """regions: any click on a one-face body picks that region (2D face picks)."""
        bodies = objects.assignable(study) if air else objects.study_bodies(study) + objects.symmetric_groups(study)
        self.main = {b.Name for b in bodies + objects.cell_bodies(study)}  # a symmetric Study meshes its cells
        self.kinds, self.whole, self.regions = kinds, whole, regions

    def allow(self, doc, obj, sub):
        if not Gui.Control.activeDialog():  # the panel was closed without OK or Cancel
            return True
        body = objects.pick_body(obj)
        if body is None or body.Name not in self.main:
            return False
        if not sub:
            return self.whole
        if self.regions and len(body.Shape.Faces) == 1:
            return sub.startswith(ANY_SUB)
        return sub.startswith(self.kinds)


def picked_bodies(study):
    """Whole bodies picked: a click anywhere on a body picks it, and a click on a face of a Symmetric Group's drawing
    picks the cell body that face is a copy of."""
    tops = drawing_names(study)
    faces = [(b, s) for b, s in selected_subs(("Face",)) if b.Name in tops]
    clicked = {b.Name for b, _ in faces}
    cells = [(b, "") for b, _ in objects.to_cells(study, faces, whole=True)]  # one no copy explains: the drawing
    return list(dict.fromkeys([(b, "") for b in selected_bodies() if b.Name not in clicked] + cells))


def mesh_picks(study, kinds):
    """Picked sub-elements named kinds[i]N, those on a Symmetric Group's drawing moved to the cell."""
    return objects.to_cells(study, selected_subs(kinds))


ANY_SUB = ("Face", "Edge", "Vertex")
# proxy: (pick(study), list label, sub-elements the gate lets through, whole bodies too?, hint for 3D, hint for 2D)
ITEM_PICKS = {
    objects.Excitation: (
        lambda study: selected_faces(),
        "Faces",
        ("Face",),
        False,
        "Click faces in the 3D view.",
        "3D only",
    ),
    objects.TransfiniteBody: (
        lambda study: picked_bodies(study) + mesh_picks(study, ("Vertex",)),
        "Bodies,\ncorner vertices",
        ANY_SUB,
        True,
        "Click a solid to add it. Clicked vertices become face corners.",
        "Click a region to add it. Clicked vertices become its corners.",
    ),
    objects.Recombine: (
        picked_bodies,
        "Bodies",
        ANY_SUB,
        True,
        "Click solids in the 3D view.",
        "Click regions in the 3D view.",
    ),
    objects.TransfiniteEdges: (
        lambda study: mesh_picks(study, ("Edge",)),
        "Edges",
        ("Edge",),
        False,
        "Click edges in the 3D view.",
        "Click edges in the 3D view.",
    ),
    objects.MeshSize: (
        lambda study: objects.to_cells(study, selected_mesh_refs()),
        "Bodies, faces,\nedges, vertices",
        ANY_SUB,
        True,
        "Click faces, edges or vertices in the 3D view, or a solid in the tree.",
        "Click regions, edges or vertices in the 3D view.",
    ),
}
# in a 2D Study: (pick, list label, gate kinds, hint) replacing those of ITEM_PICKS
ITEM_PICKS_2D = {
    objects.TransfiniteBody: (
        lambda study: selected_face_picks(study, True),
        "Bodies, faces,\ncorner vertices",
        ("Face", "Vertex"),
        "Click a face to structure that block, or select the body in the tree for all its faces."
        " Clicked vertices become corners.",
    ),
    objects.Recombine: (
        lambda study: selected_face_picks(study, False),
        "Bodies, faces",
        ("Face",),
        "Click a face to recombine that block, or select the body in the tree for all its faces.",
    ),
}


class ItemPanel:
    """Edit name, settings and references of an Excitation, Mesh Size, Recombine or transfinite item.
    new: obj was just made inside an open transaction; OK commits it, Cancel undoes it.
    While open, a selection gate limits picks to what the item takes; closing removes it."""

    def __init__(self, obj, new=False):
        self.obj = obj
        self.new = new
        study = objects.owner_study(obj)
        highlight.clear()  # the list's selected rows are highlighted instead
        self.pick, label, kinds, whole, hint3d, hint2d = ITEM_PICKS[type(obj.Proxy)]
        regions = study.Dimension == "2D" and type(obj.Proxy) in ITEM_PICKS_2D
        if regions:
            self.pick, label, kinds, hint2d = ITEM_PICKS_2D[type(obj.Proxy)]
        self.takes = label.replace("\n", " ").lower()
        air = isinstance(obj.Proxy, objects.MeshSize)  # the air is not recombined, structured or excited
        self.gate = ItemGate(study, kinds, whole, air, regions)
        Gui.Selection.addSelectionGate(self.gate)  # replaces any filter the user set
        self.current = objects.item_refs(obj)
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QFormLayout(self.form)
        layout.addRow(QtWidgets.QLabel("Study: " + study.Label))
        region = "main and moving geometry" if study.Movement == "Sliding motion" else "main geometry"
        hint = QtWidgets.QLabel(
            (hint2d if study.Dimension == "2D" else hint3d) + f" Only the Study's {region} can be picked."
        )
        hint.setWordWrap(True)
        layout.addRow(hint)
        self.others = labels.others_checkbox()
        layout.addRow(self.others)
        self.name = QtWidgets.QLineEdit(objects.display_name(obj))
        layout.addRow("Name", self.name)
        self.size = None
        if isinstance(obj.Proxy, objects.MeshSize):
            self.size = _length_box(obj.Size.Value)
            layout.addRow("Size", self.size)
        self.elements = self.distribution = self.bump = None
        if isinstance(obj.Proxy, objects.TransfiniteEdges):
            self.elements = QtWidgets.QSpinBox()
            self.elements.setRange(1, 100000)
            self.elements.setValue(obj.Elements)
            layout.addRow("Elements", self.elements)
            self.distribution = QtWidgets.QComboBox()
            self.distribution.addItems(obj.getEnumerationsOfProperty("Distribution"))
            self.distribution.setCurrentText(obj.Distribution)
            layout.addRow("Distribution", self.distribution)
            self.bump = QtWidgets.QDoubleSpinBox()
            self.bump.setDecimals(3)
            self.bump.setRange(0.001, 1000.0)
            self.bump.setValue(obj.BumpCoefficient)
            self.bump.setEnabled(obj.Distribution == "Bump")
            layout.addRow("Bump coefficient", self.bump)
            self.distribution.currentTextChanged.connect(lambda text: self.bump.setEnabled(text == "Bump"))
        self.refs = QtWidgets.QListWidget()
        self.refs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.refs.itemSelectionChanged.connect(self.highlight_rows)
        layout.addRow(label, self.refs)
        add = QtWidgets.QPushButton("Add selection")
        remove = QtWidgets.QPushButton("Remove")
        add.clicked.connect(self.add_selection)
        remove.clicked.connect(self.remove)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(add)
        buttons.addWidget(remove)
        layout.addRow(buttons)
        self.refresh()
        labels.show([obj], self.others.isChecked(), {obj.Name: self.current}, {obj.Name: self.unsaved()})
        for signal in (
            self.name.textChanged,
            self.size and self.size.valueChanged,
            self.elements and self.elements.valueChanged,
            self.distribution and self.distribution.currentTextChanged,
        ):
            if signal is not None:
                signal.connect(lambda _value: labels.set_values(self.obj, self.unsaved()))

    def unsaved(self):
        """What the panel shows and has not saved yet, for the labels."""
        values = {"Name": self.name.text().strip() or objects.display_name(self.obj)}
        if self.size is not None:
            values["Size"] = self.size.value()
        if self.elements is not None:
            values.update(Elements=self.elements.value(), Distribution=self.distribution.currentText())
        return values

    def refresh(self):
        self.refs.clear()
        self.refs.addItems([objects.ref_label(b, f) for b, f in self.current])
        labels.set_refs(self.obj, self.current)

    def highlight_rows(self):
        highlight.show([self.current[r] for r in sorted({i.row() for i in self.refs.selectedIndexes()})])

    def close(self):
        """Undo what the open panel changed outside itself."""
        Gui.Selection.removeSelectionGate()
        highlight.clear()
        labels.clear()

    def autoClosedOnDeletedDocument(self):  # FreeCAD closed the panel with its document
        self.close()

    def add_selection(self):
        study, cls = objects.owner_study(self.obj), type(self.obj.Proxy)
        new = self.pick(study)

        def problem_of(bodies):
            return objects.assignment_problem(study, bodies) or objects.air_refusal(cls, bodies)

        problem = problem_of([b for b, _ in new])
        if problem:
            warn(problem)
            new = [(b, f) for b, f in new if not problem_of([b])]
        have = {(b.Name, f) for b, f in self.current}
        added = [(b, f) for b, f in new if (b.Name, f) not in have]
        if not added and not problem:
            warn(self.nothing_added())
        self.current += added
        self.refresh()

    def nothing_added(self):
        sel = Gui.Selection.getSelectionEx()
        if not sel:
            return "Nothing is selected. Pick geometry in the 3D view first."
        other = [s.Object.Label for s in sel if objects.pick_body(s.Object) is None]
        if other:
            return "Not geometry: " + ", ".join(other) + ". If a mesh result covers the bodies, hide it and pick again."
        return f"Nothing new to add: the selection is already in the list, or not {self.takes}."

    def remove(self):
        rows = {i.row() for i in self.refs.selectedIndexes()}
        self.current = [r for i, r in enumerate(self.current) if i not in rows]
        self.refresh()

    def accept(self):
        if self.new and not self.current:
            warn("Select geometry in the 3D view and click Add selection.")
            return False
        doc = self.obj.Document
        if not self.new:  # a new item's transaction is already open
            doc.openTransaction("Edit " + self.obj.Label)
        name = self.name.text().strip()
        if name:
            self.obj.Label = name
            if hasattr(self.obj, "GroupName"):
                self.obj.GroupName = name  # FreeCAD may have suffixed the Label
        if self.size is not None:
            self.obj.Size = self.size.value()
        if self.elements is not None:
            self.obj.Elements = self.elements.value()
            self.obj.Distribution = self.distribution.currentText()
            self.obj.BumpCoefficient = self.bump.value()
        if isinstance(self.obj.Proxy, objects.TransfiniteBody):
            self.obj.References, self.obj.Corners = objects.split_corners(self.current)
        else:
            self.obj.References = list(self.current)
        doc.commitTransaction()
        doc.recompute()
        self.close()
        Gui.Control.closeDialog()
        return True

    def reject(self):
        if self.new:
            doc = self.obj.Document
            doc.abortTransaction()  # removes the new item
            doc.recompute()
        self.close()
        Gui.Control.closeDialog()
        return True


def _key(ref):
    return (ref[0].Name, ref[1])


ONE_BODY = (
    "A Material holds one body: select one, or use Assign Material with several bodies selected to give each its"
    " own Material."
)


class MaterialPanel:
    """Edit a Material: its name, library material, POTENTIAL and what it covers, one body or Air Region. Picking
    what another Material covers moves it here, after asking.
    The Material of a part of a Symmetric Group (PartKey set) edits name, library material and POTENTIAL only: its
    list shows its copies, and "All parts of this object" gives the chosen library material to every part of the
    object the part is a copy of (row: (group, row), default the part's first copy).
    new: obj was just made inside an open transaction; OK commits it, Cancel undoes it. A part's panel opens
    its own transaction, so Cancel also undoes "All parts of this object".
    While open, a selection gate limits picks to what a Material takes; closing removes it."""

    def __init__(self, obj, new=False, refs=(), row=None):
        self.obj, self.new = obj, new
        self.study = study = objects.owner_study(obj)
        self.part = bool(getattr(obj, "PartKey", ""))
        self.row = (row or objects.part_row(obj)) if self.part else None
        self.held = new or self.part  # the panel holds the transaction its OK commits
        if self.part:
            obj.Document.openTransaction("Edit " + obj.Label)
        self.air = obj.Body if obj.Body is not None and is_air(obj.Body) else None
        self.current = objects.item_refs(obj)
        highlight.clear()  # the list's selected rows are highlighted instead
        self.gate = ItemGate(study, ANY_SUB, True)
        if not self.part:  # a part takes no picks
            Gui.Selection.addSelectionGate(self.gate)  # replaces any filter the user set
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("New Material" if new else obj.Label)
        layout = QtWidgets.QFormLayout(self.form)
        layout.addRow(QtWidgets.QLabel("Study: " + study.Label))
        region = "main and moving geometry" if study.Movement == "Sliding motion" else "main geometry"
        if self.part:
            text = "This is the Material of a part of a Symmetric Group; its copies are listed below."
        elif study.Dimension == "2D":
            text = "Click a region in the 3D view, or select a body or the Air Region in the tree."
        else:
            text = "Click a solid in the 3D view, or select a body or the Air Region in the tree."
        hint = QtWidgets.QLabel(text if self.part else f"{text} Only the Study's {region} can be picked.")
        hint.setWordWrap(True)
        layout.addRow(hint)
        self.others = labels.others_checkbox()
        layout.addRow(self.others)
        self.name = QtWidgets.QLineEdit(objects.display_name(obj))
        self.typed = not new  # the name follows the suggestion until it is typed in
        self.name.textEdited.connect(self.name_typed)
        layout.addRow("Name", self.name)
        self.air_note = QtWidgets.QLabel("Named after its Air Region; rename it there.")
        layout.addRow(self.air_note)
        self.material = library_combo(study, obj.LibraryMaterial)
        self.material.currentIndexChanged.connect(lambda _index: self.suggest())
        layout.addRow("Material", self.material)
        self.potential = QtWidgets.QSpinBox()
        self.potential.setRange(0, 1000000)
        self.potential.setValue(obj.Potential)
        layout.addRow("POTENTIAL", self.potential)
        if not self.material.count():
            note = QtWidgets.QLabel(LIBRARY_EMPTY)
            note.setWordWrap(True)
            layout.addRow(note)
        self.refs = QtWidgets.QListWidget()
        self.refs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.refs.itemSelectionChanged.connect(self.highlight_rows)
        layout.addRow("Copies" if self.part else "Body", self.refs)
        self.add_button = add = QtWidgets.QPushButton("Add selection")
        self.remove_button = remove = QtWidgets.QPushButton("Remove")
        add.clicked.connect(self.add_selection)
        remove.clicked.connect(self.remove)
        add.setEnabled(self.air is None and not self.part)  # an Air Region keeps its Material; a part its copies
        remove.setEnabled(self.air is None and not self.part)
        self.name.setReadOnly(self.air is not None)
        self.air_note.setVisible(self.air is not None)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(add)
        buttons.addWidget(remove)
        layout.addRow(buttons)
        self.all_parts = QtWidgets.QPushButton("All parts of this object")
        self.all_parts.setToolTip("Give the library material shown to every part of the object this part is a copy of")
        self.all_parts.clicked.connect(self.set_all_parts)
        self.all_parts.setVisible(self.row is not None)
        layout.addRow(self.all_parts)
        self.note = QtWidgets.QLabel()
        self.note.setWordWrap(True)
        layout.addRow(self.note)
        if refs:
            self.take(list(refs))
        self.refresh()
        labels.show([obj], self.others.isChecked(), {obj.Name: self.current}, {obj.Name: self.unsaved()})
        self.material.currentIndexChanged.connect(lambda _index: labels.set_values(self.obj, self.unsaved()))

    def unsaved(self):
        """What the panel shows and has not saved yet, for the labels."""
        lib = self.lib()
        return {"Material": lib.Label if lib else objects.NO_MATERIAL}

    def name_typed(self, _text):
        self.typed = True

    def lib(self):
        name = self.material.currentData()
        return self.study.Document.getObject(name) if name else None

    def gone(self):
        """The other Materials OK removes, as they have nothing left: their names are free."""
        return [] if self.part else objects.emptied_by(self.study, self.current, own=self.obj)

    def set_all_parts(self):
        """The library material shown goes to every part of the row: the panel's transaction undoes it on Cancel."""
        lib = self.lib()
        if lib is None:
            return warn(LIBRARY_EMPTY if not self.material.count() else "Choose a material from the Material Library.")
        group, row = self.row
        objects.set_row_material(self.study, group, row, lib)

    def suggest(self):
        if self.air is not None:
            self.name.setText(objects.display_name(self.air))
        elif not self.typed:
            self.name.setText(objects.suggest_name(self.study, self.current, self.lib(), self.obj, self.gone()))

    def refresh(self):
        self.refs.clear()
        self.refs.addItems([objects.ref_label(b, s) for b, s in self.current])
        gone = self.gone()
        self.note.setText("\n".join(f'"{objects.display_name(m)}" will be removed: it has nothing left.' for m in gone))
        self.note.setVisible(bool(gone))
        labels.set_refs(self.obj, self.current)

    def highlight_rows(self):
        highlight.show([self.current[r] for r in sorted({i.row() for i in self.refs.selectedIndexes()})])

    def picks(self):
        """What the selection offers: whole bodies."""
        return [(b, "") for b in selected_bodies()]

    def take(self, picks):
        """Add picks [(body, sub)] to the list, refusing what a Material cannot take and asking before moving what
        another Material covers. Returns whether anything was added."""
        problem = objects.assignment_problem(self.study, [b for b, _ in picks])
        if problem:
            warn(problem)
            picks = [p for p in picks if not objects.assignment_problem(self.study, [p[0]])]
        airs = [p for p in picks if is_air(p[0]) and objects.air_material(self.study, p[0]) not in (None, self.obj)]
        if airs:  # one without a Material gets it here
            warn("An Air Region keeps its own Material: open it from the Air Region's row.")
            picks = [p for p in picks if p not in airs]
        have = {_key(r) for r in self.current}
        picks = list({_key(p): p for p in picks if _key(p) not in have}.values())
        if not picks:
            return False
        if len(picks) > 1:
            warn(ONE_BODY)
            return False
        owned = objects.material_owners(self.study, picks, own=self.obj)
        if owned:
            gone = objects.emptied_by(self.study, picks, own=self.obj)
            name = self.name.text().strip() if self.typed else ""
            name = name or objects.suggest_name(self.study, picks, self.lib(), self.obj, gone) or "this Material"
            if not confirm_move(owned_text(owned, "body", f'"{name}"')):
                return False
        self.current = picks
        self.air = picks[0][0] if is_air(picks[0][0]) else None  # an Air Region's Material is named after it
        self.name.setReadOnly(self.air is not None)
        self.air_note.setVisible(self.air is not None)
        self.refresh()
        self.suggest()
        return True

    def add_selection(self):
        picks = self.picks()
        if not self.take(picks) and not picks:
            if not Gui.Selection.getSelectionEx():
                warn("Nothing is selected. Pick geometry in the 3D view first.")
            else:
                warn("Nothing new to add.")

    def remove(self):
        rows = {i.row() for i in self.refs.selectedIndexes()}
        self.current = [r for i, r in enumerate(self.current) if i not in rows]
        self.refresh()
        self.suggest()

    def close(self):
        """Undo what the open panel changed outside itself."""
        Gui.Selection.removeSelectionGate()
        highlight.clear()
        labels.clear()

    def autoClosedOnDeletedDocument(self):  # FreeCAD closed the panel with its document
        self.close()

    def accept(self):
        name, lib = self.name.text().strip(), self.lib()
        if not self.current and not self.part:
            warn("Select geometry in the 3D view and click Add selection.")
            return False
        if not name:
            warn("Give the Material a name.")
            return False
        if lib is None:
            warn(LIBRARY_EMPTY if not self.material.count() else "Choose a material from the Material Library.")
            return False
        if self.air is None and objects.name_taken(self.study, name, self.obj, self.gone()):
            warn(f'Another Material is already named "{name}" (spaces and symbols count as "_" in the mesh).')
            return False
        doc = self.obj.Document
        if not self.held:  # a new item's or a part's transaction is already open
            doc.openTransaction("Edit " + self.obj.Label)
        try:
            if self.part:
                objects.apply_part_material(self.obj, name, lib, self.potential.value())
            else:
                objects.apply_material(self.study, self.obj, name, lib, self.potential.value(), self.current)
        except Exception:
            doc.abortTransaction()
            self.close()
            Gui.Control.closeDialog()
            raise
        doc.commitTransaction()
        doc.recompute()
        self.close()
        Gui.Control.closeDialog()
        return True

    def reject(self):
        if self.held:
            doc = self.obj.Document
            doc.abortTransaction()  # removes the new Material, or undoes what a part's panel changed
            doc.recompute()
        self.close()
        Gui.Control.closeDialog()
        return True


PART_MODES = [
    ("one", "One part"),
    ("each", "Each copy separate"),
    ("across", "Merged across ticked rules"),
    ("table", "Table"),
]


def _num(v):
    return f"{round(v, 6) + 0.0:g}"


def _vector_text(v):
    return "(" + ", ".join(_num(c) for c in v) + ")"


def rule_text(n, rule):
    """One line for rule n (from 1): "2. Rotate 30° × 12 about (0, 0, 1) through (0, 0, 0)"."""
    kind = rule["kind"]
    if kind == "mirror":
        return f"{n}. Mirror in the plane through {_vector_text(rule['point'])}, normal {_vector_text(rule['normal'])}"
    if kind == "rotate":
        axis, point = _vector_text(rule["axis"]), _vector_text(rule["point"])
        return f"{n}. Rotate {_num(rule['step'])}° × {rule['count']} about {axis} through {point}"
    if kind == "translate":
        return f"{n}. Translate {_vector_text(rule['vector'])} × {rule['count']}"
    return f"{n}. Motion × {rule['count']}"


def _number_box(minimum=-1e6, maximum=1e6, suffix=""):
    box = QtWidgets.QDoubleSpinBox()
    box.setDecimals(10)  # a normal at 15° or a step of 360/7 rounded to 6 places leaves the copies micrometres off
    box.setRange(minimum, maximum)
    box.setSuffix(suffix)
    box.setKeyboardTracking(False)  # a value is written when typed in, not at every key
    return box


def ask_proposal(proposals):
    """The index of the proposal of rules_from_chain to take, or None on Cancel."""
    texts = [
        f"{', '.join(b.Label for b in p.cells)}: {len(p.rules)} rules, {symmetry.copy_count(p.rules)} copies"
        for p in proposals
    ]
    text, ok = QtWidgets.QInputDialog.getItem(
        Gui.getMainWindow(), "Read from drawing", "The drawing copies these bodies differently. Take:", texts, 0, False
    )
    return texts.index(text) if ok else None


class SymmetricGroupPanel:
    """Edit a Symmetric Group: its cell objects, what the copies of each become, and the ordered rules that copy them.
    Every change is written as it is made and the drawing recomputed, so the 3D view shows the copies, inside one
    transaction: OK commits it and makes a Material per new part, Cancel undoes it. new: obj was just made inside the
    command's open transaction, so Cancel removes it."""

    def __init__(self, obj, new=False):
        self.obj, self.new = obj, new
        self.study = study = objects.owner_study(obj)
        self.doc = obj.Document
        if objects.stale_drawing(obj):  # a container of a cell was moved; outside the transaction, so Cancel keeps it
            obj.touch()
            self.doc.recompute()
        if not new:  # a new item's transaction is already open
            self.doc.openTransaction("Edit " + obj.Label)
        highlight.clear()
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QVBoxLayout(self.form)
        top = QtWidgets.QFormLayout()
        layout.addLayout(top)
        top.addRow(QtWidgets.QLabel("Study: " + study.Label))
        hint = QtWidgets.QLabel(
            "Select the cell objects and click Use selection, then add the rules. Each rule copies everything made"
            " before it; the drawing in the 3D view shows every copy."
        )
        hint.setWordWrap(True)
        top.addRow(hint)
        self.name = QtWidgets.QLineEdit(objects.display_name(obj))
        top.addRow("Name", self.name)
        self.side = QtWidgets.QComboBox()
        self.side.addItems(obj.getEnumerationsOfProperty("Side"))
        self.side.setCurrentText(obj.Side)
        self.side_label = QtWidgets.QLabel("Side")
        top.addRow(self.side_label, self.side)
        sliding = study.Movement == "Sliding motion"
        self.side.setVisible(sliding)
        self.side_label.setVisible(sliding)
        self.side.currentTextChanged.connect(self.write_side)

        cells = QtWidgets.QGroupBox("Cell objects and what their copies become")
        cells_layout = QtWidgets.QVBoxLayout(cells)
        self.rows = QtWidgets.QTableWidget()
        self.rows.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.rows.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.rows.verticalHeader().setVisible(False)
        self.rows.itemChanged.connect(self.write_tick)
        self.rows.currentCellChanged.connect(lambda *_: self.show_state())
        cells_layout.addWidget(self.rows)
        self.use_selection = QtWidgets.QPushButton("Use selection")
        self.use_selection.setToolTip("The selected bodies become the cell objects")
        self.read_drawing = QtWidgets.QPushButton("Read from drawing")
        self.read_drawing.setToolTip("Select the top of a Mirror / Polar Array drawing: its cell bodies and rules")
        self.table_button = QtWidgets.QPushButton("Table…")
        self.table_button.setToolTip("Name the part of each copy of the selected row, or generate a winding")
        cells_layout.addLayout(self._buttons(self.use_selection, self.read_drawing, self.table_button))
        layout.addWidget(cells)

        rules = QtWidgets.QGroupBox("Rules, in the order they apply")
        rules_layout = QtWidgets.QVBoxLayout(rules)
        self.rules = QtWidgets.QListWidget()
        self.rules.currentRowChanged.connect(lambda _row: self.show_rule())
        rules_layout.addWidget(self.rules)
        self.add_mirror = QtWidgets.QPushButton("Mirror")
        self.add_rotate = QtWidgets.QPushButton("Rotate")
        self.add_translate = QtWidgets.QPushButton("Translate")
        rules_layout.addLayout(
            self._buttons(QtWidgets.QLabel("Add"), self.add_mirror, self.add_rotate, self.add_translate)
        )
        self.remove_rule = QtWidgets.QPushButton("Remove")
        self.rule_up = QtWidgets.QPushButton("Up")
        self.rule_down = QtWidgets.QPushButton("Down")
        rules_layout.addLayout(self._buttons(self.remove_rule, self.rule_up, self.rule_down))
        self.editor = QtWidgets.QWidget()
        fields = QtWidgets.QFormLayout(self.editor)
        fields.setContentsMargins(0, 0, 0, 0)
        self.point = [_number_box(suffix=" mm") for _ in range(3)]
        self.point_label = QtWidgets.QLabel("Point")
        fields.addRow(self.point_label, self._buttons(*self.point))
        self.direction = [_number_box() for _ in range(3)]
        self.direction_label = QtWidgets.QLabel("Normal")
        fields.addRow(self.direction_label, self._buttons(*self.direction))
        self.step = _number_box(-360, 360, "°")
        self.step_label = QtWidgets.QLabel("Step")
        fields.addRow(self.step_label, self.step)
        self.count = QtWidgets.QSpinBox()
        self.count.setRange(2, 1000000)
        self.count.setKeyboardTracking(False)
        self.count_label = QtWidgets.QLabel("Count")
        fields.addRow(self.count_label, self.count)
        rules_layout.addWidget(self.editor)
        layout.addWidget(rules)

        self.summary = QtWidgets.QLabel()
        layout.addWidget(self.summary)
        self.problem = QtWidgets.QLabel()
        self.problem.setWordWrap(True)
        self.problem.setStyleSheet("color: #c0392b")
        layout.addWidget(self.problem)

        self.use_selection.clicked.connect(self.take_selection)
        self.read_drawing.clicked.connect(self.read_chain)
        self.table_button.clicked.connect(self.open_table)
        self.add_mirror.clicked.connect(lambda: self.add_rule("mirror"))
        self.add_rotate.clicked.connect(lambda: self.add_rule("rotate"))
        self.add_translate.clicked.connect(lambda: self.add_rule("translate"))
        self.remove_rule.clicked.connect(self.drop_rule)
        self.rule_up.clicked.connect(lambda: self.move_rule(-1))
        self.rule_down.clicked.connect(lambda: self.move_rule(1))
        for box in self.point + self.direction + [self.step]:
            box.valueChanged.connect(lambda _value: self.write_rule())
        self.count.valueChanged.connect(lambda _value: self.write_rule())
        self.refresh(0)

    @staticmethod
    def _buttons(*widgets):
        row = QtWidgets.QHBoxLayout()
        for w in widgets:
            row.addWidget(w)
        return row

    def plane(self):
        """ "" in 3D, else the plane of the cell objects ("XY" or "ZX"), as Validate takes it."""
        return "" if self.study.Dimension == "3D" else airshapes.plane_of_bodies(self.obj.Cells)

    # ---- showing

    def refresh(self, rule=None):
        """Show the group again; rule: the row of the rule list to select (else the current one)."""
        rules = objects.rules_of(self.obj)
        current = self.rules.currentRow() if rule is None else rule
        self.rules.blockSignals(True)
        self.rules.clear()
        self.rules.addItems([rule_text(n, r) for n, r in enumerate(rules, 1)])
        self.rules.setCurrentRow(min(current, len(rules) - 1))
        self.rules.blockSignals(False)
        self.fill_rows()
        self.show_rule()
        self.show_state()

    def fill_rows(self):
        rows, count = objects.rows_of(self.obj), len(objects.rules_of(self.obj))
        current = self.rows.currentRow()
        self.rows.blockSignals(True)
        self.rows.clear()
        self.rows.setColumnCount(2 + count)
        self.rows.setHorizontalHeaderLabels(["Object", "Parts"] + [str(n) for n in range(1, count + 1)])
        for n in range(count):
            self.rows.horizontalHeaderItem(2 + n).setToolTip(
                f"Merged across rule {n + 1}: copies that differ only in the ticked rules are one part"
            )
        self.rows.setRowCount(len(rows))
        for r, row in enumerate(rows):
            label = QtWidgets.QTableWidgetItem(objects.row_label(self.obj, row))
            label.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.rows.setItem(r, 0, label)
            mode = QtWidgets.QComboBox()
            for key, text in PART_MODES:
                mode.addItem(text, key)
            mode.setCurrentIndex(max(mode.findData(row.get("mode", "one")), 0))
            mode.currentIndexChanged.connect(lambda _index, r=r, box=mode: self.write_mode(r, box.currentData()))
            self.rows.setCellWidget(r, 1, mode)
            for n in range(count):
                tick = QtWidgets.QTableWidgetItem()
                tick.setCheckState(QtCore.Qt.Checked if n in row.get("across", []) else QtCore.Qt.Unchecked)
                self.rows.setItem(r, 2 + n, tick)
            self.show_ticks(r, row.get("mode"))
        self.rows.resizeColumnsToContents()
        if 0 <= current < len(rows):
            self.rows.setCurrentCell(current, 0)
        self.rows.blockSignals(False)

    def show_ticks(self, r, mode):
        """The ticks of row r can be clicked only when its copies are merged across ticked rules."""
        flags = QtCore.Qt.ItemIsUserCheckable | (QtCore.Qt.ItemIsEnabled if mode == "across" else QtCore.Qt.NoItemFlags)
        blocked = self.rows.blockSignals(True)
        for column in range(2, self.rows.columnCount()):
            self.rows.item(r, column).setFlags(flags)
        self.rows.blockSignals(blocked)

    def show_rule(self):
        """The editor shows the selected rule's values; nothing is written while they are filled in."""
        rules, i = objects.rules_of(self.obj), self.rules.currentRow()
        rule = rules[i] if 0 <= i < len(rules) else None
        self.editor.setEnabled(rule is not None)
        kind = rule["kind"] if rule else "mirror"
        direction = {"mirror": "normal", "rotate": "axis", "translate": "vector"}.get(kind)
        boxes = self.point + self.direction + [self.step, self.count]
        for box in boxes:
            box.blockSignals(True)
        if rule is not None:
            for box, value in zip(self.point, rule.get("point", [0, 0, 0])):
                box.setValue(value)
            for box, value in zip(self.direction, rule.get(direction, [0, 0, 0]) if direction else [0, 0, 0]):
                box.setValue(value)
            self.step.setValue(rule.get("step", 0))
            self.count.setValue(int(rule.get("count", 2)))
        for box in boxes:
            box.blockSignals(False)
        self.direction_label.setText((direction or "normal").capitalize())
        for widgets, shown in (
            ([self.point_label, *self.point], kind in ("mirror", "rotate")),
            ([self.direction_label, *self.direction], direction is not None),
            ([self.step_label, self.step], kind == "rotate"),
            ([self.count_label, self.count], kind != "mirror"),
        ):
            for w in widgets:
                w.setVisible(shown)

    def rules_ok(self):
        try:
            return not symmetry.rule_problems(objects.rules_of(self.obj), self.plane())
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return False

    def show_state(self):
        """The number of copies and parts, what Validate will say about the group, and whether the selected row has
        a table to fill."""
        prefix = f"Symmetric Group {self.obj.Label}: "
        texts = [p.text.removeprefix(prefix) for p in validation.group_problems(self.obj)]
        self.problem.setText("\n".join(texts))
        self.problem.setVisible(bool(texts))
        if self.rules_ok():
            n = symmetry.copy_count(objects.rules_of(self.obj))
            parts = len(objects.study_parts(self.study, [self.obj]))
            self.summary.setText(f"{n} {'copy' if n == 1 else 'copies'}, {parts} {'part' if parts == 1 else 'parts'}")
        else:
            self.summary.setText("No drawing until the rules are fixed.")
        r, rows = self.rows.currentRow(), objects.rows_of(self.obj)
        self.table_button.setEnabled(0 <= r < len(rows) and rows[r].get("mode") == "table")

    # ---- writing

    def apply(self, rule=None):
        """Recompute the drawing and show it; rule: as for refresh."""
        self.doc.recompute()
        self.refresh(rule)

    def write_side(self, side):
        self.obj.Side = side
        self.apply()

    def write_cells(self, cells):
        self.obj.Cells = list(cells)
        objects.sync_rows(self.obj)
        self.apply()

    def write_mode(self, r, mode):
        rows = objects.rows_of(self.obj)
        rows[r]["mode"] = mode
        objects.set_rows(self.obj, rows)
        self.show_ticks(r, mode)
        self.rows.setCurrentCell(r, 0)
        self.doc.recompute()
        self.show_state()

    def write_tick(self, item):
        if item.column() < 2:
            return
        rows, rule = objects.rows_of(self.obj), item.column() - 2
        across = set(rows[item.row()].get("across", [])) - {rule}
        if item.checkState() == QtCore.Qt.Checked:
            across.add(rule)
        rows[item.row()]["across"] = sorted(across)
        objects.set_rows(self.obj, rows)
        self.doc.recompute()
        self.show_state()

    def renumber(self, moved):
        """Keep the ticks on their rules: moved maps an old rule index to its new one, a removed rule to None."""
        rows = objects.rows_of(self.obj)
        for row in rows:
            row["across"] = sorted(moved[i] for i in row.get("across", []) if moved.get(i) is not None)
        objects.set_rows(self.obj, rows)

    def default_rule(self, kind):
        """A new rule the Study's plane allows: in a ZX Study mirrors and translations are along Z."""
        along_z = self.plane() == "ZX"
        if kind == "mirror":
            return {"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 1] if along_z else [0, 1, 0]}
        if kind == "rotate":
            return {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 90.0, "count": 4}
        return {"kind": "translate", "vector": [0, 0, 10] if along_z else [10, 0, 0], "count": 2}

    def add_rule(self, kind):
        rules = objects.rules_of(self.obj) + [self.default_rule(kind)]
        objects.set_rules(self.obj, rules)
        self.apply(len(rules) - 1)

    def drop_rule(self):
        rules, i = objects.rules_of(self.obj), self.rules.currentRow()
        if not 0 <= i < len(rules):
            return warn("Select a rule first.")
        del rules[i]
        self.renumber({k: (k if k < i else k - 1) for k in range(len(rules) + 1) if k != i})
        objects.set_rules(self.obj, rules)
        self.apply(max(0, min(i, len(rules) - 1)))

    def move_rule(self, step):
        rules, i = objects.rules_of(self.obj), self.rules.currentRow()
        j = i + step
        if not (0 <= i < len(rules) and 0 <= j < len(rules)):
            return
        rules[i], rules[j] = rules[j], rules[i]
        self.renumber({k: k for k in range(len(rules))} | {i: j, j: i})
        objects.set_rules(self.obj, rules)
        self.apply(j)

    def write_rule(self):
        rules, i = objects.rules_of(self.obj), self.rules.currentRow()
        if not 0 <= i < len(rules):
            return
        rule = rules[i]
        point, direction = [b.value() for b in self.point], [b.value() for b in self.direction]
        if rule["kind"] == "mirror":
            rule.update(point=point, normal=direction)
        elif rule["kind"] == "rotate":
            rule.update(point=point, axis=direction, step=self.step.value(), count=self.count.value())
        elif rule["kind"] == "translate":
            rule.update(vector=direction, count=self.count.value())
        else:
            rule["count"] = self.count.value()
        objects.set_rules(self.obj, rules)
        self.apply(i)

    def take_selection(self):
        picked = [b for b in selected_bodies() if not objects.is_study_object(b)]
        if not picked:
            return warn("Select the cell objects in the tree or the 3D view first.")
        self.write_cells(picked)

    def read_chain(self):
        """Cell objects and rules from a Mirror / Polar Array drawing; a drawing whose bodies have other copies gives
        a choice, and the rest is left for another group."""
        picked = Gui.Selection.getSelection()
        if len(picked) != 1:
            return warn("Select the top object of a Mirror / Polar Array drawing (its Fragments, Compound or Array).")
        try:
            proposals = symmetry.rules_from_chain(picked[0])
        except symmetry.SymmetryError as exc:
            return warn(str(exc))
        choice = 0 if len(proposals) == 1 else ask_proposal(proposals)
        if choice is None:
            return
        taken = proposals[choice]
        self.obj.Cells = taken.cells
        objects.sync_rows(self.obj)
        self.renumber({})  # the rules are new: no tick stands
        objects.set_rules(self.obj, taken.rules)
        self.apply(0)
        left = [b.Label for p in proposals if p is not taken for b in p.cells]
        if left:
            warn(
                f"These bodies are copied differently and were left out: {', '.join(left)}. Read them into a group of their own."
            )

    def open_table(self):
        r, rows = self.rows.currentRow(), objects.rows_of(self.obj)
        if not (0 <= r < len(rows) and rows[r].get("mode") == "table"):
            return warn("Select a row whose parts are named by a Table.")
        if not self.rules_ok():
            return warn("Fix the rules first: the table has a line per copy.")
        if TableDialog(self.obj, r).exec() == QtWidgets.QDialog.Accepted:
            self.apply()

    # ---- closing

    def accept(self):
        if not self.obj.Cells:
            warn("Select the cell objects and click Use selection.")
            return False
        name = self.name.text().strip()
        if name:
            self.obj.Label = name
        removed = objects.sync_parts(self.study) if self.rules_ok() else []  # parts follow once the rules can be read
        for cell in self.obj.Cells:  # the drawing shows them
            cell.Visibility = False
        self.doc.commitTransaction()
        self.doc.recompute()
        Gui.Control.closeDialog()
        if removed:
            warn("The parts of these Materials are gone, so the Materials were removed: " + ", ".join(removed) + ".")
        return True

    def reject(self):
        self.doc.abortTransaction()  # removes a new group, undoes the edits of an old one
        self.doc.recompute()
        Gui.Control.closeDialog()
        return True


def ask_winding(dialog):
    """Show the winding dialog; True on OK."""
    return dialog.exec() == QtWidgets.QDialog.Accepted


class WindingDialog(QtWidgets.QDialog):
    """The inputs of a three-phase winding: slots, pole pairs, coil span, which layer the row is, and whether each
    coil is a part of its own (else one part per phase and direction)."""

    LAYERS = [("top", "Top layer"), ("bottom", "Bottom layer"), ("whole", "Whole coil")]

    def __init__(self, slots, parent=None):
        super().__init__(parent or Gui.getMainWindow())
        self.setWindowTitle("Generate winding")
        layout = QtWidgets.QFormLayout(self)
        self.slots = QtWidgets.QSpinBox()
        self.slots.setRange(1, 100000)
        self.slots.setValue(slots)
        layout.addRow("Slots", self.slots)
        self.pole_pairs = QtWidgets.QSpinBox()
        self.pole_pairs.setRange(1, 10000)
        layout.addRow("Pole pairs", self.pole_pairs)
        self.span = QtWidgets.QSpinBox()
        self.span.setRange(1, 100000)
        self.span.setToolTip("Slots from the top side of a coil to its bottom side; 1 for a concentrated winding")
        layout.addRow("Coil span", self.span)
        self.layer = QtWidgets.QComboBox()
        for key, text in self.LAYERS:
            self.layer.addItem(text, key)
        layout.addRow("This object is the", self.layer)
        self.per_coil = QtWidgets.QCheckBox("One part per coil (else one per phase and direction: A+, A-, ...)")
        layout.addRow(self.per_coil)
        self.pole_pairs.valueChanged.connect(lambda _value: self.full_pitch())
        self.slots.valueChanged.connect(lambda _value: self.full_pitch())
        self.full_pitch()
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def full_pitch(self):
        self.span.setValue(max(1, self.slots.value() // (2 * self.pole_pairs.value())))

    def values(self):
        return {
            "slots": self.slots.value(),
            "pole_pairs": self.pole_pairs.value(),
            "span": self.span.value(),
            "per_coil": self.per_coil.isChecked(),
            "layer": self.layer.currentData(),
        }


class TableDialog(QtWidgets.QDialog):
    """The part name of every copy of one row of a Symmetric Group, a line per copy; copies with the same name are one
    part, across the group's objects too. generate fills it with a three-phase winding. OK writes it to the row."""

    def __init__(self, item, row, parent=None):
        super().__init__(parent or Gui.getMainWindow())
        self.item, self.row = item, row
        self.rules = objects.rules_of(item)
        data = objects.rows_of(item)[row]
        n = symmetry.copy_count(self.rules)
        names = [str(s) for s in data.get("table", [])][:n]
        names += [""] * (n - len(names))
        self.setWindowTitle("Parts of " + objects.row_label(item, data))
        layout = QtWidgets.QVBoxLayout(self)
        note = QtWidgets.QLabel(
            "A part name for each copy. Copies with the same name are one part, also across the group's objects."
            " The copy numbers in brackets count each rule's steps, the first rule fastest."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        self.table = QtWidgets.QTableWidget(n, 2)
        self.table.setHorizontalHeaderLabels(["Copy", "Part"])
        self.table.verticalHeader().setVisible(False)
        for k, index in enumerate(symmetry.copies(self.rules)):
            copy = QtWidgets.QTableWidgetItem(f"{k + 1}  ({', '.join(str(i) for i in index)})")
            copy.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(k, 0, copy)
            self.table.setItem(k, 1, QtWidgets.QTableWidgetItem(names[k]))
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.generate = QtWidgets.QPushButton("Generate winding…")
        self.generate.clicked.connect(self.generate_winding)
        if self.rotation() is None:
            self.generate.setEnabled(False)
            self.generate.setToolTip("A winding needs a rotation rule: the slots are found about its axis.")
        layout.addWidget(self.generate, 0, QtCore.Qt.AlignLeft)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def rotation(self):
        """The first rotation rule: the winding's slots are about its axis."""
        return next((r for r in self.rules if r["kind"] == "rotate"), None)

    def names(self):
        return [self.table.item(k, 1).text().strip() for k in range(self.table.rowCount())]

    def generate_winding(self):
        rule = self.rotation()
        dialog = WindingDialog(int(rule["count"]), self)
        if ask_winding(dialog):
            names = objects.winding_table(self.item, self.row, rule, **dialog.values())
            for k, name in enumerate(names):
                self.table.item(k, 1).setText(name)

    def accept(self):
        rows = objects.rows_of(self.item)
        rows[self.row]["table"] = self.names()
        objects.set_rows(self.item, rows)
        super().accept()


def field_value(box):
    """The number a formula_box shows."""
    return box.property("rawValue" if box.metaObject().className() == "Gui::QuantitySpinBox" else "value")


def set_field_value(box, value):
    """Show (and, like typing it, write) a number in a formula_box."""
    box.setProperty("rawValue" if box.metaObject().className() == "Gui::QuantitySpinBox" else "value", value)


def show_field_value(box, value):
    """Show a number in a formula_box without writing it: the property already holds it."""
    box.blockSignals(True)
    set_field_value(box, value)
    box.blockSignals(False)


def property_number(obj, prop):
    """The number in obj.prop: mm or degrees for a quantity. prop may name one component of a vector, "Center.x"."""
    name, _, part = prop.partition(".")
    value = getattr(obj, name)
    value = getattr(value, part) if part else value
    return float(getattr(value, "Value", value))


def formula_box(obj, prop, minimum=None, maximum=None):
    """A number field bound to obj.prop, in FreeCAD's own style: it shows the unit, takes a formula through its f(x)
    button, writes each edit to the property and recomputes. A formula is stored on the property and the field
    follows it. Length, Distance and Angle give a Gui::QuantitySpinBox; Float a Gui::DoubleSpinBox; Integer and
    IntegerConstraint a Gui::IntSpinBox (no decimals). prop may be one component of a Vector property ("Center.x":
    a length). minimum and maximum are in mm, degrees or plain numbers."""
    name, _, part = prop.partition(".")
    kind = obj.getTypeIdOfProperty(name)
    whole = kind in ("App::PropertyInteger", "App::PropertyIntegerConstraint")
    quantity = kind in ("App::PropertyLength", "App::PropertyDistance", "App::PropertyAngle") or bool(part)
    widget = "Gui::IntSpinBox" if whole else "Gui::QuantitySpinBox" if quantity else "Gui::DoubleSpinBox"
    box = Gui.UiLoader().createWidget(widget)
    binding = Gui.ExpressionBinding(box)
    binding.bind(obj, prop)
    binding.setAutoApply(True)  # a formula typed in the f(x) dialog goes onto the property
    if quantity:
        box.setProperty("unit", "deg" if kind == "App::PropertyAngle" else "mm")
    cast = int if whole else float
    box.setProperty("minimum", cast(-1e9 if minimum is None else minimum))
    box.setProperty("maximum", cast(1e9 if maximum is None else maximum))
    show_field_value(box, cast(property_number(obj, prop)))  # showing the stored value is not an edit

    def edited(number):
        doc = obj.Document
        if binding.hasExpression():  # the property takes the formula's value when the document recomputes
            QtCore.QTimer.singleShot(0, lambda: doc.recompute())
            return
        if part:
            vector = App.Vector(getattr(obj, name))
            setattr(vector, part, number)
            setattr(obj, name, vector)
        else:
            setattr(obj, name, cast(number))
        doc.recompute()

    box.connect(QtCore.SIGNAL("valueChanged(int)" if whole else "valueChanged(double)"), edited)
    return box


class AirRegionPanel:
    """Edit an Air Region: its outer shape and its size, typed in or padded around the Study's bodies. Every field
    writes its property as it changes, inside one transaction: OK commits it, Cancel undoes it. The fields take
    formulas (see formula_box). new: obj was just made inside the command's open transaction, so Cancel removes it."""

    # plane -> [(AirShape, name shown)]; a 2D box is a rectangle and a ZX sector is a half disc
    SHAPES = {
        "3D": [("Box", "Box"), ("Sector", "Sector"), ("Custom", "Custom")],
        "XY": [("Box", "Rectangle"), ("Sector", "Sector"), ("Custom", "Custom")],
        "ZX": [("Box", "Rectangle"), ("Sector", "Half disc")],
    }
    CENTER_AXES = {"3D": "xyz", "XY": "xy", "ZX": "xz"}

    def __init__(self, obj, new=False):
        self.obj, self.new, self.done = obj, new, False
        self.study = objects.owner_study(obj)
        self.plane = airshapes.study_plane(self.study)
        self.source = obj.Source
        if not new:  # a new item's transaction is already open
            obj.Document.openTransaction("Edit " + obj.Label)
        highlight.clear()
        self.bound = []  # (field, property) of every formula field, to show the properties again
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QVBoxLayout(self.form)
        top = QtWidgets.QFormLayout()
        layout.addLayout(top)
        top.addRow(QtWidgets.QLabel("Study: " + self.study.Label))
        self.name = QtWidgets.QLineEdit(objects.display_name(obj))
        top.addRow("Name", self.name)
        self.shape = QtWidgets.QComboBox()
        for key, text in self.SHAPES[self.plane]:
            self.shape.addItem(text, key)
        self.shape.setCurrentIndex(max(self.shape.findData(obj.AirShape), 0))
        top.addRow("Shape", self.shape)
        self.mode_box = QtWidgets.QWidget()  # hidden for a Custom shape: it has no Padding
        modes = QtWidgets.QHBoxLayout(self.mode_box)
        modes.setContentsMargins(0, 0, 0, 0)
        self.mode_manual, self.mode_padding = QtWidgets.QRadioButton("Manual"), QtWidgets.QRadioButton("Padding")
        self.mode_padding.setToolTip("Size the air from the Study's bodies: a percentage and a length beyond each side")
        for widget in (QtWidgets.QLabel("Size"), self.mode_manual, self.mode_padding):
            modes.addWidget(widget)
        modes.addStretch()
        layout.addWidget(self.mode_box)
        self.groups = {"Box": self.box_group(), "Sector": self.sector_group(), "Custom": self.custom_group()}
        self.pad, self.ring = {}, None  # shape -> {side key: (percent field, length field)}; the Sector ring switch
        self.tables = {"Box": self.padding_table("Box"), "Sector": self.padding_table("Sector")}
        for widget in list(self.groups.values()) + list(self.tables.values()):
            layout.addWidget(widget)
        self.symmetric = QtWidgets.QCheckBox("Symmetric")
        self.symmetric.setToolTip("Each - side takes the value (or formula) of its + side")
        self.symmetric.setChecked(self.is_symmetric())
        self.result = QtWidgets.QLabel()
        self.convert = QtWidgets.QPushButton("Convert to Manual")
        self.convert.setToolTip("Keep the sizes as they are now and stop following the bodies")
        self.foot = QtWidgets.QWidget()
        foot = QtWidgets.QVBoxLayout(self.foot)
        foot.setContentsMargins(0, 0, 0, 0)
        foot.addWidget(self.symmetric)
        foot.addWidget(self.result)
        foot.addWidget(self.convert, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(self.foot)
        self.shape.currentIndexChanged.connect(self.write_shape)
        self.mode_padding.toggled.connect(lambda padding: self.set_mode("Padding" if padding else "Manual"))
        self.symmetric.toggled.connect(self.write_symmetric)
        self.convert.clicked.connect(lambda: self.set_mode("Manual"))
        self.show_layout()
        self.show_values()

    def field(self, prop, minimum=None, maximum=None):
        """A formula field on obj.prop; its edits update the panel."""
        box = formula_box(self.obj, prop, minimum, maximum)
        box.connect(QtCore.SIGNAL("valueChanged(double)"), self.changed)
        self.bound.append((box, prop))
        return box

    def box_group(self):
        plane = self.plane
        group = QtWidgets.QGroupBox("Box" if plane == "3D" else "Rectangle")
        form = QtWidgets.QFormLayout(group)
        self.center = {}
        for axis in self.CENTER_AXES[plane]:
            self.center[axis] = self.field(f"Center.{axis}", -1e6, 1e6)
            form.addRow(f"Centre {axis}", self.center[axis])
        labels = {
            "Length": "Length (x)",
            "Width": "Width (z)" if plane == "ZX" else "Width (y)",
            "Height": "Height (z)",
        }
        self.size = {}
        for prop in ("Length", "Width") + (("Height",) if plane == "3D" else ()):
            self.size[prop] = self.field(prop, 0.001, 1e6)
            form.addRow(labels[prop], self.size[prop])
        return group

    def sector_group(self):
        plane = self.plane
        group = QtWidgets.QGroupBox("Half disc" if plane == "ZX" else "Sector")
        self.sector_form = form = QtWidgets.QFormLayout(group)
        self.inner, self.outer = self.field("InnerRadius", 0, 1e6), self.field("OuterRadius", 0.001, 1e6)
        form.addRow("Inner radius", self.inner)
        form.addRow("Outer radius", self.outer)
        self.sector_sized = [self.inner, self.outer]  # the rows Padding computes
        self.angles = self.z_min = self.sector_height = self.sector_z = None
        if plane == "ZX":
            self.sector_z = self.field("Center.z", -1e6, 1e6)
            form.addRow("Centre z", self.sector_z)
        else:
            self.angles = (self.field("StartAngle", -360, 720), self.field("EndAngle", -360, 720))
            form.addRow("Start angle", self.angles[0])
            form.addRow("End angle", self.angles[1])
        if plane == "3D":
            self.z_min, self.sector_height = self.field("ZMin", -1e6, 1e6), self.field("Height", 0.001, 1e6)
            form.addRow("Z min", self.z_min)
            form.addRow("Height", self.sector_height)
            self.sector_sized += [self.z_min, self.sector_height]
        return group

    def custom_group(self):
        group = QtWidgets.QGroupBox("Custom")
        form = QtWidgets.QFormLayout(group)
        self.source_label = QtWidgets.QLabel()
        self.source_label.setWordWrap(True)
        form.addRow("Body", self.source_label)
        pick = QtWidgets.QPushButton("Use selected body")
        pick.setToolTip("The air takes the shape of the body selected in the 3D view or the tree")
        pick.clicked.connect(self.pick_source)
        form.addRow(pick)
        self.show_source()
        return group

    def padding_table(self, shape):
        """The % and mm fields of each side Padding offers for shape; the padding is their sum."""
        group = QtWidgets.QGroupBox("Padding")
        grid = QtWidgets.QGridLayout(group)
        grid.addWidget(QtWidgets.QLabel("%"), 0, 1)
        grid.addWidget(QtWidgets.QLabel("mm"), 0, 2)
        self.pad[shape] = {}
        for row, (key, label) in enumerate(airshapes.padding_sides(shape, self.plane), 1):
            percent, length = self.field(f"Pad{key}Percent", 0, 1e6), self.field(f"Pad{key}", 0, 1e6)
            self.pad[shape][key] = (percent, length)
            grid.addWidget(QtWidgets.QLabel(label), row, 0)
            grid.addWidget(percent, row, 1)
            grid.addWidget(length, row, 2)
        if shape == "Sector" and self.plane != "ZX":
            self.ring = QtWidgets.QCheckBox("Inner radius from the bodies (a ring)")
            self.ring.setToolTip("Unchecked: a full disc, inner radius 0")
            self.ring.setChecked(self.obj.InnerFromBodies)
            self.ring.toggled.connect(self.write_ring)
            grid.addWidget(self.ring, len(self.pad[shape]) + 1, 0, 1, 3)
        return group

    def pairs(self, shapes):
        """[(+ property, - property)] that Symmetric ties for the sides of the shapes: the % and the mm of each axis."""
        found = []
        for shape in shapes:
            keys = [key for key, _ in airshapes.padding_sides(shape, self.plane)]
            for key in keys:
                if key.endswith("Plus") and key[:-4] + "Minus" in keys:
                    for suffix in ("Percent", ""):
                        found.append((f"Pad{key}{suffix}", f"Pad{key[:-4]}Minus{suffix}"))
        return list(dict.fromkeys(found))

    def is_symmetric(self):
        """True if every - side holds what its + side holds, a value or the same formula."""
        formulas, obj = dict(self.obj.ExpressionEngine), self.obj
        return all(
            formulas.get(plus) == formulas.get(minus) and property_number(obj, plus) == property_number(obj, minus)
            for plus, minus in self.pairs(("Box", "Sector"))
        )

    def mirror(self):
        """Copy the value or formula of each + side of the current shape to its - side."""
        obj, formulas = self.obj, dict(self.obj.ExpressionEngine)
        for plus, minus in self.pairs((self.shape.currentData(),)):
            if formulas.get(plus):
                if formulas.get(minus) != formulas[plus]:
                    obj.setExpression(minus, formulas[plus])
            else:
                if formulas.get(minus):
                    obj.setExpression(minus, None)
                if property_number(obj, plus) != property_number(obj, minus):
                    setattr(obj, minus, getattr(obj, plus))

    def write_symmetric(self, checked):
        if checked:
            self.mirror()
            self.settle()
        self.show_layout()

    def changed(self, _value=None):
        """A field was edited, by hand or by a formula: keep the - sides equal while Symmetric. The recompute of a
        formula waits for the event loop, so the panel updates after it."""
        if self.symmetric.isChecked():
            self.mirror()
        QtCore.QTimer.singleShot(0, self.settle)

    def settle(self):
        if not self.done:
            if self.symmetric.isChecked():  # a formula that kept its value sent no change
                self.mirror()
            self.obj.Document.recompute()
            self.show_values()

    def show_values(self):
        """Show the properties in the fields and the result line: the recompute may have written them."""
        for box, prop in self.bound:
            number = property_number(self.obj, prop)
            if abs(field_value(box) - number) > 1e-9:
                show_field_value(box, number)
        self.result.setText(self.result_text())

    def result_text(self):
        obj = self.obj
        if "Invalid" in obj.State:
            return "Result: " + obj.getStatusString()
        if obj.AirShape == "Sector":
            text = f"radii {obj.InnerRadius.Value:g} to {obj.OuterRadius.Value:g} mm"
            if self.plane == "3D":
                text += f" · z {obj.ZMin.Value:g} to {obj.ZMin.Value + obj.Height.Value:g} mm"
            return "Result: " + text
        centre = ", ".join(f"{getattr(obj.Center, axis):g}" for axis in self.CENTER_AXES[self.plane])
        sizes = [obj.Length.Value, obj.Width.Value] + ([obj.Height.Value] if self.plane == "3D" else [])
        return f"Result: centre ({centre}) · " + " × ".join(f"{v:g}" for v in sizes) + " mm"

    def show_layout(self):
        """Show what the shape and the size mode need."""
        shape, padding = self.shape.currentData(), self.obj.SizeMode == "Padding"
        for radio, on in ((self.mode_manual, not padding), (self.mode_padding, padding)):
            radio.blockSignals(True)
            radio.setChecked(on)
            radio.blockSignals(False)
        self.mode_box.setVisible(shape != "Custom")
        self.groups["Box"].setVisible(shape == "Box" and not padding)
        self.groups["Sector"].setVisible(shape == "Sector")
        self.groups["Custom"].setVisible(shape == "Custom")
        for box in self.sector_sized:  # Padding computes these; the angles and the centre z stay manual
            box.setVisible(not padding)
            self.sector_form.labelForField(box).setVisible(not padding)
        for key, table in self.tables.items():
            table.setVisible(key == shape and padding)
        self.foot.setVisible(padding and shape != "Custom")
        self.symmetric.setVisible(bool(self.pairs((shape,))))
        minus = {pair[1] for pair in self.pairs(("Box", "Sector"))}
        for box, prop in self.bound:
            if prop in minus:
                box.setEnabled(not self.symmetric.isChecked())
        if self.ring is not None:  # no inner padding for a full disc
            for box in self.pad["Sector"]["Inner"]:
                box.setEnabled(self.ring.isChecked())

    def set_mode(self, mode):
        self.obj.SizeMode = mode
        self.obj.Document.recompute()
        self.show_layout()
        self.show_values()

    def write_ring(self, checked):
        self.obj.InnerFromBodies = checked
        self.show_layout()
        self.settle()

    def write_shape(self):
        obj, shape = self.obj, self.shape.currentData()
        if shape == "Custom":
            if self.source is not None:  # applied only with a body: until then the air keeps its shape and mode
                obj.SizeMode = "Manual"  # a Custom shape has no Padding
                obj.Source = self.source
                obj.AirShape = "Custom"
        else:
            if obj.SizeMode == "Padding":  # sides new to the shape start padded, as a new Air Region does
                airshapes.seed_padding(obj, obj.AirShape, shape, self.plane)
            obj.AirShape = shape
            if self.symmetric.isChecked():
                self.mirror()
        obj.Document.recompute()
        self.show_layout()
        self.show_values()

    def show_source(self):
        self.source_label.setText(self.source.Label if self.source is not None else "none picked yet")

    def pick_source(self):
        picked = [b for b in selected_bodies() if b != self.obj]
        if not picked:
            return warn("Select a body in the 3D view or the tree first.")
        self.source = picked[0]
        self.show_source()
        if self.shape.currentData() == "Custom":
            self.write_shape()

    def accept(self):
        obj, doc = self.obj, self.obj.Document
        if self.shape.currentData() == "Custom" and obj.AirShape != "Custom":
            warn("Select a body and click Use selected body.")
            return False
        name = self.name.text().strip()
        if name:
            objects.rename_air_region(objects.owner_study(obj), obj, name)
        if self.symmetric.isChecked():  # a formula that kept its value sent no change
            self.mirror()
        self.done = True
        doc.commitTransaction()
        doc.recompute()
        Gui.Control.closeDialog()
        return True

    def reject(self):
        doc = self.obj.Document
        self.done = True
        doc.abortTransaction()  # removes a new Air Region, undoes the edits of an old one
        doc.recompute()
        Gui.Control.closeDialog()
        return True


class SlidingInterfacePanel:
    """Edit a Sliding Interface: its kind, where its surface lies and how many divisions the motion has.
    Changes apply as they are made, inside one transaction: OK commits it, Cancel undoes it. new: obj was just made
    inside an open transaction, so Cancel removes it."""

    def __init__(self, obj, new=False):
        self.obj, self.new = obj, new
        self.study = objects.owner_study(obj)
        self.three_d = self.study.Dimension == "3D"
        if not new:  # a new item's transaction is already open
            obj.Document.openTransaction("Edit " + obj.Label)
        highlight.clear()
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QVBoxLayout(self.form)
        self.fields = QtWidgets.QFormLayout()
        self.rows = []  # (kinds, label, widget) of the rows only some kinds show
        layout.addLayout(self.fields)
        self.fields.addRow(QtWidgets.QLabel("Study: " + self.study.Label))
        self.name = QtWidgets.QLineEdit(objects.display_name(obj))
        self.fields.addRow("Name", self.name)
        self.kind = QtWidgets.QComboBox()
        for kind in ("Rotational", "Axial gap", "Linear"):
            if self.three_d or kind != "Axial gap":
                self.kind.addItem(kind, kind)
        self.kind.setCurrentIndex(max(self.kind.findData(obj.Kind), 0))
        self.fields.addRow("Kind", self.kind)
        axes = objects.AXES if self.three_d else objects.AXES[:2]  # a 2D motion lies in the XY plane
        self.radius = formula_box(obj, "Radius", 0.001, 1e6)
        self.add_field("Radius", self.radius, "Rotational")
        self.position = formula_box(obj, "Position", -1e6, 1e6)
        self.position_text = self.add_field("Position", self.position, "Axial gap", "Linear")
        self.normal = QtWidgets.QComboBox()
        self.normal.addItems(axes)
        self.normal.setCurrentText(obj.NormalAxis if obj.NormalAxis in axes else axes[-1])
        self.add_field("Normal axis", self.normal, "Linear")
        self.motion = QtWidgets.QComboBox()
        self.motion.addItems(axes)
        self.motion.setCurrentText(obj.MotionAxis if obj.MotionAxis in axes else axes[0])
        self.add_field("Motion axis", self.motion, "Linear")
        self.divisions = formula_box(obj, "Divisions", 2, 100000)
        self.fields.addRow("Divisions", self.divisions)
        self.cross = None  # 3D only
        if self.three_d:
            self.cross = formula_box(obj, "CrossDivisions", 1, 100000)
            self.fields.addRow("Cross divisions", self.cross)
        self.step_label = QtWidgets.QLabel()
        self.fields.addRow("Step", self.step_label)
        self.kind.currentIndexChanged.connect(self.write_kind)
        self.normal.currentIndexChanged.connect(self.write_axes)
        self.motion.currentIndexChanged.connect(self.write_axes)
        self.kind.currentIndexChanged.connect(self.show_kind)
        self.divisions.connect(QtCore.SIGNAL("valueChanged(int)"), self.show_step)
        self.motion.currentIndexChanged.connect(self.show_step)
        self.show_kind()

    def write_kind(self):
        self.obj.Kind = self.kind.currentData()
        self.obj.Document.recompute()

    def write_axes(self):
        """The axes of a Linear interface; equal axes are not written (OK refuses them)."""
        if self.normal.currentText() != self.motion.currentText():
            self.obj.NormalAxis, self.obj.MotionAxis = self.normal.currentText(), self.motion.currentText()
            self.obj.Document.recompute()

    def add_field(self, label, widget, *kinds):
        """A row shown only for the kinds; returns its label (the widget is the caller's)."""
        text = QtWidgets.QLabel(label)
        self.fields.addRow(text, widget)
        self.rows.append((kinds, text, widget))
        return text

    def show_kind(self):
        kind = self.kind.currentData()
        for kinds, text, widget in self.rows:
            text.setVisible(kind in kinds)
            widget.setVisible(kind in kinds)
        self.position_text.setText("Z position" if kind == "Axial gap" else "Position")
        self.show_step()

    def show_step(self):
        """The motion of one division: an angle about Z, or a length along the motion axis of a Linear interface."""
        n, air = field_value(self.divisions), objects.air_of(self.obj)
        if self.kind.currentData() == "Linear":
            if air is None or air.AirShape != "Box":
                return self.step_label.setText("")
            length = (air.Length, air.Width, air.Height)[objects.AXES.index(self.motion.currentText())].Value
            return self.step_label.setText(f"{length / n:g} mm per division")
        span = 360.0
        if air is not None and air.AirShape == "Sector":
            span = min(air.EndAngle.Value - air.StartAngle.Value, 360.0)
        self.step_label.setText(f"{span / n:g} deg per division")

    def accept(self):
        obj, doc = self.obj, self.obj.Document
        if self.kind.currentData() == "Linear" and self.normal.currentText() == self.motion.currentText():
            warn("The motion axis must differ from the normal axis.")
            return False
        name = self.name.text().strip()
        if name:
            obj.Label = name
            obj.GroupName = name  # FreeCAD may have suffixed the Label
        doc.commitTransaction()
        doc.recompute()
        Gui.Control.closeDialog()
        return True

    def reject(self):
        doc = self.obj.Document
        doc.abortTransaction()  # removes a new Sliding Interface, undoes the edits of an old one
        doc.recompute()
        Gui.Control.closeDialog()
        return True


class IdTableDialog(QtWidgets.QDialog):
    """Lists every group with its ID. The ID column is editable; duplicates are refused."""

    def __init__(self, study):
        super().__init__(Gui.getMainWindow())
        self.study = study
        self.setWindowTitle("EMSolution IDs")
        objects.update_ids(study)  # so bodies added since the last run show up
        self.rows = objects.id_rows(study)
        self.table = QtWidgets.QTableWidget(len(self.rows), 3)
        self.table.setHorizontalHeaderLabels(["Type", "Name", "ID"])
        for r, (table, _key, name, id_) in enumerate(self.rows):
            kind = "MAT_ID" if table == "MatIds" else "SMAT_ID"
            for c, text in enumerate((kind, name, str(id_))):
                item = QtWidgets.QTableWidgetItem(text)
                if c < 2:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
        self.table.itemChanged.connect(self.changed)
        close = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        close.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(close)

    def changed(self, item):
        table, key, name, old = self.rows[item.row()]
        try:
            new = int(item.text())
            objects.set_id(self.study, table, key, new)
        except ValueError as exc:
            QtWidgets.QMessageBox.warning(self, "EMSolution IDs", str(exc))
            self.table.blockSignals(True)
            item.setText(str(old))
            self.table.blockSignals(False)
            return
        self.rows[item.row()] = (table, key, name, new)


class ValidationPanel:
    """Every problem of a Study at once, then the mesher's geometry checks (without meshing).
    Selecting a row selects the item it is about and highlights its bodies, faces, edges and vertices."""

    ICONS = {
        validation.ERROR: QtWidgets.QStyle.SP_MessageBoxCritical,
        validation.WARNING: QtWidgets.QStyle.SP_MessageBoxWarning,
        "info": QtWidgets.QStyle.SP_MessageBoxInformation,
        "ok": QtWidgets.QStyle.SP_DialogApplyButton,
    }

    def __init__(self, study):
        self.study = study
        highlight.clear()
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Validate Study")
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.addWidget(QtWidgets.QLabel(f"Study: {study.Label} ({study.Dimension})"))
        self.list = QtWidgets.QListWidget()
        self.list.setWordWrap(True)
        self.list.itemSelectionChanged.connect(self.show_row)
        layout.addWidget(self.list)
        self.again = QtWidgets.QPushButton("Check again")
        self.again.clicked.connect(self.run)
        layout.addWidget(self.again)
        self.rows, self.pending = [], None
        self.run()

    def getStandardButtons(self):
        return QtWidgets.QDialogButtonBox.Close

    def reject(self):
        highlight.clear()
        Gui.Control.closeDialog()
        return True

    def add(self, severity, text, item=None, refs=()):
        style = self.form.style()
        self.list.addItem(QtWidgets.QListWidgetItem(style.standardIcon(self.ICONS[severity]), text))
        self.rows.append((item, list(refs)))

    def run(self):
        from . import runner

        self.list.clear()
        self.rows = []
        highlight.clear()
        problems = validation.validate(self.study)
        for p in problems:
            self.add(p.severity, p.text, p.item, p.refs)
        if not problems:
            self.add("ok", "Study setup: no problems found.")
        if validation.errors(problems):
            self.add("info", "The mesher's geometry check runs once the errors above are fixed.")
            return
        if runner.busy():
            self.add("info", "A mesh run is going on: check again when it ends.")
            return
        self.again.setEnabled(False)
        self.pending = self.list.count()
        self.add("info", "Checking the geometry with the mesher…")
        runner.check(self.study, self.checked)

    def checked(self, error, notes):
        """runner.check() result: replaces the "Checking…" row."""
        if self.pending is not None:
            self.list.takeItem(self.pending)
            self.rows.pop(self.pending)
            self.pending = None
        if error is None:
            self.add("info", "Geometry check cancelled.")
        elif error:
            self.add(validation.ERROR, "Mesher: " + error)
        else:
            self.add("ok", "The mesher's geometry checks passed (no mesh was made).")
        for note in notes:
            self.add("info", "Mesher note: " + note)
        self.again.setEnabled(True)

    def show_row(self):
        rows = sorted(self.list.row(i) for i in self.list.selectedItems())
        if not rows:
            highlight.clear()
            return
        item, refs = self.rows[rows[0]]
        highlight.show(refs or (objects.item_refs(item) if item is not None and objects.is_item(item) else []))
        if item is not None and getattr(item, "Document", None) is not None:
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(item)
