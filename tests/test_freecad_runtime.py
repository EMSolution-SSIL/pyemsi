from __future__ import annotations

import os
import types

import pytest

from pyemsi.gui import freecad_runtime


def _make_prefix(tmp_path, *subdirs):
    prefix = tmp_path / "env"
    prefix.mkdir(exist_ok=True)
    for sub in subdirs:
        (prefix / sub).mkdir(parents=True)
    return str(prefix)


def _fake_module(name, file):
    mod = types.ModuleType(name)
    mod.__file__ = file
    return mod


def test_search_paths_only_returns_existing_dirs_inside_prefix(tmp_path):
    prefix = _make_prefix(tmp_path, "Library/bin", "Library/Mod")

    paths = freecad_runtime.freecad_search_paths(prefix)

    assert paths == [
        os.path.normpath(os.path.join(prefix, "Library", "bin")),
        os.path.normpath(os.path.join(prefix, "Library", "Mod")),
    ]
    assert all(p.startswith(prefix) for p in paths)


def test_search_paths_defaults_to_sys_prefix(monkeypatch, tmp_path):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime.sys, "prefix", prefix)

    assert freecad_runtime.freecad_search_paths() == [os.path.normpath(os.path.join(prefix, "Library", "bin"))]


def test_prepare_paths_is_idempotent_and_registers_dll_dir_once(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin", "Library/Mod")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())
    monkeypatch.setattr(freecad_runtime, "_dll_handles", [])
    sys_path: list[str] = ["already"]
    dll_calls: list[str] = []

    first = freecad_runtime.prepare_freecad_paths(prefix, sys_path=sys_path, dll_adder=dll_calls.append)
    second = freecad_runtime.prepare_freecad_paths(prefix, sys_path=sys_path, dll_adder=dll_calls.append)

    assert first == second
    assert sys_path == ["already", *first]
    assert dll_calls == [os.path.normpath(os.path.join(prefix, "Library", "bin"))]


def test_prepare_paths_raises_clear_error_when_no_freecad_dirs(tmp_path):
    prefix = _make_prefix(tmp_path)

    with pytest.raises(freecad_runtime.FreeCADRuntimeError) as excinfo:
        freecad_runtime.prepare_freecad_paths(prefix, sys_path=[], dll_adder=lambda p: None)

    message = str(excinfo.value)
    assert "FreeCAD could not be initialized" in message
    assert prefix in message


def test_import_freecad_returns_modules_from_active_prefix(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())
    bin_dir = os.path.join(prefix, "Library", "bin")
    modules = {
        "FreeCAD": _fake_module("FreeCAD", os.path.join(bin_dir, "FreeCAD.pyd")),
        "FreeCADGui": _fake_module("FreeCADGui", os.path.join(bin_dir, "FreeCADGui.pyd")),
    }

    result = freecad_runtime.import_freecad(prefix, importer=modules.__getitem__, sys_path=[], dll_adder=lambda p: None)

    assert result.app is modules["FreeCAD"]
    assert result.gui is modules["FreeCADGui"]


def test_import_freecad_reports_missing_module_with_diagnostics(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())

    def _importer(name):
        raise ModuleNotFoundError(f"No module named '{name}'")

    with pytest.raises(freecad_runtime.FreeCADRuntimeError) as excinfo:
        freecad_runtime.import_freecad(prefix, importer=_importer, sys_path=[], dll_adder=lambda p: None)

    message = str(excinfo.value)
    assert "No module named 'FreeCAD'" in message
    assert freecad_runtime.sys.executable in message
    assert os.path.join("Library", "bin") in message


def test_import_freecad_rejects_module_outside_prefix(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())
    elsewhere = str(tmp_path / "other" / "FreeCAD.pyd")
    modules = {
        "FreeCAD": _fake_module("FreeCAD", elsewhere),
        "FreeCADGui": _fake_module("FreeCADGui", elsewhere),
    }

    with pytest.raises(freecad_runtime.FreeCADRuntimeError) as excinfo:
        freecad_runtime.import_freecad(prefix, importer=modules.__getitem__, sys_path=[], dll_adder=lambda p: None)

    assert "outside the active environment" in str(excinfo.value)
