"""View providers, the item edit panel, the ID table dialog and selection helpers."""
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
            self.size = QtWidgets.QDoubleSpinBox()
            self.size.setDecimals(3)
            self.size.setRange(0.001, 1e6)
            self.size.setSuffix(" mm")
            self.size.setValue(obj.Size.Value)
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
        self.refs.addItems([f"{b.Label}.{f}" if f else b.Label for b, f in self.current])

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
