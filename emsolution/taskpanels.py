"""View providers, the item edit panel, folder watchers, the ID table dialog and selection helpers."""
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import icon, objects


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


def selected_faces():
    return selected_subs(("Face",))


def selected_mesh_refs():
    return selected_subs(("Face", "Edge", "Vertex"), whole_bodies=True)


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
        IdTableDialog(vobj.Object).exec()
        return True


class ViewProviderFolder(_ViewProvider):
    """No getIcon: the standard folder icon. Its panel shows in the Tasks tab when the folder
    is selected (FolderWatcher). Double-click does nothing, so it does not start a rename."""

    def doubleClicked(self, vobj):
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
    """Edits the mesh settings stored on the Mesh Sizes folder. Each change applies at once."""

    def __init__(self, folder):
        self.folder = folder
        self.box = QtWidgets.QGroupBox("Mesh settings")
        form = QtWidgets.QFormLayout(self.box)
        self.default = _length_box(folder.DefaultMeshSize.Value)
        form.addRow("Default size", self.default)
        self.algorithms = {}
        for prop, label in (("SurfaceAlgorithm", "2D algorithm"),
                            ("VolumeAlgorithm", "3D algorithm")):
            combo = QtWidgets.QComboBox()
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
        out.update(DefaultMeshSize=self.default.value(), SizeFactor=self.factor.value(),
                   MinSize=self.min_size.value(), MaxSize=self.max_size.value(),
                   SmoothingSteps=self.smoothing.value(), OptimizeNetgen=self.netgen.isChecked())
        return out

    def save(self, *_):
        f = self.folder
        changed = {p: v for p, v in self.values().items()
                   if getattr(getattr(f, p), "Value", getattr(f, p)) != v}  # Value: a length
        if not changed:
            return
        f.Document.openTransaction("Edit mesh settings")
        for prop, value in changed.items():
            setattr(f, prop, value)
        f.Document.commitTransaction()
        f.Document.recompute()


class FolderView:
    """Overview of a folder's items. Double-click a row to edit that item.
    The Mesh Sizes folder also edits the mesh settings."""

    def __init__(self, folder):
        study = objects.find_study(folder.Document)
        headers, rows = {
            objects.MaterialsFolder: (["Material", "Body", "Volume ID"], objects.material_rows),
            objects.ExcitationsFolder: (["Excitation", "Body", "Faces", "Surface ID"],
                                        objects.excitation_rows),
            objects.MeshSizesFolder: (["Mesh size", "Size", "Applies to"], objects.mesh_size_rows),
        }[type(folder.Proxy)]
        self.rows = rows(study)
        self.form = QtWidgets.QWidget()  # the watcher's task box shows the folder name
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.setContentsMargins(0, 0, 0, 0)
        self.settings = None
        if isinstance(folder.Proxy, objects.MeshSizesFolder):
            self.settings = MeshSettings(folder)
            layout.addWidget(self.settings.box)
        self.table = QtWidgets.QTableWidget(len(self.rows), len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        for r, (_item, cells) in enumerate(self.rows):
            for c, text in enumerate(cells):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
        self.table.cellDoubleClicked.connect(self.open_item)
        layout.addWidget(self.table)
        self.missing = None
        if isinstance(folder.Proxy, objects.MaterialsFolder):
            bodies = objects.bodies_without_material(study)
            if bodies:
                self.missing = QtWidgets.QLabel(
                    "No material (Run Mesh will stop): " + ", ".join(b.Label for b in bodies))
                self.missing.setWordWrap(True)
                self.missing.setStyleSheet("color: #c00000")
                layout.addWidget(self.missing)

    def open_item(self, row, _column):
        Gui.Control.showDialog(ItemPanel(self.rows[row][0]))


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
    return [FolderWatcher(cls) for _prop, cls in objects.FOLDERS]


WORKBENCH = "EMSolutionWorkbench"


class WorkbenchSwitch:
    """Selecting a study object while another workbench is active switches to EMSolution,
    so its panel can show. Bodies and faces do not switch; nor does anything during an edit."""

    def addSelection(self, doc, obj, sub, pnt):
        QtCore.QTimer.singleShot(0, self.check)  # switching inside the selection event is unsafe

    def check(self):
        if Gui.activeWorkbench().name() == WORKBENCH or Gui.Control.activeDialog():
            return
        if any(objects.is_study_object(o) for o in Gui.Selection.getSelection()):
            Gui.activateWorkbench(WORKBENCH)


_switch = None


def install_workbench_switch():
    global _switch
    if _switch is None:
        _switch = WorkbenchSwitch()
        Gui.Selection.addObserver(_switch)


class ViewProviderItem(_ViewProvider):
    def getIcon(self):
        obj = getattr(self, "Object", None)
        return icon(type(obj.Proxy).__name__.lower()) if obj else icon("emsolution")

    def doubleClicked(self, vobj):
        Gui.Control.showDialog(ItemPanel(vobj.Object))
        return True


class ItemPanel:
    """Edit name, size (Mesh Size only) and references of a tree item."""

    def __init__(self, obj):
        self.obj = obj
        self.bodies_only = isinstance(obj.Proxy, objects.Material)
        if self.bodies_only:
            self.pick, label = (lambda: [(b, "") for b in selected_bodies()]), "Bodies"
            self.current = [(b, "") for b in obj.References]
        else:
            if isinstance(obj.Proxy, objects.Excitation):
                self.pick, label = selected_faces, "Faces"
            else:
                self.pick, label = selected_mesh_refs, "Bodies, faces,\nedges, vertices"
            self.current = [(b, s) for b, subs in obj.References for s in subs]
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QFormLayout(self.form)
        self.name = QtWidgets.QLineEdit(getattr(obj, "GroupName", "") or obj.Label)
        layout.addRow("Name", self.name)
        self.size = None
        if isinstance(obj.Proxy, objects.MeshSize):
            self.size = _length_box(obj.Size.Value)
            layout.addRow("Size", self.size)
        self.refs = QtWidgets.QListWidget()
        self.refs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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

    def refresh(self):
        self.refs.clear()
        self.refs.addItems([objects.ref_label(b, f) for b, f in self.current])

    def add_selection(self):
        new = self.pick()
        have = {(b.Name, f) for b, f in self.current}
        self.current += [(b, f) for b, f in new if (b.Name, f) not in have]
        self.refresh()

    def remove(self):
        rows = {i.row() for i in self.refs.selectedIndexes()}
        self.current = [r for i, r in enumerate(self.current) if i not in rows]
        self.refresh()

    def accept(self):
        doc = self.obj.Document
        doc.openTransaction("Edit " + self.obj.Label)
        name = self.name.text().strip()
        if name:
            self.obj.Label = name
            if hasattr(self.obj, "GroupName"):
                self.obj.GroupName = name  # FreeCAD may have suffixed the Label
        if self.size is not None:
            self.obj.Size = self.size.value()
        if self.bodies_only:
            self.obj.References = [b for b, _ in self.current]
        else:
            self.obj.References = list(self.current)
        doc.commitTransaction()
        doc.recompute()
        Gui.Control.closeDialog()
        return True

    def reject(self):
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
            kind = "Volume" if table == "VolumeIds" else "Surface"
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
