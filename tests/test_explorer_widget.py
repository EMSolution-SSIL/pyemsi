"""Focused checks for the Explorer icon and toolbar behavior."""

from __future__ import annotations

from PySide6.QtCore import QFile, QFileInfo, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pyemsi.widgets.explorer_icons import MaterialFileIconProvider, icon_name_for_path
from pyemsi.widgets.explorer_widget import ExplorerWidget


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_material_icon_associations_cover_pyemsi_formats() -> None:
    assert icon_name_for_path("project/.pyemsi", is_dir=True) == "folder-simulations"
    assert icon_name_for_path("mesh.vtu", is_dir=False) == "vtk"
    assert icon_name_for_path("assembly.FCStd", is_dir=False) == "freecad"
    assert icon_name_for_path("post_geom.neu", is_dir=False) == "simulink"
    assert icon_name_for_path("unknown.bin", is_dir=False) == "document"


def test_material_icon_provider_loads_bundled_icons(tmp_path) -> None:
    app = _app()
    python_file = tmp_path / "model.py"
    python_file.touch()

    provider = MaterialFileIconProvider()

    assert QFile.exists(":/icons/material/python.svg")
    assert QFile.exists(":/icons/FreeCAD.svg")
    icon = provider.icon(QFileInfo(str(python_file)))
    assert isinstance(icon, QIcon)
    assert provider._icons["python"] is icon
    assert app is QApplication.instance()


def test_explorer_uses_18px_icons_and_enables_toolbar(tmp_path) -> None:
    app = _app()
    widget = ExplorerWidget()
    try:
        assert widget._tree.iconSize() == QSize(18, 18)
        assert not widget._new_file_action.isEnabled()

        widget.set_directory(str(tmp_path))

        assert widget._new_file_action.isEnabled()
        assert widget._new_folder_action.isEnabled()
        assert widget._refresh_action.isEnabled()
        assert widget._collapse_action.isEnabled()
        assert widget._root_label.text() == tmp_path.name.upper()
        assert app is QApplication.instance()
    finally:
        widget.close()


def test_explorer_exposes_expected_context_commands_and_terminal_signal(tmp_path) -> None:
    _app()
    widget = ExplorerWidget()
    terminal_paths: list[str] = []
    widget.terminal_requested.connect(terminal_paths.append)
    try:
        widget.set_directory(str(tmp_path))
        widget._context_path = str(tmp_path)
        widget._open_context_terminal()

        assert widget._open_action.text() == "Open"
        assert widget._rename_action.text() == "Rename..."
        assert widget._trash_action.text() in {"Move to Recycle Bin", "Move to Trash"}
        assert widget._copy_relative_action.text() == "Copy Relative Path"
        assert widget._copy_full_action.text() == "Copy Full Path"
        assert terminal_paths == [str(tmp_path)]
    finally:
        widget.close()
