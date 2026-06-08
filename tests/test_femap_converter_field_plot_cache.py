import os
from importlib import import_module

import numpy as np
import pytest

from pyemsi.settings import SettingsManager
from pyemsi.tools.FemapConverter import FemapConverter


def _configure_converter_settings(tmp_path, monkeypatch) -> os.PathLike[str]:
    settings_path = tmp_path / "config" / "settings.json"
    femap_converter_module = import_module("pyemsi.tools.FemapConverter")
    monkeypatch.setattr(
        femap_converter_module,
        "SettingsManager",
        lambda: SettingsManager(global_settings_path=settings_path),
    )
    return settings_path


def test_femap_converter_persists_field_plot_cache_entry_on_success(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    settings_path = _configure_converter_settings(tmp_path, monkeypatch)
    monkeypatch.setattr(FemapConverter, "_utc_now_timestamp", staticmethod(lambda: "2026-06-08T00:00:00Z"))
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    mesh_path = os.path.join(fixtures_dir, "simple_mesh.neu")
    output_dir = workspace / ".pyemsi"

    converter = FemapConverter(
        workspace_path=workspace,
        input_dir=fixtures_dir,
        output_dir=output_dir,
        output_name="motor",
        mesh=mesh_path,
    )
    converter.sets = {1: {"title": "Step 1", "value": 0.0}}

    def _record_metadata_only() -> None:
        converter.mesh.point_data["Point Scalar"] = np.linspace(-2.0, 4.0, converter.mesh.n_points)
        converter.mesh.cell_data["Point Vector"] = np.tile(np.array([[3.0, 4.0, 0.0]]), (converter.mesh.n_cells, 1))
        converter._update_field_plot_metadata_from_mesh(converter.mesh)

    converter.parse_data_files = lambda: None
    converter.time_stepping = _record_metadata_only
    converter.run()

    manager = SettingsManager(global_settings_path=settings_path)
    manager.load_workspace(workspace)

    cached_entries = manager.get_local("tools.field_plot.cached_pvds")
    assert len(cached_entries) == 1
    entry = cached_entries[0]
    assert entry["relative_path"] == os.path.normpath(os.path.join(".pyemsi", "motor.pvd"))
    assert entry["updated_at_utc"] == "2026-06-08T00:00:00Z"
    assert entry["mesh_length"] > 0.0
    assert entry["scalar_names"] == ["Point Scalar", "PropertyID"]
    assert entry["vector_names"] == ["Point Vector"]
    assert entry["ranges"]["Point Scalar"] == {"min": -2.0, "max": 4.0}
    assert entry["ranges"]["PropertyID"]["min"] == entry["ranges"]["PropertyID"]["max"]
    assert entry["ranges"]["Point Vector"] == {"min": 5.0, "max": 5.0}
    assert manager.get_local("tools.field_plot.selected_relative_path") == os.path.normpath(
        os.path.join(".pyemsi", "motor.pvd")
    )
    assert manager.get_local("tools.field_plot.filepath") == os.path.abspath(
        os.path.normpath(os.fspath(output_dir / "motor.pvd"))
    )


def test_femap_converter_does_not_persist_field_plot_cache_when_run_fails(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    settings_path = _configure_converter_settings(tmp_path, monkeypatch)
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    mesh_path = os.path.join(fixtures_dir, "simple_mesh.neu")

    converter = FemapConverter(
        workspace_path=workspace,
        input_dir=fixtures_dir,
        output_dir=workspace / ".pyemsi",
        output_name="motor",
        mesh=mesh_path,
    )

    converter._build_mesh = lambda *_args, **_kwargs: None
    converter.parse_data_files = lambda: None
    converter.init_pvd = lambda: None
    converter.time_stepping = lambda: (_ for _ in ()).throw(RuntimeError("time stepping failed"))

    with pytest.raises(RuntimeError, match="time stepping failed"):
        converter.run()

    manager = SettingsManager(global_settings_path=settings_path)
    manager.load_workspace(workspace)

    assert manager.get_local("tools.field_plot.cached_pvds") is None
