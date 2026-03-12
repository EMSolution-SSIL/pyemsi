from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton, QSplitter

from pyemsi.gui._viewers._emsolution_plot_dialog import EMSolutionPlotDialog, PlotDialogSettings, PlotSeriesStyle
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
    assert dialog._plot_settings_button.text() == "Plot Settings..."


def test_emsolution_plot_dialog_uses_default_axis_label_before_overrides():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    assert dialog._effective_x_label() == "Time (s)"


def test_emsolution_plot_dialog_updates_preview_from_tree_and_labels():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            title="Custom Plot",
            x_label="Rotor Angle",
            y_label="Response",
            show_legend=True,
            show_grid=False,
        )
    )
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
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            show_legend=False,
            show_grid=True,
        )
    )
    dialog._redraw_plot()

    ax = dialog._preview.figure.axes[0]

    assert ax.get_legend() is None
    assert any(line.get_visible() for line in ax.xaxis.get_gridlines())
    assert any(line.get_visible() for line in ax.yaxis.get_gridlines())


def test_emsolution_plot_dialog_applies_per_series_style():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    descriptor = dialog._descriptor_for_item(leaf)
    assert descriptor is not None
    dialog._apply_series_style(
        descriptor,
        PlotSeriesStyle(line_style="--", marker="o", line_width=2.5, color="#ff0000"),
    )
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

    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)

    first_descriptor = dialog._descriptor_for_item(first_leaf)
    second_descriptor = dialog._descriptor_for_item(second_leaf)
    assert first_descriptor is not None
    assert second_descriptor is not None

    dialog._apply_series_style(first_descriptor, PlotSeriesStyle(line_style="--", line_width=2.0))
    dialog._apply_series_style(second_descriptor, PlotSeriesStyle(marker="s", line_width=3.0))

    dialog._redraw_plot()
    lines = dialog._preview.figure.axes[0].lines

    assert len(lines) == 2
    assert lines[0].get_linestyle() == "--"
    assert lines[0].get_linewidth() == 2.0
    assert lines[1].get_marker() == "s"
    assert lines[1].get_linewidth() == 3.0


def test_emsolution_plot_dialog_only_shows_style_button_for_checked_leaf():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    assert dialog._tree.itemWidget(leaf, dialog.SETTINGS_COLUMN) is None

    leaf.setCheckState(0, Qt.CheckState.Checked)
    button = dialog._tree.itemWidget(leaf, dialog.SETTINGS_COLUMN)

    assert isinstance(button, QPushButton)
    assert button.text() == "Style"

    leaf.setCheckState(0, Qt.CheckState.Unchecked)

    assert dialog._tree.itemWidget(leaf, dialog.SETTINGS_COLUMN) is None


def test_emsolution_plot_dialog_style_button_opens_for_checked_leaf(monkeypatch):
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    button = dialog._tree.itemWidget(leaf, dialog.SETTINGS_COLUMN)

    opened = {"item": None}

    def fake_open(item):
        opened["item"] = item

    monkeypatch.setattr(dialog, "_open_style_dialog_for_item", fake_open)
    button.click()

    assert opened["item"] is leaf
