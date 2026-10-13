"""Temporary Material Manager GUI for the Material Library: a picker and the library's own editor window.

Delete this module when ems_material ships MaterialPickerDialog and MaterialEditorWidget
(docs/superpowers/specs/2026-10-13-ems-material-manager-widgets-prd.md).
"""

import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from ems_material import MaterialManager, MaterialManagerError

from . import objects, studymaterials

_editors = {}  # (document name, Study Name) -> MaterialManagerWindow


class MaterialPicker(QtWidgets.QDialog):
    """Search the Material Manager and pick materials; IDs in taken cannot be picked."""

    def __init__(self, manager, taken, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import from Material Manager")
        self.manager, self.taken = manager, set(taken)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search name, ID, manufacturer, tag…")
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list)
        layout.addWidget(buttons)
        self.resize(480, 520)
        self.search.textChanged.connect(self.fill)
        self.fill()

    def fill(self, *_):
        text = self.search.text().strip()
        self.list.clear()
        for m in self.manager.search(text=text) if text else self.manager.list():
            item = QtWidgets.QListWidgetItem(f"{m.name} — {m.family} ({self.manager.source_for(m.material_id)})")
            item.setData(QtCore.Qt.UserRole, m.material_id)
            if m.material_id in self.taken:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled & ~QtCore.Qt.ItemIsSelectable)
                item.setToolTip("already in Material Library")
            self.list.addItem(item)

    def selected(self):
        return [self.manager.get(i.data(QtCore.Qt.UserRole)) for i in self.list.selectedItems()]


def ask_root(parent=None):
    """Ask for the Material Manager root; remember and return it only if it has manager.config.json."""
    from . import taskpanels

    parent = parent or Gui.getMainWindow()
    root = QtWidgets.QFileDialog.getExistingDirectory(parent, "Material Manager root (folder with manager.config.json)")
    if not root:
        return None
    if not studymaterials.is_manager_root(root):
        taskpanels.warn(f"Not a Material Manager root (no manager.config.json): {root}")
        return None
    from ems_material.gui.product_exchange import remember_library_root

    remember_library_root(root)  # shared with eMotorSolution
    return root


def _root(parent):
    return studymaterials.library_root() or ask_root(parent)


def pick_materials(study, parent=None):
    """Ask for materials and copy them into the Material Library. Returns the new objects."""
    parent = parent or Gui.getMainWindow()
    root = _root(parent)
    if root is None:
        return []
    try:
        manager = MaterialManager(root)
        taken = {o.MaterialId for o in objects.library_materials(study)}
        dialog = MaterialPicker(manager, taken, parent)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return []
        return studymaterials.import_materials(study, dialog.selected())
    except MaterialManagerError as exc:
        QtWidgets.QMessageBox.warning(parent, "Material Manager", str(exc))
        return []


def _edits(window, study):
    """True while window is alive and edits this very Study."""
    try:
        window.isVisible()  # RuntimeError once Qt deleted it
        return window.library.repository.study is study and study.Document is not None
    except (ReferenceError, RuntimeError, AttributeError):
        return False


def open_editor(study, material_id=None):
    """The library's editor window on the Study's Material Library; one per Study."""
    from ems_material.gui import MaterialManagerWindow
    from . import taskpanels

    key = (study.Document.Name, study.Name)
    window = _editors.get(key)
    if window is not None and not _edits(window, study):  # a closed document's Names are reused
        _editors.pop(key, None)
        try:
            window.close()
        except RuntimeError:  # the Qt window is already gone
            pass
        window = None
    if window is None:
        repository = studymaterials.StudyMaterialRepository(study, on_change=taskpanels.refresh_library_views)
        window = MaterialManagerWindow(MaterialManager(repository=repository), Gui.getMainWindow())
        window.setWindowTitle(f"Material Library — {study.Label}")
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.destroyed.connect(lambda *_, w=window: _editors.get(key) is w and _editors.pop(key))
        _editors[key] = window
    window.reload_materials(select_id=material_id)
    window.show()
    window.raise_()
    window.activateWindow()
    return window
