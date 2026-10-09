"""View providers, the item edit panel, folder watchers, the ID table dialog, the selection
observer and selection helpers."""

from collections import Counter

import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin
from PySide import QtCore, QtWidgets

from . import geometry, highlight, icon, jobwriter, objects

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
        if not Gui.Control.activeDialog():
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(vobj.Object)
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
        for prop, label in (("SurfaceAlgorithm", "Surface algorithm"), ("VolumeAlgorithm", "Volume algorithm")):
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


class FolderView:
    """Assignment overview, plus general settings for the Mesh Sizes folder."""

    def __init__(self, folder):
        study = objects.owner_study(folder)
        self.study = study
        headers, rows = {
            objects.MaterialsFolder: (["Material", "Body", "Volume ID"], objects.material_rows),
            objects.ExcitationsFolder: (["Excitation", "Body", "Faces", "Surface ID"], objects.excitation_rows),
            objects.MeshSizesFolder: (["Mesh size", "Size", "Applies to"], objects.mesh_size_rows),
        }[type(folder.Proxy)]
        self.rows = rows(study)
        self.form = QtWidgets.QWidget()  # the watcher's task box shows the folder name
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("Study: " + study.Label))
        if study.MainMode != "Materials":
            notice = QtWidgets.QLabel("Only assignments on the selected geometry are exported.")
            notice.setWordWrap(True)
            layout.addWidget(notice)
        if study.Dimension == "2D":
            notice = QtWidgets.QLabel(
                "2D material, excitation and local size assignments will be added with 2D meshing."
            )
            notice.setWordWrap(True)
            layout.addWidget(notice)
        self.settings = None
        if isinstance(folder.Proxy, objects.MeshSizesFolder):
            self.settings = MeshSettings(folder)
            layout.addWidget(self.settings.box)
            if study.Dimension == "2D":
                self.settings.box.setEnabled(False)
                self.settings.box.setToolTip("2D mesh settings will be enabled with 2D generation.")
        self.table = QtWidgets.QTableWidget(len(self.rows), len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        for r, (_item, _refs, cells) in enumerate(self.rows):
            for c, text in enumerate(cells):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
        self.table.itemSelectionChanged.connect(self.highlight_rows)
        self.table.cellDoubleClicked.connect(self.open_item)
        layout.addWidget(self.table)
        if isinstance(folder.Proxy, objects.MaterialsFolder):
            bodies = objects.bodies_without_material(study)
            if bodies:
                missing = QtWidgets.QLabel("No material (Run Mesh will stop): " + ", ".join(b.Label for b in bodies))
                missing.setWordWrap(True)
                missing.setStyleSheet("color: #c00000")
                layout.addWidget(missing)

    def highlight_rows(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()})
        highlight.show([ref for r in rows for ref in self.rows[r][1]])

    def open_item(self, row, _column):
        if self.study.Dimension == "3D":
            Gui.Control.showDialog(ItemPanel(self.rows[row][0]))


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
        self.regions = {}
        for name in ("Main", "Moving"):
            box = QtWidgets.QGroupBox()
            rows = QtWidgets.QVBoxLayout(box)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(name + "Geometry")
            rows.addWidget(combo)
            count = QtWidgets.QLabel()
            count.setWordWrap(True)
            rows.addWidget(count)
            buttons = QtWidgets.QHBoxLayout()
            inspect = QtWidgets.QPushButton("Inspect / highlight")
            manual = QtWidgets.QPushButton("Edit manual selection")
            inspect.clicked.connect(lambda _=False, n=name: self.inspect(n))
            manual.clicked.connect(lambda _=False, n=name: self.edit_manual(n))
            buttons.addWidget(inspect)
            buttons.addWidget(manual)
            rows.addLayout(buttons)
            layout.addWidget(box)
            self.regions[name] = (box, combo, count, manual)
            combo.currentIndexChanged.connect(lambda _i, n=name: self.choose_source(n))
        refresh = QtWidgets.QPushButton("Refresh geometry")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        self.diagnostics = QtWidgets.QLabel()
        self.diagnostics.setWordWrap(True)
        layout.addWidget(self.diagnostics)
        self.sliding_notice = QtWidgets.QLabel(
            "Sliding-interface configuration will be added with sliding-motion meshing."
        )
        self.sliding_notice.setWordWrap(True)
        layout.addWidget(self.sliding_notice)
        output = QtWidgets.QFormLayout()
        layout.addLayout(output)
        self.version = QtWidgets.QComboBox()
        self.version.addItems(study.getEnumerationsOfProperty("MshVersion"))
        self.version.setCurrentText(study.MshVersion)
        output.addRow("MSH version", self.version)
        self.id_button = QtWidgets.QPushButton("Edit IDs…")
        self.id_button.setEnabled(study.Dimension == "3D")
        self.id_button.clicked.connect(lambda: IdTableDialog(study).exec())
        layout.addWidget(self.id_button)
        self.run_button = QtWidgets.QPushButton("Generate mesh")
        self.run_button.clicked.connect(self.run_mesh)
        layout.addWidget(self.run_button)
        self.export_notice = QtWidgets.QLabel()
        self.export_notice.setWordWrap(True)
        layout.addWidget(self.export_notice)
        self.movement.currentTextChanged.connect(self.change_movement)
        self.version.currentTextChanged.connect(lambda value: self.save("MshVersion", value))
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
        containers = [o for o in study.Document.Objects if geometry.is_source(o)]
        labels = Counter(o.Label for o in containers)
        sliding = study.Movement == "Sliding motion"
        for name, (box, combo, count, manual) in self.regions.items():
            box.setTitle("Moving geometry" if name == "Moving" else "Fixed geometry" if sliding else "Main geometry")
            box.setVisible(name == "Main" or sliding)
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Choose a Part or Group…", "mode:Unassigned")
            combo.addItem("Manual selection", "mode:Manual")
            if name == "Main" and study.Dimension == "3D":
                combo.addItem("Material assignments (existing 3D workflow)", "mode:Materials")
            for obj in containers:
                kind = "Part" if obj.isDerivedFrom("App::Part") else "Group"
                label = f"{obj.Label} ({kind})"
                if labels[obj.Label] > 1:
                    label += f" — {obj.Name}"
                combo.addItem(label, "source:" + obj.Name)
            mode = getattr(study, name + "Mode")
            source = getattr(study, name + "Source")
            key = "source:" + source.Name if mode == "Container" and source is not None else "mode:" + mode
            if mode == "Container" and source is None:
                combo.addItem("Missing container — choose another", "mode:Container")
            combo.setCurrentIndex(combo.findData(key))
            combo.blockSignals(False)
            manual.setEnabled(mode == "Manual")
            resolved, _ = geometry.region(study, name)
            if study.Dimension == "2D":
                number = sum(len(obj.Shape.Faces) for obj in resolved)
                text = f"Included: {number} face region{'s' if number != 1 else ''} "
                text += f"({len(resolved)} object{'s' if len(resolved) != 1 else ''})"
            else:
                text = f"Included: {len(resolved)} solid object{'s' if len(resolved) != 1 else ''}"
            count.setText(text)
        _, _, errors = geometry.setup(study)
        if not errors and not geometry.export_unavailable(study):
            try:
                jobwriter.check(study)
            except jobwriter.StudyError as exc:
                errors.append(str(exc))
        self.diagnostics.setText("\n".join(errors))
        self.sliding_notice.setVisible(sliding)
        unavailable = geometry.export_unavailable(study)
        if unavailable:
            self.export_notice.setText(unavailable)
        else:
            try:
                self.export_notice.setText(f"Writes {jobwriter.mesh_file(study)}")
            except jobwriter.StudyError as exc:
                self.export_notice.setText(str(exc))
        self.update_run_button()

    def update_run_button(self):
        from . import runner

        if self.study.Document is not None:
            self.run_button.setEnabled(not geometry.export_unavailable(self.study) and not runner.busy())

    def choose_source(self, name):
        key = self.regions[name][1].currentData()
        if key is None:
            return
        kind, value = key.split(":", 1)
        mode = value if kind == "mode" else "Container"
        doc = self.study.Document
        doc.openTransaction("Choose Study geometry")
        setattr(self.study, name + "Mode", mode)
        if kind == "source":
            setattr(self.study, name + "Source", doc.getObject(value))
        doc.commitTransaction()
        doc.recompute()
        self.refresh()

    def inspect(self, name):
        Gui.Control.showDialog(GeometryPanel(self.study, name))

    def edit_manual(self, name):
        Gui.Control.showDialog(GeometryPanel(self.study, name, editable=True))

    def run_mesh(self):
        from . import runner

        runner.start(self.study)
        self.refresh()


class GeometryPanel:
    """Persistent bulk selection editor or inspection panel for a single Study region."""

    def __init__(self, study, region, editable=False):
        self.study, self.region, self.editable = study, region, editable
        self.current = list(getattr(study, region + "Objects")) if editable else geometry.region(study, region)[0]
        highlight.clear()
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Study geometry")
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.addWidget(QtWidgets.QLabel(f"{study.Label} — {region} geometry ({study.Dimension})"))
        self.refs = QtWidgets.QListWidget()
        self.refs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.refs.itemSelectionChanged.connect(self.highlight_rows)
        layout.addWidget(self.refs)
        self.message = QtWidgets.QLabel()
        self.message.setWordWrap(True)
        layout.addWidget(self.message)
        if editable:
            add = QtWidgets.QPushButton("Add selected objects / containers")
            remove = QtWidgets.QPushButton("Remove selected rows")
            add.clicked.connect(self.add_selection)
            remove.clicked.connect(self.remove)
            layout.addWidget(add)
            layout.addWidget(remove)
        self.refresh()

    def refresh(self):
        self.refs.clear()
        self.refs.addItems([f"{o.Label} — {o.Name}" for o in self.current])

    def add_selection(self):
        selected = [objects.owning_body(o) for o in Gui.Selection.getSelection() if o.Document == self.study.Document]
        added, errors = geometry.collect(selected, self.study.Dimension)
        if errors or not added:
            self.message.setText("\n".join(errors) or "Select filled faces or solid objects first.")
            return
        self.current = list(dict.fromkeys(self.current + added))
        self.message.clear()
        self.refresh()

    def remove(self):
        rows = {i.row() for i in self.refs.selectedIndexes()}
        self.current = [obj for i, obj in enumerate(self.current) if i not in rows]
        self.refresh()

    def highlight_rows(self):
        rows = sorted({i.row() for i in self.refs.selectedIndexes()})
        highlight.show([(self.current[r], "") for r in rows])

    def accept(self):
        if self.editable:
            _, errors = geometry.collect(self.current, self.study.Dimension)
            if errors:
                self.message.setText("\n".join(errors))
                return False
            doc = self.study.Document
            doc.openTransaction("Edit Study geometry")
            setattr(self.study, self.region + "Objects", self.current)
            setattr(self.study, self.region + "Mode", "Manual")
            doc.commitTransaction()
            doc.recompute()
        return self.reject()

    def reject(self):
        highlight.clear()
        Gui.Control.closeDialog()
        return True

    def getStandardButtons(self):
        return (
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
            if self.editable
            else QtWidgets.QDialogButtonBox.Close
        )


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
        if len(sel) == 1 and objects.is_item(sel[0]) and not editing:
            highlight.show(objects.item_refs(sel[0]))
        else:
            highlight.clear()
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
        Gui.Control.showDialog(ItemPanel(vobj.Object))
        return True


class ItemPanel:
    """Edit name, size (Mesh Size only) and references of a tree item."""

    def __init__(self, obj):
        self.obj = obj
        study = objects.owner_study(obj)
        highlight.clear()  # it would not follow the edits
        self.bodies_only = isinstance(obj.Proxy, objects.Material)
        if self.bodies_only:
            self.pick, label = (lambda: [(b, "") for b in selected_bodies()]), "Bodies"
        elif isinstance(obj.Proxy, objects.Excitation):
            self.pick, label = selected_faces, "Faces"
        else:
            self.pick, label = selected_mesh_refs, "Bodies, faces,\nedges, vertices"
        self.current = objects.item_refs(obj)
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QFormLayout(self.form)
        layout.addRow(QtWidgets.QLabel("Study: " + study.Label))
        self.name = QtWidgets.QLineEdit(objects.display_name(obj))
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
