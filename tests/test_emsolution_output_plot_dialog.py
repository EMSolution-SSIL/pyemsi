import json
from pathlib import Path

from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QPushButton, QSplitter

from pyemsi.gui import emsolution_output_plot_builder_dialog as _emsolution_plot_dialog
from pyemsi.gui.emsolution_output_plot_builder_dialog import (
    EMSolutionOutputPlotBuilderDialog,
    EMSolutionOutputPlotBuilderDialog as EMSolutionPlotDialog,
    GeneratedScriptDialog,
    PlotDialogSettings,
    PlotSeriesStyle,
    PlotSettingsDialog,
)
from pyemsi.gui.file_viewers import MatplotlibViewer
from pyemsi.io import EMSolutionOutput
from pyemsi.widgets.monaco_lsp import MonacoLspWidget


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _uses_tight_layout(figure: Figure) -> bool:
    if hasattr(figure, "get_layout_engine"):
        engine = figure.get_layout_engine()
        return engine is not None and engine.__class__.__name__ == "TightLayoutEngine"
    return bool(figure.get_tight_layout())


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


def _rich_payload():
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
            "time": [1.0, 2.0, 3.0],
            "timeUnit": "s",
            "position": [[5.0, 10.0, 15.0]],
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
            },
            "forceNodal": {
                "forceUnit": ["N", "Nm"],
                "forceNodalData": [
                    {
                        "propertyNum": 12,
                        "forceX": [1.0, 1.5, 2.0],
                        "forceY": [2.0, 2.5, 3.0],
                        "forceZ": [3.0, 3.5, 4.0],
                        "forceMX": [4.0, 4.5, 5.0],
                        "forceMY": [5.0, 5.5, 6.0],
                        "forceMZ": [6.0, 6.5, 7.0],
                    }
                ],
            },
        },
    }


def _first_leaf(item):
    if item.childCount() == 0:
        return item
    return _first_leaf(item.child(0))


def _find_item_by_path(tree, path):
    current = None
    for depth, text in enumerate(path):
        if depth == 0:
            matches = [
                tree.topLevelItem(index)
                for index in range(tree.topLevelItemCount())
                if tree.topLevelItem(index).text(0) == text
            ]
        else:
            matches = [
                current.child(index) for index in range(current.childCount()) if current.child(index).text(0) == text
            ]
        assert matches
        current = matches[0]
    return current


def _find_combo_index_by_data(combo, data):
    for index in range(combo.count()):
        if combo.itemData(index) == data:
            return index
    raise AssertionError(f"Could not find combo data: {data!r}")


def _set_indicator_mode(viewer: MatplotlibViewer, mode: str) -> None:
    viewer._indicator_mode_combo.setCurrentIndex(_find_combo_index_by_data(viewer._indicator_mode_combo, mode))


def _set_indicator_index_combo(viewer: MatplotlibViewer, index: int) -> None:
    viewer._indicator_index_combo.setCurrentIndex(_find_combo_index_by_data(viewer._indicator_index_combo, index))


def _indicator_artists_on_axis(viewer: MatplotlibViewer, axis) -> list:
    return [artist for artist in viewer._indicator_artists if getattr(artist, "axes", None) is axis]


def test_emsolution_plot_dialog_places_tree_left_and_preview_right():
    _app()
    dialog = EMSolutionOutputPlotBuilderDialog(EMSolutionOutput.from_dict(_sample_payload()))

    splitter = dialog.findChild(QSplitter)

    assert splitter is not None
    assert splitter.widget(0).findChild(type(dialog._tree)) is dialog._tree
    assert isinstance(splitter.widget(1), MatplotlibViewer)
    assert dialog._plot_settings_button.text() == "Plot Settings..."


def test_matplotlib_viewer_enables_tight_layout_by_default():
    _app()

    viewer = MatplotlibViewer()

    assert _uses_tight_layout(viewer.figure)


def test_matplotlib_viewer_can_disable_tight_layout():
    _app()

    viewer = MatplotlibViewer(Figure(), tight_layout=False)

    assert not _uses_tight_layout(viewer.figure)


def test_matplotlib_viewer_exposes_indicator_toolbar_combos_with_off_default():
    _app()

    figure = Figure()
    axis = figure.add_subplot(111)
    axis.plot([0, 1, 2], [3, 4, 5])
    viewer = MatplotlibViewer(figure, tight_layout=False)

    assert viewer._indicator_mode_combo.count() == 4
    assert viewer._indicator_mode_combo.itemData(viewer._indicator_mode_combo.currentIndex()) == (
        MatplotlibViewer.INDICATOR_MODE_OFF
    )
    assert viewer._indicator_index_combo.count() == 3
    assert viewer._indicator_index_combo.currentIndex() == -1
    assert viewer._indicator_index_combo.itemText(0) == "0   : 0"
    assert viewer._indicator_index_combo.itemText(1) == "1   : 1"


def test_matplotlib_viewer_indicator_index_combo_tracks_slot_and_manual_selection():
    _app()

    figure = Figure()
    axis = figure.add_subplot(111)
    axis.plot([0, 1, 2], [1, 2, 3])
    viewer = MatplotlibViewer(figure, tight_layout=False)

    viewer.set_indicator_index(2)

    assert viewer._indicator_index_combo.currentData() == 2
    assert viewer._indicator_index == 2
    assert viewer._indicator_artists[0].get_xdata()[0] == 2

    _set_indicator_index_combo(viewer, 1)

    assert viewer._indicator_index == 1
    assert viewer._indicator_index_combo.currentData() == 1
    assert viewer._indicator_artists[0].get_xdata()[0] == 1


def test_matplotlib_viewer_vertical_indicator_renders_per_eligible_subplot_without_duplicates():
    _app()

    figure = Figure()
    axes = figure.subplots(2, 1, squeeze=False)
    top_axis = axes[0][0]
    bottom_axis = axes[1][0]
    top_axis.plot([0, 1, 2], [1, 2, 3])
    top_axis.plot([0, 1, 2], [3, 2, 1])
    bottom_axis.plot([0, 1, 2], [2, 3, 4])

    viewer = MatplotlibViewer(figure, tight_layout=False)
    viewer.set_indicator_index(1)

    assert len(_indicator_artists_on_axis(viewer, top_axis)) == 1
    assert len(_indicator_artists_on_axis(viewer, bottom_axis)) == 1
    assert len(top_axis.lines) == 3
    assert len(bottom_axis.lines) == 2

    viewer.draw()

    assert len(_indicator_artists_on_axis(viewer, top_axis)) == 1
    assert len(_indicator_artists_on_axis(viewer, bottom_axis)) == 1
    assert len(top_axis.lines) == 3
    assert len(bottom_axis.lines) == 2


def test_matplotlib_viewer_off_mode_hides_indicator_but_preserves_index():
    _app()

    figure = Figure()
    axis = figure.add_subplot(111)
    axis.plot([0, 1, 2], [4, 5, 6])
    viewer = MatplotlibViewer(figure, tight_layout=False)

    _set_indicator_mode(viewer, MatplotlibViewer.INDICATOR_MODE_VERTICAL_LINE)
    viewer.set_indicator_index(2)

    assert len(viewer._indicator_artists) == 1

    _set_indicator_mode(viewer, MatplotlibViewer.INDICATOR_MODE_OFF)

    assert viewer._indicator_index == 2
    assert len(viewer._indicator_artists) == 0
    assert len(axis.lines) == 1

    _set_indicator_mode(viewer, MatplotlibViewer.INDICATOR_MODE_VERTICAL_LINE)

    assert len(viewer._indicator_artists) == 1
    assert len(axis.lines) == 2


def test_matplotlib_viewer_strict_axis_eligibility_ignores_invisible_lines():
    _app()

    figure = Figure()
    axes = figure.subplots(2, 1, squeeze=False)
    eligible_axis = axes[0][0]
    ineligible_axis = axes[1][0]
    eligible_axis.plot([0, 1, 2], [1, 2, 3])
    hidden_short_line = eligible_axis.plot([0], [9])[0]
    hidden_short_line.set_visible(False)
    ineligible_axis.plot([0, 1, 2], [3, 4, 5])
    ineligible_axis.plot([0], [8])

    viewer = MatplotlibViewer(figure, tight_layout=False)
    viewer.set_indicator_index(2)

    assert len(_indicator_artists_on_axis(viewer, eligible_axis)) == 1
    assert len(_indicator_artists_on_axis(viewer, ineligible_axis)) == 0
    assert len(viewer._indicator_artists) == 1


def test_matplotlib_viewer_marker_modes_create_expected_indicator_artists():
    _app()

    figure = Figure()
    axis = figure.add_subplot(111)
    axis.plot([0, 1, 2], [1, 2, 3])
    axis.plot([0, 1, 2], [3, 2, 1])
    viewer = MatplotlibViewer(figure, tight_layout=False)
    viewer.set_indicator_index(1)

    _set_indicator_mode(viewer, MatplotlibViewer.INDICATOR_MODE_MARKERS)

    assert len(_indicator_artists_on_axis(viewer, axis)) == 2
    assert len(axis.lines) == 4

    _set_indicator_mode(viewer, MatplotlibViewer.INDICATOR_MODE_LINE_AND_MARKERS)

    assert len(_indicator_artists_on_axis(viewer, axis)) == 3
    assert len(axis.lines) == 5


def test_matplotlib_viewer_ignores_negative_indicator_indices():
    _app()

    figure = Figure()
    axis = figure.add_subplot(111)
    axis.plot([0, 1, 2], [1, 2, 3])
    viewer = MatplotlibViewer(figure, tight_layout=False)
    viewer.set_indicator_index(1)
    indicator_x = viewer._indicator_artists[0].get_xdata()[0]

    viewer.set_indicator_index(-1)

    assert viewer._indicator_index == 1
    assert len(viewer._indicator_artists) == 1
    assert viewer._indicator_artists[0].get_xdata()[0] == indicator_x


def test_emsolution_plot_dialog_and_subdialogs_expose_plot_icons():
    _app()
    dialog = EMSolutionOutputPlotBuilderDialog(EMSolutionOutput.from_dict(_sample_payload()))
    result = EMSolutionOutput.from_dict(_positive_payload())
    x_options = {option.key: option for option in result.get_plot_x_options()}
    x_axis_key = next(iter(x_options))
    settings_dialog = PlotSettingsDialog(
        x_options,
        PlotDialogSettings(x_axis_key=x_axis_key),
        default_title="Default Title",
        default_x_label="Default X",
        default_y_label="Default Y",
    )
    style_dialog = _emsolution_plot_dialog.SeriesStyleDialog(PlotSeriesStyle(), "Series")
    script_dialog = GeneratedScriptDialog("print('hello')")

    assert not dialog.windowIcon().isNull()
    assert not settings_dialog.windowIcon().isNull()
    assert not style_dialog.windowIcon().isNull()
    assert not script_dialog.windowIcon().isNull()
    assert not script_dialog._copy_button.icon().isNull()
    assert not script_dialog._save_button.icon().isNull()
    assert not dialog._plot_settings_button.icon().isNull()
    assert not dialog._script_button.icon().isNull()
    assert not dialog._plot_button.icon().isNull()


def test_generated_script_dialog_uses_monaco_python_editor():
    _app()
    dialog = GeneratedScriptDialog("print('hello')")

    assert isinstance(dialog._text_edit, MonacoLspWidget)
    assert dialog._text_edit.language() == "python"
    assert dialog._text_edit.isReadOnly() is True
    assert dialog.script_text() == "print('hello')"


def test_generated_script_dialog_copy_button_updates_clipboard():
    app = _app()
    dialog = GeneratedScriptDialog("print('copied')")

    dialog._copy_button.click()

    assert app.clipboard().text() == "print('copied')"


def test_generated_script_dialog_save_button_writes_python_file(tmp_path, monkeypatch):
    _app()
    dialog = GeneratedScriptDialog("print('saved')")
    save_target = tmp_path / "generated_script"

    monkeypatch.setattr(
        _emsolution_plot_dialog.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(save_target), "Python Files (*.py)"),
    )

    dialog._save_button.click()

    saved_path = Path(f"{save_target}.py")
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == "print('saved')"


def test_generated_script_dialog_uses_explorer_path_for_save_dialog(tmp_path, monkeypatch):
    _app()
    dialog = GeneratedScriptDialog("print('saved')")

    class _Explorer:
        current_path = str(tmp_path)

    class _Window:
        explorer = _Explorer()

    captured = {}

    monkeypatch.setattr(dialog, "_main_window", lambda: _Window())

    def fake_get_save_file_name(parent, title, path, file_filter):
        captured["parent"] = parent
        captured["title"] = title
        captured["path"] = path
        captured["filter"] = file_filter
        return ("", "")

    monkeypatch.setattr(_emsolution_plot_dialog.QFileDialog, "getSaveFileName", fake_get_save_file_name)

    dialog._save_button.click()

    assert captured["parent"] is dialog
    assert captured["title"] == "Save Plot Script"
    assert captured["path"] == str(tmp_path / "plot_script.py")
    assert captured["filter"] == "Python Files (*.py)"


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


def test_emsolution_plot_dialog_can_hide_plot_title():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            title="Hidden Plot",
            show_title=False,
            x_label="Rotor Angle",
        )
    )

    ax = dialog._preview.figure.axes[0]

    assert ax.get_title() == ""
    assert ax.get_xlabel() == "Rotor Angle"
    assert dialog._figure_title(dialog._all_checked_series()) == "Hidden Plot"


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


def test_emsolution_plot_dialog_generates_script_for_selected_network_series():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    descriptor = dialog._descriptor_for_item(leaf)
    assert descriptor is not None

    dialog._apply_series_style(
        descriptor,
        PlotSeriesStyle(label="Custom Current", line_style="--", marker="o", line_width=2.5, color="#ff0000"),
    )
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key="position",
            title="Custom Plot",
            x_label="Rotor Angle",
            y_label="Response",
            legend_mode="best",
            grid_mode="off",
        )
    )

    script = dialog._generate_script_text()

    assert "from matplotlib.figure import Figure" in script
    assert "from pyemsi import EMSolutionOutput, gui" in script
    assert "result = EMSolutionOutput.from_file('output.json')" in script
    assert "x_values = result.position" in script
    assert "y_values_1 = result.network.elements[0].current" in script
    assert "label='Custom Current'" in script
    assert "linestyle='--'" in script
    assert "marker='o'" in script
    assert "linewidth=2.5" in script
    assert "color='#ff0000'" in script
    assert "ax.set_title('Custom Plot')" in script
    assert "ax.set_xlabel('Rotor Angle')" in script
    assert "ax.set_ylabel('Response')" in script
    assert "ax.grid(False)" in script


def test_emsolution_output_plot_builder_dialog_uses_source_file_name_in_script(tmp_path):
    _app()
    path = tmp_path / "motor-output.json"
    path.write_text(json.dumps(_positive_payload()), encoding="utf-8")

    dialog = EMSolutionOutputPlotBuilderDialog(path)

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)

    script = dialog._generate_script_text()

    assert "result = EMSolutionOutput.from_file('motor-output.json')" in script
    assert str(path) not in script
    assert "plt.show()" not in script


def test_emsolution_plot_dialog_generates_script_without_plot_title_when_hidden():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key="position",
            title="Hidden Plot",
            show_title=False,
            x_label="Rotor Angle",
        )
    )

    script = dialog._generate_script_text()

    assert "ax.set_title(" not in script
    assert "fig.suptitle(" not in script
    assert "gui.add_figure(fig, 'Hidden Plot')" in script


def test_emsolution_plot_dialog_generates_script_for_mixed_series():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_rich_payload()))

    network_leaf = _find_item_by_path(dialog._tree, ["Network", "Coil #3", "Current"])
    force_leaf = _find_item_by_path(dialog._tree, ["Force Nodal", "Property #12", "Force Y"])
    network_leaf.setCheckState(0, Qt.CheckState.Checked)
    force_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key="time",
            title="Mixed Plot",
            legend_mode="upper left",
            grid_mode="major",
            x_log_scale=True,
            y_log_scale=True,
        )
    )

    script = dialog._generate_script_text()

    assert "x_values = result.time" in script
    assert "y_values_1 = result.network.elements[0].current" in script
    assert "y_values_2 = result.force_nodal.entries[0].force_y" in script
    assert "ax.set_xscale('log')" in script
    assert "ax.set_yscale('log')" in script
    assert "positive_x = x_values[x_values > 0]" in script
    assert "ax.legend(loc='upper left')" in script
    assert "ax.grid(True, axis='both', which='major')" in script
    assert "ax.set_title('Mixed Plot')" in script
    assert "gui.add_figure(fig, 'Mixed Plot')" in script


def test_emsolution_plot_dialog_only_shows_style_button_for_checked_leaf():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    leaf = _first_leaf(dialog._tree.topLevelItem(0))
    assert dialog._tree.itemWidget(leaf, dialog.SETTINGS_COLUMN) is None

    leaf.setCheckState(0, Qt.CheckState.Checked)
    button = dialog._tree.itemWidget(leaf, dialog.SETTINGS_COLUMN)

    assert isinstance(button, QPushButton)
    assert button.text() == ""
    assert not button.icon().isNull()
    assert button.maximumHeight() == dialog._style_button_max_height(leaf)

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


def test_plot_settings_dialog_round_trips_hidden_title_setting():
    _app()
    result = EMSolutionOutput.from_dict(_positive_payload())
    x_options = {option.key: option for option in result.get_plot_x_options()}
    x_axis_key = next(iter(x_options))

    dialog = PlotSettingsDialog(
        x_options,
        PlotDialogSettings(
            x_axis_key=x_axis_key,
            title="Hidden Plot",
            show_title=False,
        ),
        default_title="Default Title",
        default_x_label="Default X",
        default_y_label="Default Y",
    )

    settings = dialog.settings()

    assert settings.title == "Hidden Plot"
    assert settings.show_title is False
    assert dialog._title_edit.isEnabled() is False


def test_plot_settings_dialog_defaults_shared_x_on_for_multiple_subplots():
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
        has_multiple_subplots=True,
    )

    settings = dialog.settings()

    assert settings.share_x is True
    assert dialog._share_x_checkbox.isEnabled() is True


def test_plot_settings_dialog_disables_shared_x_for_single_subplot():
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
        has_multiple_subplots=False,
    )

    assert dialog._share_x_checkbox.isEnabled() is False


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
            self.subplotYLabelApplied = _Signal()
            self.subplotYLabelCanceled = _Signal()

        def exec(self):
            self.settingsApplied.emit(changed)
            self.settingsCanceled.emit(original)
            self.subplotYLabelApplied.emit(changed.y_label)
            self.subplotYLabelCanceled.emit(original.y_label)
            return QDialog.DialogCode.Rejected

        def settings(self):
            return changed

        def subplot_y_label(self):
            return changed.y_label

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


def test_emsolution_plot_dialog_initializes_subplot_controls():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    assert dialog._subplot_combo.count() == 2
    assert dialog._subplot_combo.itemText(0) == "1"
    assert dialog._subplot_combo.itemData(0) == 0
    assert dialog._subplot_combo.itemText(1) == "Add New Subplot..."
    assert dialog._subplot_combo.itemData(1) == dialog.ADD_SUBPLOT_DATA
    assert dialog._subplot_combo.currentIndex() == 0
    assert dialog._delete_subplot_button.isEnabled() is False


def test_emsolution_plot_dialog_restores_tree_selection_when_switching_subplots():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)

    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)

    assert len(dialog._subplots) == 2
    assert dialog._active_subplot_index == 1
    assert dialog._subplot_combo.currentText() == "2"
    assert first_leaf.checkState(0) == Qt.CheckState.Unchecked

    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._subplot_combo.setCurrentIndex(0)

    assert dialog._active_subplot_index == 0
    assert first_leaf.checkState(0) == Qt.CheckState.Checked
    assert second_leaf.checkState(0) == Qt.CheckState.Unchecked

    dialog._subplot_combo.setCurrentIndex(1)

    assert dialog._active_subplot_index == 1
    assert first_leaf.checkState(0) == Qt.CheckState.Unchecked
    assert second_leaf.checkState(0) == Qt.CheckState.Checked


def test_emsolution_plot_dialog_deletes_current_subplot_and_restores_remaining_state():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    first_leaf = _first_leaf(dialog._tree.topLevelItem(0))
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)

    second_leaf = dialog._tree.topLevelItem(0).child(0).child(1)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._delete_subplot_button.click()

    assert len(dialog._subplots) == 1
    assert dialog._active_subplot_index == 0
    assert dialog._subplot_combo.count() == 2
    assert dialog._subplot_combo.currentText() == "1"
    assert dialog._delete_subplot_button.isEnabled() is False
    assert first_leaf.checkState(0) == Qt.CheckState.Checked
    assert second_leaf.checkState(0) == Qt.CheckState.Unchecked


def test_emsolution_plot_dialog_renders_vertical_subplots_for_each_subplot_selection():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)

    axes = dialog._preview.figure.axes

    assert len(axes) == 2
    assert axes[0].get_shared_x_axes().joined(axes[0], axes[1])
    assert len(axes[0].lines) == 1
    assert len(axes[1].lines) == 1
    assert axes[0].get_legend_handles_labels()[1] == ["Coil #3 Current"]
    assert axes[1].get_legend_handles_labels()[1] == ["Coil #3 Voltage"]


def test_emsolution_plot_dialog_can_disable_shared_x_for_multiple_subplots():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            share_x=False,
        )
    )

    axes = dialog._preview.figure.axes

    assert len(axes) == 2
    assert not axes[0].get_shared_x_axes().joined(axes[0], axes[1])


def test_emsolution_plot_dialog_uses_subplot_specific_y_labels():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_sample_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            y_label="Current Response",
        )
    )

    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key=dialog._plot_settings.x_axis_key,
            y_label="Voltage Response",
        )
    )

    axes = dialog._preview.figure.axes

    assert axes[0].get_ylabel() == "Current Response"
    assert axes[1].get_ylabel() == "Voltage Response"


def test_emsolution_plot_dialog_generates_script_for_multiple_vertical_subplots():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key="position",
            title="Stacked Plot",
            x_label="Rotor Angle",
            y_label="Current Response",
            legend_mode="best",
            grid_mode="off",
        )
    )

    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key="position",
            title="Stacked Plot",
            x_label="Rotor Angle",
            y_label="Voltage Response",
            legend_mode="best",
            grid_mode="off",
        )
    )

    script = dialog._generate_script_text()

    assert "axes = fig.subplots(2, 1, sharex=True, squeeze=False)" in script
    assert "ax_1 = axes[0][0]" in script
    assert "ax_2 = axes[1][0]" in script
    assert "y_values_1_1 = result.network.elements[0].current" in script
    assert "y_values_2_1 = result.network.elements[0].voltage" in script
    assert "ax_1.label_outer()" in script
    assert "fig.suptitle('Stacked Plot')" in script
    assert "ax_2.set_xlabel('Rotor Angle')" in script
    assert "ax_1.set_ylabel('Current Response')" in script
    assert "ax_2.set_ylabel('Voltage Response')" in script
    assert "gui.add_figure(fig, 'Stacked Plot')" in script


def test_emsolution_plot_dialog_generates_script_without_shared_x_when_disabled():
    _app()
    dialog = EMSolutionPlotDialog(EMSolutionOutput.from_dict(_positive_payload()))

    top = dialog._tree.topLevelItem(0)
    first_leaf = _first_leaf(top)
    second_leaf = top.child(0).child(1)
    first_leaf.setCheckState(0, Qt.CheckState.Checked)
    add_index = _find_combo_index_by_data(dialog._subplot_combo, dialog.ADD_SUBPLOT_DATA)
    dialog._subplot_combo.setCurrentIndex(add_index)
    second_leaf.setCheckState(0, Qt.CheckState.Checked)
    dialog._apply_plot_settings(
        PlotDialogSettings(
            x_axis_key="position",
            title="Stacked Plot",
            share_x=False,
        )
    )

    script = dialog._generate_script_text()

    assert "axes = fig.subplots(2, 1, sharex=False, squeeze=False)" in script
    assert "label_outer()" not in script
