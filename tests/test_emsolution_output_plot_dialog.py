from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QPushButton, QSplitter

from pyemsi.gui._viewers import _emsolution_plot_dialog
from pyemsi.gui._viewers._emsolution_plot_dialog import (
    EMSolutionPlotDialog,
    PlotDialogSettings,
    PlotSeriesStyle,
    PlotSettingsDialog,
)
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


def _positive_payload():
    payload = _sample_payload()
    payload["timeStep"]["time"] = [1.0, 2.0, 3.0]
    payload["timeStep"]["position"] = [[5.0, 10.0, 15.0]]
    return payload


def _mixed_sign_payload():
    payload = _positive_payload()
    payload["postData"]["network"]["networkData"][0]["voltage"] = [4.0, 0.0, 6.0]
    return payload


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
            legend_mode="best",
            grid_mode="off",
        )
    )
    dialog._redraw_plot()

    ax = dialog._preview.figure.axes[0]

    assert len(ax.lines) == 1
    assert ax.get_title() == "Custom Plot"
    assert ax.get_xlabel() == "Rotor Angle"
    assert ax.get_ylabel() == "Response"


def test_emsolution_plot_dialog_applies_legend_and_grid_modes():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            legend_mode="none",
            grid_mode="x",
        )
    )
    dialog._redraw_plot()

    ax = dialog._preview.figure.axes[0]

    assert ax.get_legend() is None
    assert any(line.get_visible() for line in ax.xaxis.get_gridlines())
    assert not any(line.get_visible() for line in ax.yaxis.get_gridlines())


def test_emsolution_plot_dialog_applies_legend_location_mode():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            legend_mode="lower left",
        )
    )

    legend = dialog._preview.figure.axes[0].get_legend()

    assert legend is not None
    assert legend._loc == 3


def test_emsolution_plot_dialog_applies_major_only_grid_mode_for_log_scale():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            x_log_scale=True,
            y_log_scale=True,
            grid_mode="major",
        )
    )

    ax = dialog._preview.figure.axes[0]

    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
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
        PlotSeriesStyle(label="Custom Current", line_style="--", marker="o", line_width=2.5, color="#ff0000"),
    )
    dialog._redraw_plot()

    ax = dialog._preview.figure.axes[0]
    line = ax.lines[0]

    assert line.get_linestyle() == "--"
    assert line.get_marker() == "o"
    assert line.get_linewidth() == 2.5
    assert line.get_color() == "#ff0000"
    assert ax.get_legend_handles_labels()[1] == ["Custom Current"]


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


def test_plot_settings_dialog_round_trips_style_and_log_scale_settings():
    _app()
    result = EMSolutionOutput.from_dict(_positive_payload())
    x_options = {option.key: option for option in result.get_plot_x_options()}
    x_axis_key = next(iter(x_options))

    dialog = PlotSettingsDialog(
        x_options,
        PlotDialogSettings(
            x_axis_key=x_axis_key,
            title="Custom Plot",
            x_label="Rotor Angle",
            y_label="Response",
            style_preset="ggplot",
            legend_mode="none",
            grid_mode="off",
            x_log_scale=True,
            y_log_scale=True,
        ),
        default_title="Default Title",
        default_x_label="Default X",
        default_y_label="Default Y",
    )

    settings = dialog.settings()

    assert settings.style_preset == "ggplot"
    assert settings.x_log_scale is True
    assert settings.y_log_scale is True
    assert settings.legend_mode == "none"
    assert settings.grid_mode == "off"


def test_series_style_dialog_round_trips_custom_label():
    _app()
    dialog = _emsolution_plot_dialog.SeriesStyleDialog(
        PlotSeriesStyle(label="Custom Voltage", line_style="--"),
        "Voltage",
    )

    style = dialog.style()

    assert style.label == "Custom Voltage"
    assert style.line_style == "--"


def test_plot_settings_dialog_apply_emits_current_settings_without_closing():
    _app()
    result = EMSolutionOutput.from_dict(_positive_payload())
    x_options = {option.key: option for option in result.get_plot_x_options()}
    x_axis_key = next(iter(x_options))
    dialog = PlotSettingsDialog(
        x_options,
        PlotDialogSettings(x_axis_key=x_axis_key),
        default_title="Default Title",
        default_x_label="Default X",
        default_y_label="Default Y",
    )

    applied = []
    dialog.settingsApplied.connect(applied.append)

    dialog._title_edit.setText("Preview Title")
    dialog._x_log_scale_checkbox.setChecked(True)
    apply_button = dialog._button_box.button(QDialogButtonBox.StandardButton.Apply)

    assert apply_button is not None

    apply_button.click()

    assert dialog.result() == 0
    assert len(applied) == 1
    assert applied[0].title == "Preview Title"
    assert applied[0].x_log_scale is True


def test_plot_settings_dialog_cancel_emits_original_settings():
    _app()
    result = EMSolutionOutput.from_dict(_positive_payload())
    x_options = {option.key: option for option in result.get_plot_x_options()}
    x_axis_key = next(iter(x_options))
    original = PlotDialogSettings(
        x_axis_key=x_axis_key,
        title="Original Title",
        style_preset="ggplot",
        grid_mode="off",
        x_log_scale=True,
    )
    dialog = PlotSettingsDialog(
        x_options,
        original,
        default_title="Default Title",
        default_x_label="Default X",
        default_y_label="Default Y",
    )

    canceled = []
    dialog.settingsCanceled.connect(canceled.append)

    dialog._title_edit.setText("Changed Title")
    dialog._style_preset_combo.setCurrentIndex(0)
    dialog._grid_mode_combo.setCurrentIndex(1)
    dialog._x_log_scale_checkbox.setChecked(False)
    cancel_button = dialog._button_box.button(QDialogButtonBox.StandardButton.Cancel)

    assert cancel_button is not None

    cancel_button.click()

    assert dialog.result() == QDialog.DialogCode.Rejected
    assert len(canceled) == 1
    assert canceled[0] == original


def test_emsolution_plot_dialog_restores_original_settings_when_plot_settings_cancel(monkeypatch):
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))
    original = dialog._plot_settings
    changed = PlotDialogSettings(
        x_axis_key=original.x_axis_key,
        title="Applied Title",
        style_preset="ggplot",
        x_log_scale=True,
    )

    class _Signal:
        def __init__(self):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

        def emit(self, value):
            for callback in self._callbacks:
                callback(value)

    class StubDialog:
        def __init__(self, *args, **kwargs):
            self.settingsApplied = _Signal()
            self.settingsCanceled = _Signal()

        def exec(self):
            self.settingsApplied.emit(changed)
            self.settingsCanceled.emit(original)
            return QDialog.DialogCode.Rejected

        def settings(self):
            return changed

    monkeypatch.setattr(_emsolution_plot_dialog, "PlotSettingsDialog", StubDialog)

    dialog._open_plot_settings_dialog()

    assert dialog._plot_settings == original


def test_emsolution_plot_dialog_applies_style_preset_with_scoped_context(monkeypatch):
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    captured = []

    class DummyContext:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_style_context(style_name):
        captured.append(style_name)
        return DummyContext()

    monkeypatch.setattr(_emsolution_plot_dialog, "_matplotlib_style_context", fake_style_context)

    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            style_preset="ggplot",
        )
    )

    assert "ggplot" in captured


def test_emsolution_plot_dialog_uses_custom_series_label_in_legend():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    descriptor = dialog._descriptor_for_item(leaf)
    assert descriptor is not None

    dialog._apply_series_style(descriptor, PlotSeriesStyle(label="Rotor Current"))

    ax = dialog._preview.figure.axes[0]

    assert ax.get_legend_handles_labels()[1] == ["Rotor Current"]


def test_emsolution_plot_dialog_applies_log_scale_to_axes():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            x_log_scale=True,
            y_log_scale=True,
        )
    )

    ax = dialog._preview.figure.axes[0]

    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
    assert len(ax.lines) == 1
    assert dialog._warning_label.isHidden()


def test_emsolution_plot_dialog_skips_invalid_y_series_for_log_scale():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_mixed_sign_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)

    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            y_log_scale=True,
        )
    )

    ax = dialog._preview.figure.axes[0]

    assert ax.get_yscale() == "log"
    assert len(ax.lines) == 1
    assert not dialog._warning_label.isHidden()
    assert "Skipped series with non-positive Y values" in dialog._warning_label.text()


def test_emsolution_plot_dialog_warns_when_x_log_scale_is_invalid():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            x_log_scale=True,
        )
    )

    ax = dialog._preview.figure.axes[0]

    assert ax.get_xscale() == "log"
    assert len(ax.lines) == 0
    assert not dialog._warning_label.isHidden()
    assert "X-axis log scale requires all X values to be greater than zero." in dialog._warning_label.text()


def test_plot_settings_dialog_round_trips_legend_and_grid_modes_from_comboboxes():
    _app()
    result = EMSolutionOutput.from_dict(_positive_payload())
    x_options = {option.key: option for option in result.get_plot_x_options()}
    x_axis_key = next(iter(x_options))
    dialog = PlotSettingsDialog(
        x_options,
        PlotDialogSettings(x_axis_key=x_axis_key),
        default_title="Default Title",
        default_x_label="Default X",
        default_y_label="Default Y",
    )

    dialog._legend_mode_combo.setCurrentIndex(dialog._legend_mode_combo.findData("upper left"))
    dialog._grid_mode_combo.setCurrentIndex(dialog._grid_mode_combo.findData("y"))

    settings = dialog.settings()

    assert settings.legend_mode == "upper left"
    assert settings.grid_mode == "y"
