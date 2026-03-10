"""Regression tests for GUI path normalization."""

import os

from pyemsi.widgets.split_container import _resolve_open_path


def test_resolve_open_path_returns_absolute_normalized_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    nested = tmp_path / "nested"
    nested.mkdir()

    resolved = _resolve_open_path(os.path.join("nested", ".", "..", "nested", "example.py"))

    assert resolved == os.path.normpath(str(nested / "example.py"))
    assert os.path.isabs(resolved)
