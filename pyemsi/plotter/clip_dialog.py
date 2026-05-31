"""Clip dialog for actor-based PyVista plane clipping."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    import pyvista as pv
    from pyvistaqt import QtInteractor

    from pyemsi.plotter.qt_window import QtPlotterWindow

ClipState = dict[str, object]


class ClipDialog(QDialog):
    """Non-modal dialog for editing a single GUI clip plane."""

    def __init__(self, plotter: "QtInteractor | pv.Plotter", plotter_window: "QtPlotterWindow") -> None:
        self.plotter = plotter
        self.plotter_window = plotter_window
        self.parent_plotter = plotter_window.parent_plotter
        super().__init__(plotter_window._window)

        if self.parent_plotter is None:
            raise ValueError("Parent plotter is required for clipping.")

        self._clip_actor_datasets: dict[str, "pv.DataSet"] = {}
        self._active_clip_state: ClipState | None = None
        self._open_clip_state: ClipState | None = None
        self._updating_fields = False
        self._updating_actor_list = False
        self._updating_plane_widget = False
        self._applying_clip = False
        self._finished = False

        self.setWindowTitle("Clip")
        self.setWindowIcon(QIcon(":/icons/Clip.svg"))
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.resize(520, 430)

        self._create_ui()
        self.open_for_editing()

    @property
    def has_active_clip(self) -> bool:
        """Return whether this dialog owns an active GUI clip."""
        return self._active_clip_state is not None

    def open_for_editing(self) -> None:
        """Prepare the dialog and plane widget for a new edit session."""
        self._finished = False
        self._open_clip_state = self._copy_state(self._active_clip_state)
        initial_state = self._copy_state(self._active_clip_state) or self._default_clip_state()
        self._set_fields(
            initial_state["normal"],
            initial_state["origin"],
            bool(initial_state["crinkle"]),
            bool(initial_state["invert"]),
        )
        self._refresh_actor_list(initial_state)
        initial_state = self._current_state()
        self._replace_plane_widget(initial_state["normal"], initial_state["origin"])
        self._apply_clip_state(initial_state, render=True)

    def reapply_after_scene_rebuild(self) -> None:
        """Re-cache rebuilt actor sources and reapply the active GUI clip."""
        if self._active_clip_state is None:
            return
        state = self._copy_state(self._active_clip_state)
        self._clip_actor_datasets.clear()
        self._refresh_actor_list(state)
        state = self._current_state()
        self._apply_clip_state(state, render=True)

    def _create_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        main_layout.addWidget(self._create_options_row())
        main_layout.addWidget(self._create_plane_group())

        self._actor_group = self._create_actor_group()
        main_layout.addWidget(self._actor_group)

        self.button_box = QDialogButtonBox()
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.remove_button = QPushButton("Remove Clips")
        self.button_box.addButton(self.remove_button, QDialogButtonBox.ButtonRole.DestructiveRole)

        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self._on_cancel)
        self.remove_button.clicked.connect(self._on_remove_clips)
        main_layout.addWidget(self.button_box)

    def _create_options_row(self) -> QWidget:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._crinkle_checkbox = QCheckBox("Crinkle")
        self._crinkle_checkbox.toggled.connect(self._on_clip_control_changed)

        self._invert_checkbox = QCheckBox("Invert")
        self._invert_checkbox.toggled.connect(self._on_clip_control_changed)

        layout.addWidget(QLabel("Options", row))
        layout.addWidget(self._crinkle_checkbox)
        layout.addWidget(self._invert_checkbox)
        layout.addStretch(1)
        return row

    def _create_plane_group(self) -> QGroupBox:
        group = QGroupBox("Plane", self)
        grid = QGridLayout(group)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        for col, axis in enumerate(("X", "Y", "Z"), start=1):
            label = QLabel(axis, group)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(label, 0, col)

        self._normal_spins = self._create_vector_spin_row(grid, 1, "Normal", group)
        self._origin_spins = self._create_vector_spin_row(grid, 2, "Origin", group)

        return group

    def _create_vector_spin_row(
        self,
        grid: QGridLayout,
        row: int,
        title: str,
        parent: QWidget,
    ) -> dict[str, QDoubleSpinBox]:
        label = QLabel(title, parent)
        grid.addWidget(label, row, 0)

        spins: dict[str, QDoubleSpinBox] = {}
        for col, axis in enumerate(("x", "y", "z"), start=1):
            spin = QDoubleSpinBox(parent)
            spin.setDecimals(12)
            spin.setRange(-1e100, 1e100)
            spin.setSingleStep(0.1)
            spin.setKeyboardTracking(False)
            spin.valueChanged.connect(self._on_clip_control_changed)
            spins[axis] = spin
            grid.addWidget(spin, row, col)

        return spins

    def _create_actor_group(self) -> QGroupBox:
        group = QGroupBox("Clip Actors", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        button_row = QWidget(group)
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(6)

        self.select_all_button = QPushButton("All", button_row)
        self.select_none_button = QPushButton("None", button_row)
        self.invert_selection_button = QPushButton("Invert", button_row)
        self._actor_count_label = QLabel("0 / 0 selected", button_row)

        self.select_all_button.clicked.connect(self._on_select_all_actors)
        self.select_none_button.clicked.connect(self._on_select_no_actors)
        self.invert_selection_button.clicked.connect(self._on_invert_actor_selection)

        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.select_none_button)
        button_layout.addWidget(self.invert_selection_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self._actor_count_label)
        layout.addWidget(button_row)

        self._actor_list = QListWidget(group)
        self._actor_list.setMinimumHeight(120)
        self._actor_list.setMaximumHeight(170)
        self._actor_list.itemChanged.connect(self._on_actor_selection_changed)
        layout.addWidget(self._actor_list)

        return group

    def _vector_values(self, spins: dict[str, object]) -> tuple[float, float, float]:
        return (
            float(spins["x"].value()),
            float(spins["y"].value()),
            float(spins["z"].value()),
        )

    def _current_state(self) -> ClipState:
        return {
            "normal": self._vector_values(self._normal_spins),
            "origin": self._vector_values(self._origin_spins),
            "crinkle": self._crinkle_checkbox.isChecked(),
            "invert": self._invert_checkbox.isChecked(),
            "actor_names": self._selected_actor_names(),
            "available_actor_names": self._current_actor_names(),
        }

    def _default_clip_state(self) -> ClipState:
        bounds = self.parent_plotter.mesh.bounds
        origin = (
            float((bounds[0] + bounds[1]) / 2),
            float((bounds[2] + bounds[3]) / 2),
            float((bounds[4] + bounds[5]) / 2),
        )
        return {
            "normal": (0.0, 0.0, 1.0),
            "origin": origin,
            "crinkle": False,
            "invert": True,
            "actor_names": self._current_actor_names(),
            "available_actor_names": self._current_actor_names(),
        }

    def _copy_state(self, state: ClipState | None) -> ClipState | None:
        if state is None:
            return None
        return {
            "normal": tuple(state["normal"]),
            "origin": tuple(state["origin"]),
            "crinkle": bool(state["crinkle"]),
            "invert": bool(state["invert"]),
            "actor_names": tuple(state.get("actor_names", ())),
            "available_actor_names": tuple(state.get("available_actor_names", state.get("actor_names", ()))),
        }

    def _set_fields(self, normal, origin, crinkle: bool, invert: bool) -> None:
        self._updating_fields = True
        try:
            for spins, values in ((self._normal_spins, normal), (self._origin_spins, origin)):
                for axis, value in zip(("x", "y", "z"), values):
                    spins[axis].setValue(float(value))
            self._crinkle_checkbox.setChecked(bool(crinkle))
            self._invert_checkbox.setChecked(bool(invert))
        finally:
            self._updating_fields = False

    def _replace_plane_widget(self, normal, origin) -> None:
        self._updating_plane_widget = True
        try:
            self._clear_plane_widget()
            self.plotter.add_plane_widget(
                self._on_plane_changed,
                normal=normal,
                origin=origin,
                bounds=self.parent_plotter.mesh.bounds,
                color="cyan",
                outline_translation=True,
                origin_translation=True,
                normal_rotation=True,
                interaction_event="always",
                test_callback=False,
            )
        finally:
            self._updating_plane_widget = False

    def _clear_plane_widget(self) -> None:
        try:
            self.plotter.clear_plane_widgets()
        except AttributeError:
            pass

    def _iter_clip_actors(self):
        import pyvista as pv

        actors = getattr(self.plotter, "actors", {})
        for actor_name, actor in list(actors.items()):
            if not isinstance(actor, pv.Actor):
                continue
            mapper = getattr(actor, "mapper", None)
            dataset = getattr(mapper, "dataset", None)
            if mapper is None or dataset is None:
                continue
            yield str(actor_name), actor, mapper, dataset

    def _current_actor_names(self) -> tuple[str, ...]:
        return tuple(actor_name for actor_name, _actor, _mapper, _dataset in self._iter_clip_actors())

    def _selected_actor_names(self) -> tuple[str, ...]:
        selected: list[str] = []
        for row in range(self._actor_list.count()):
            item = self._actor_list.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return tuple(selected)

    def _refresh_actor_list(self, state: ClipState | None) -> None:
        current_names = self._current_actor_names()
        if state is None:
            selected_names = set(current_names)
            known_names = set()
        else:
            selected_names = set(state.get("actor_names", current_names))
            known_names = set(state.get("available_actor_names", state.get("actor_names", ())))

        self._updating_actor_list = True
        try:
            self._actor_list.clear()
            for actor_name in current_names:
                item = QListWidgetItem(actor_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                checked = actor_name in selected_names or actor_name not in known_names
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
                self._actor_list.addItem(item)
        finally:
            self._updating_actor_list = False
        self._update_actor_count_label()

    def _cache_actor_datasets(self) -> None:
        current_names = set()
        for actor_name, _actor, _mapper, dataset in self._iter_clip_actors():
            current_names.add(actor_name)
            if actor_name not in self._clip_actor_datasets:
                self._clip_actor_datasets[actor_name] = dataset

        for stale_name in set(self._clip_actor_datasets) - current_names:
            self._clip_actor_datasets.pop(stale_name, None)

    def _restore_actor_datasets(self, render: bool) -> None:
        for actor_name, _actor, mapper, _dataset in self._iter_clip_actors():
            original = self._clip_actor_datasets.get(actor_name)
            if original is None:
                continue
            mapper.SetInputDataObject(original)
            mapper.Modified()
        if render:
            self.plotter.render()

    def _apply_clip_state(self, state: ClipState, render: bool) -> None:
        if self._applying_clip:
            return

        self._applying_clip = True
        try:
            self._restore_actor_datasets(render=False)
            self._cache_actor_datasets()

            normal = state["normal"]
            origin = state["origin"]
            crinkle = bool(state["crinkle"])
            invert = bool(state["invert"])
            selected_actor_names = set(state.get("actor_names", ()))

            for actor_name, _actor, mapper, dataset in self._iter_clip_actors():
                if actor_name not in selected_actor_names:
                    continue
                source = self._clip_actor_datasets.get(actor_name, dataset)
                clipped = source.clip(normal=normal, origin=origin, invert=invert, crinkle=crinkle)
                mapper.SetInputDataObject(clipped)
                mapper.Modified()

            self._active_clip_state = self._copy_state(state)
            self._sync_remove_button()
            if render:
                self.plotter.render()
        finally:
            self._applying_clip = False

    def _sync_remove_button(self) -> None:
        self.remove_button.setEnabled(self._active_clip_state is not None or bool(self._clip_actor_datasets))

    def _update_actor_count_label(self) -> None:
        total = self._actor_list.count()
        selected = len(self._selected_actor_names())
        self._actor_count_label.setText(f"{selected} / {total} selected")

    def _on_plane_changed(self, normal, origin) -> None:
        if self._finished or self._updating_fields or self._updating_plane_widget:
            return
        self._set_fields(normal, origin, self._crinkle_checkbox.isChecked(), self._invert_checkbox.isChecked())
        state = self._current_state()
        self._apply_clip_state(state, render=True)

    def _on_clip_control_changed(self, *_args) -> None:
        if self._finished or self._updating_fields:
            return
        state = self._current_state()
        self._replace_plane_widget(state["normal"], state["origin"])
        self._apply_clip_state(state, render=True)

    def _on_actor_selection_changed(self, _item) -> None:
        if self._finished or self._updating_actor_list:
            return
        self._update_actor_count_label()
        self._apply_clip_state(self._current_state(), render=True)

    def _on_select_all_actors(self) -> None:
        self._set_all_actor_checks(Qt.CheckState.Checked)

    def _on_select_no_actors(self) -> None:
        self._set_all_actor_checks(Qt.CheckState.Unchecked)

    def _on_invert_actor_selection(self) -> None:
        self._updating_actor_list = True
        try:
            for row in range(self._actor_list.count()):
                item = self._actor_list.item(row)
                new_state = (
                    Qt.CheckState.Unchecked
                    if item.checkState() == Qt.CheckState.Checked
                    else Qt.CheckState.Checked
                )
                item.setCheckState(new_state)
        finally:
            self._updating_actor_list = False
        self._update_actor_count_label()
        self._apply_clip_state(self._current_state(), render=True)

    def _set_all_actor_checks(self, check_state: Qt.CheckState) -> None:
        self._updating_actor_list = True
        try:
            for row in range(self._actor_list.count()):
                self._actor_list.item(row).setCheckState(check_state)
        finally:
            self._updating_actor_list = False
        self._update_actor_count_label()
        self._apply_clip_state(self._current_state(), render=True)

    def _on_ok(self) -> None:
        self._finished = True
        self._clear_plane_widget()
        self.accept()

    def _on_cancel(self) -> None:
        self._finished = True
        self._restore_open_state()
        self._clear_plane_widget()
        self.reject()

    def _restore_open_state(self) -> None:
        if self._open_clip_state is None:
            self._active_clip_state = None
            self._restore_actor_datasets(render=True)
            self._clip_actor_datasets.clear()
            self._refresh_actor_list(self._default_clip_state())
            self._sync_remove_button()
            return
        self._refresh_actor_list(self._open_clip_state)
        restored_state = self._copy_state(self._open_clip_state)
        restored_state["actor_names"] = self._selected_actor_names()
        restored_state["available_actor_names"] = self._current_actor_names()
        self._apply_clip_state(restored_state, render=True)

    def _on_remove_clips(self) -> None:
        self._active_clip_state = None
        self._open_clip_state = None
        self._restore_actor_datasets(render=True)
        self._clip_actor_datasets.clear()
        self._clear_plane_widget()
        default_state = self._default_clip_state()
        self._refresh_actor_list(default_state)
        self._set_fields(
            default_state["normal"],
            default_state["origin"],
            bool(default_state["crinkle"]),
            bool(default_state["invert"]),
        )
        self._sync_remove_button()

    def closeEvent(self, event) -> None:
        if not self._finished:
            self._finished = True
            self._restore_open_state()
            self._clear_plane_widget()
        super().closeEvent(event)
