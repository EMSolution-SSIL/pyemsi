from __future__ import annotations

import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class AudioViewer(QWidget):
    """Audio player with play/pause, seek slider, and time display."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._name_label = QLabel()
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._play_btn = QPushButton("Play")
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._time_label = QLabel("0:00 / 0:00")

        controls = QHBoxLayout()
        controls.addWidget(self._play_btn)
        controls.addWidget(self._slider, 1)
        controls.addWidget(self._time_label)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self._name_label)
        layout.addLayout(controls)
        layout.addStretch()

        self._play_btn.clicked.connect(self._toggle_playback)
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._slider.sliderMoved.connect(self._player.setPosition)

    def load_file(self, path: str) -> None:
        self._name_label.setText(os.path.basename(path))
        self._player.setSource(QUrl.fromLocalFile(path))

    def _toggle_playback(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _on_state_changed(self, state) -> None:
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._play_btn.setText("Pause")
        else:
            self._play_btn.setText("Play")

    def _on_position_changed(self, position: int) -> None:
        if not self._slider.isSliderDown():
            self._slider.setValue(position)
        duration = self._player.duration()
        self._time_label.setText(f"{self._format_time(position)} / {self._format_time(duration)}")

    def _on_duration_changed(self, duration: int) -> None:
        self._slider.setRange(0, duration)

    @staticmethod
    def _format_time(ms: int) -> str:
        total_seconds = max(ms, 0) // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
