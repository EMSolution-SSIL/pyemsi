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
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
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
        self._finished = False
        self._removed_without_apply = False

        self.setWindowTitle("Clip")
        self.setWindowIcon(QIcon(":/icons/Clip.svg"))
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.resize(430, 290)

        self._create_ui()
        self.open_for_editing()

    @property
    def has_active_clip(self) -> bool:
        """Return whether this dialog owns an active GUI clip."""
        return self._active_clip_state is not None

    def open_for_editing(self) -> None:
        """Prepare the dialog and plane widget for a new edit session."""
        self._finished = False
        self._removed_without_apply = False
        self._open_clip_state = self._copy_state(self._active_clip_state)
        initial_state = self._copy_state(self._active_clip_state) or self._default_clip_state()
        self._set_fields(
            initial_state["normal"],
            initial_state["origin"],
            bool(initial_state["crinkle"]),
            bool(initial_state["invert"]),
        )
        self._replace_plane_widget(initial_state["normal"], initial_state["origin"])
        self._sync_remove_button()

    def reapply_after_scene_rebuild(self) -> None:
        """Re-cache rebuilt actor sources and reapply the active GUI clip."""
        if self._active_clip_state is None:
            return
        state = self._copy_state(self._active_clip_state)
        self._clip_actor_datasets.clear()
        self._apply_clip_state(state, render=True)

    def _create_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self._crinkle_checkbox = QCheckBox("Crinkle")
        main_layout.addWidget(self._crinkle_checkbox)

        self._invert_checkbox = QCheckBox("Invert")
        main_layout.addWidget(self._invert_checkbox)

        self._normal_spins = self._create_vector_group("Normal")
        main_layout.addWidget(self._normal_spins["group"])

        self._origin_spins = self._create_vector_group("Origin")
        main_layout.addWidget(self._origin_spins["group"])

        self.button_box = QDialogButtonBox()
        self.apply_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Apply)
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.remove_button = QPushButton("Remove Clips")
        self.button_box.addButton(self.remove_button, QDialogButtonBox.ButtonRole.DestructiveRole)

        self.apply_button.clicked.connect(self._on_apply)
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self._on_cancel)
        self.remove_button.clicked.connect(self._on_remove_clips)
        main_layout.addWidget(self.button_box)

    def _create_vector_group(self, title: str) -> dict[str, object]:
        group = QGroupBox(title, self)
        form_layout = QFormLayout(group)

        row = QWidget(group)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        spins: dict[str, QDoubleSpinBox] = {}
        for axis in ("x", "y", "z"):
            row_layout.addWidget(QLabel(axis.upper(), row))
            spin = QDoubleSpinBox(row)
            spin.setDecimals(12)
            spin.setRange(-1e100, 1e100)
            spin.setSingleStep(0.1)
            spin.setKeyboardTracking(False)
            spins[axis] = spin
            row_layout.addWidget(spin, 1)

        form_layout.addRow(row)
        return {"group": group, **spins}

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
        }

    def _copy_state(self, state: ClipState | None) -> ClipState | None:
        if state is None:
            return None
        return {
            "normal": tuple(state["normal"]),
            "origin": tuple(state["origin"]),
            "crinkle": bool(state["crinkle"]),
            "invert": bool(state["invert"]),
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
        self._restore_actor_datasets(render=False)
        self._cache_actor_datasets()

        normal = state["normal"]
        origin = state["origin"]
        crinkle = bool(state["crinkle"])
        invert = bool(state["invert"])

        for actor_name, _actor, mapper, dataset in self._iter_clip_actors():
            source = self._clip_actor_datasets.get(actor_name, dataset)
            clipped = source.clip(normal=normal, origin=origin, invert=invert, crinkle=crinkle)
            mapper.SetInputDataObject(clipped)
            mapper.Modified()

        self._active_clip_state = self._copy_state(state)
        self._removed_without_apply = False
        self._sync_remove_button()
        if render:
            self.plotter.render()

    def _sync_remove_button(self) -> None:
        self.remove_button.setEnabled(self._active_clip_state is not None or bool(self._clip_actor_datasets))

    def _on_plane_changed(self, normal, origin) -> None:
        if self._finished or self._updating_fields:
            return
        self._set_fields(normal, origin, self._crinkle_checkbox.isChecked(), self._invert_checkbox.isChecked())

    def _on_apply(self) -> None:
        state = self._current_state()
        self._replace_plane_widget(state["normal"], state["origin"])
        self._apply_clip_state(state, render=True)

    def _on_ok(self) -> None:
        if not self._removed_without_apply:
            state = self._current_state()
            self._apply_clip_state(state, render=True)
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
            self._sync_remove_button()
            return
        self._apply_clip_state(self._open_clip_state, render=True)

    def _on_remove_clips(self) -> None:
        self._active_clip_state = None
        self._open_clip_state = None
        self._removed_without_apply = True
        self._restore_actor_datasets(render=True)
        self._clip_actor_datasets.clear()
        self._clear_plane_widget()
        default_state = self._default_clip_state()
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
