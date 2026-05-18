from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from pyemsi.gui.update_checker import UpdateInfo


class UpdateAvailableDialog(QDialog):
    def __init__(self, update_info: UpdateInfo, parent=None) -> None:
        super().__init__(parent)
        self._update_info = update_info
        self.setWindowTitle("Update Available")
        self.setModal(True)

        layout = QVBoxLayout(self)

        heading = QLabel("A newer version of pyemsi is available.", self)
        heading.setWordWrap(True)
        layout.addWidget(heading)

        current_version = update_info.current_version or "Unknown"
        latest_version = update_info.latest_version or "Unknown"
        versions = QLabel(
            f"Current version: {current_version}\nLatest version: {latest_version}",
            self,
        )
        versions.setTextInteractionFlags(versions.textInteractionFlags())
        layout.addWidget(versions)

        self._button_box = QDialogButtonBox(self)
        self._view_release_button = self._button_box.addButton(
            "View Release",
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        self._remind_later_button = self._button_box.addButton(
            "Remind Me Later",
            QDialogButtonBox.ButtonRole.RejectRole,
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)
