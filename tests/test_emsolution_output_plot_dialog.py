from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSplitter

from pyemsi.gui._viewers._emsolution_plot_dialog import EMSolutionPlotDialog
from pyemsi.gui.file_viewers import MatplotlibViewer
from pyemsi.io import EMSolutionOutput


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _sample_payload():
    return {
        "metaData": {
            "EMSolutionVersion": "1.0",
            "releaseDate": "2026-01-01",
            "creationDate": "2026-01-02",
            "comments": "example",
        },
        "analysisCondition": {
            "analysisType": "TRANSIENT",
            "nonlinear": "LINEAR",
            "motionType": "SLIDE_MOTION",
            "circuitType": "NETWORK",
        },
        "timeStep": {
            "time": [0.0, 1.0, 2.0],
            "timeUnit": "s",
            "position": [[0.0, 5.0, 10.0]],
            "positionUnit": "deg",
            "motionDirection": "CW",
        },
        "postData": {
            "network": {
                "networkUnit": ["A", "V", "Wb"],
                "networkData": [
                    {
                        "elementNum": 3,
                        "elementName": "Coil",
                        "current": [1.0, 2.0, 3.0],
                        "voltage": [4.0, 5.0, 6.0],
                    }
                ],
            }
        },
    }


def _first_leaf(item):
    if item.childCount() == 0:
        return item
    return _first_leaf(item.child(0))


def test_emsolution_plot_dialog_places_tree_left_and_preview_right():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    splitter = dialog.findChild(QSplitter)

    assert splitter is not None
    assert splitter.widget(0).findChild(type(dialog._tree)) is dialog._tree
    assert isinstance(splitter.widget(1), MatplotlibViewer)
    assert dialog._x_label_edit.placeholderText() == "Time (s)"


def test_emsolution_plot_dialog_updates_preview_from_tree_and_labels():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._title_edit.setText("Custom Plot")
    dialog._x_label_edit.setText("Rotor Angle")
    dialog._y_label_edit.setText("Response")
    dialog._redraw_plot()

    ax = dialog._preview.figure.axes[0]

    assert len(ax.lines) == 1
    assert ax.get_title() == "Custom Plot"
    assert ax.get_xlabel() == "Rotor Angle"
    assert ax.get_ylabel() == "Response"


def test_emsolution_plot_dialog_toggles_legend_and_grid():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._show_legend_checkbox.setChecked(False)
    dialog._show_grid_checkbox.setChecked(True)
    dialog._redraw_plot()

    ax = dialog._preview.figure.axes[0]

    assert ax.get_legend() is None
    assert any(line.get_visible() for line in ax.xaxis.get_gridlines())
    assert any(line.get_visible() for line in ax.yaxis.get_gridlines())


def test_emsolution_plot_dialog_applies_per_series_style():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    dialog._tree.setCurrentItem(leaf)
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._line_style_combo.setCurrentIndex(dialog._line_style_combo.findData("--"))
    dialog._marker_combo.setCurrentIndex(dialog._marker_combo.findData("o"))
    dialog._line_width_spin.setValue(2.5)
    style = dialog._style_for_descriptor(dialog._current_styled_series())
    style.color = "#ff0000"
    dialog._update_color_button(style.color)
    dialog._redraw_plot()

    line = dialog._preview.figure.axes[0].lines[0]

    assert line.get_linestyle() == "--"
    assert line.get_marker() == "o"
    assert line.get_linewidth() == 2.5
    assert line.get_color() == "#ff0000"


def test_emsolution_plot_dialog_preserves_distinct_styles_for_multiple_series():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)

    dialog._tree.setCurrentItem(first_leaf)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._line_style_combo.setCurrentIndex(dialog._line_style_combo.findData("--"))
    dialog._line_width_spin.setValue(2.0)

    dialog._tree.setCurrentItem(second_leaf)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._marker_combo.setCurrentIndex(dialog._marker_combo.findData("s"))
    dialog._line_width_spin.setValue(3.0)

    dialog._redraw_plot()
    lines = dialog._preview.figure.axes[0].lines

    assert len(lines) == 2
    assert lines[0].get_linestyle() == "--"
    assert lines[0].get_linewidth() == 2.0
    assert lines[1].get_marker() == "s"
    assert lines[1].get_linewidth() == 3.0


def test_emsolution_plot_dialog_disables_style_controls_for_unchecked_leaf():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    dialog._tree.setCurrentItem(leaf)

    assert dialog._line_style_combo.isEnabled() is False
    assert dialog._marker_combo.isEnabled() is False
    assert dialog._line_width_spin.isEnabled() is False
    assert dialog._color_button.isEnabled() is False
