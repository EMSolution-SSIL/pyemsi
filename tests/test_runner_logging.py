from __future__ import annotations

import sys
from types import SimpleNamespace

from pyemsi.tools import run_femap_converter, run_source_to_femap


class _FakeLogger:
    def __init__(self) -> None:
        self.info_messages: list[str] = []
        self.exception_messages: list[str] = []

    def info(self, message: str, *args) -> None:
        self.info_messages.append(message % args if args else message)

    def exception(self, message: str, *args) -> None:
        self.exception_messages.append(message % args if args else message)


def test_run_source_to_femap_main_uses_package_logger(monkeypatch):
    fake_logger = _FakeLogger()
    config = SimpleNamespace(source_format="atlas", input_dir="C:/input")

    monkeypatch.setattr(sys, "argv", ["run_source_to_femap.py", "--config", "config.json"])
    monkeypatch.setattr(run_source_to_femap, "LOGGER", fake_logger)
    monkeypatch.setattr(run_source_to_femap, "_load_config", lambda path: {"input_dir": "C:/input"})
    monkeypatch.setattr(run_source_to_femap, "load_source_to_femap_config", lambda payload: config)
    monkeypatch.setattr(run_source_to_femap, "convert_source_to_femap", lambda value: ["C:/output"])
    monkeypatch.setattr(run_source_to_femap.pyemsi, "configure_logging", lambda level: None)

    run_source_to_femap.main()

    assert fake_logger.info_messages == [
        "Running atlas to FEMAP conversion for C:/input",
        "Source-to-FEMAP conversion completed: ['C:/output']",
    ]


def test_run_femap_converter_main_uses_package_logger(monkeypatch):
    fake_logger = _FakeLogger()
    captured = {}

    class _FakeConverter:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

        def run(self) -> None:
            captured["ran"] = True

    monkeypatch.setattr(sys, "argv", ["run_femap_converter.py", "--config", "config.json"])
    monkeypatch.setattr(run_femap_converter, "LOGGER", fake_logger)
    monkeypatch.setattr(run_femap_converter, "_load_config", lambda path: {"input_dir": "C:/input"})
    monkeypatch.setattr(run_femap_converter, "FemapConverter", _FakeConverter)
    monkeypatch.setattr(run_femap_converter.pyemsi, "configure_logging", lambda level: None)

    run_femap_converter.main()

    assert captured["input_dir"] == "C:/input"
    assert captured["ran"] is True
    assert fake_logger.info_messages == [
        "Running FemapConverter for C:/input",
        "FemapConverter run completed",
    ]
