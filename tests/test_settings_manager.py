import json
import os

from pyemsi.settings import SettingsManager


def test_settings_manager_merges_defaults_global_and_local(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    nested_workspace = workspace / "nested"
    nested_workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.set_global("workbench.window.dock_visibility", {"ipython": True})
    manager.set_global("workbench.window.maximized", True)
    manager.load_workspace(workspace)
    manager.set_local("workbench.explorer.root_path", str(nested_workspace))
    manager.save()

    reloaded = SettingsManager(global_settings_path=global_settings_path)
    reloaded.load_workspace(workspace)

    assert reloaded.get_effective("workbench.window.dock_visibility") == {
        "explorer": True,
        "external_terminal": False,
        "ipython": True,
    }
    assert reloaded.get_effective("workbench.window.maximized") is True
    assert reloaded.get_local("workbench.explorer.root_path") == os.path.abspath(
        os.path.normpath(str(nested_workspace))
    )


def test_settings_manager_falls_back_when_json_is_malformed(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    global_settings_path.parent.mkdir(parents=True)
    global_settings_path.write_text("{not valid json", encoding="utf-8")

    manager = SettingsManager(global_settings_path=global_settings_path)

    assert manager.get_effective("app.recent_folders") == []
    assert any("failed to read global settings" in warning for warning in manager.warnings)


def test_settings_manager_ignores_invalid_global_window_values(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    global_settings_path.parent.mkdir(parents=True)
    global_settings_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "workbench": {
                    "window": {
                        "dock_visibility": {"ipython": "yes"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    manager = SettingsManager(global_settings_path=global_settings_path)

    assert manager.get_effective("workbench.window.dock_visibility") == {
        "explorer": True,
        "external_terminal": False,
        "ipython": False,
    }
    assert any("ignored invalid value for workbench.window.dock_visibility" in warning for warning in manager.warnings)


def test_settings_manager_recent_folders_are_unique_and_limited_to_ten(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    manager = SettingsManager(global_settings_path=global_settings_path)

    folders = []
    for index in range(12):
        folder = tmp_path / f"workspace_{index}"
        folder.mkdir()
        folders.append(folder)
        manager.add_recent_folder(folder)

    manager.add_recent_folder(folders[5])

    recent_folders = manager.get_global("app.recent_folders")

    assert len(recent_folders) == 10
    assert recent_folders[0] == os.path.abspath(os.path.normpath(str(folders[5])))
    assert len(recent_folders) == len(set(recent_folders))
    assert os.path.abspath(os.path.normpath(str(folders[0]))) not in recent_folders
    assert os.path.abspath(os.path.normpath(str(folders[1]))) not in recent_folders


def test_settings_manager_recent_folders_filters_missing_directories(tmp_path):
    existing_folder = tmp_path / "existing"
    existing_folder.mkdir()
    missing_folder = tmp_path / "missing"
    global_settings_path = tmp_path / "config" / "settings.json"
    global_settings_path.parent.mkdir(parents=True)
    global_settings_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "app": {
                    "recent_folders": [str(existing_folder), str(missing_folder), str(existing_folder)],
                },
            }
        ),
        encoding="utf-8",
    )

    manager = SettingsManager(global_settings_path=global_settings_path)

    assert manager.get_global("app.recent_folders") == [os.path.abspath(os.path.normpath(str(existing_folder)))]


def test_settings_manager_drops_removed_legacy_settings_on_load_and_save(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"
    local_settings_path = workspace / ".pyemsi" / "workspace.json"
    global_settings_path.parent.mkdir(parents=True)
    global_settings_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "app": {
                    "last_workspace_path": str(tmp_path / "workspace"),
                    "recent_folders": [],
                },
                "workbench": {
                    "layout": {"splitter_sizes": [320, 1080]},
                    "window": {
                        "geometry": "Zm9v",
                        "state": "YmFy",
                        "state_version": 1,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    local_settings_path.parent.mkdir(parents=True)
    local_settings_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "workbench": {
                    "layout": {"splitter_sizes": [100, 200]},
                    "window": {
                        "geometry": "Zm9v",
                        "state": "YmFy",
                        "state_version": 1,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)
    manager.save()

    global_payload = json.loads(global_settings_path.read_text(encoding="utf-8"))
    local_payload = json.loads(local_settings_path.read_text(encoding="utf-8"))

    assert "last_workspace_path" not in global_payload.get("app", {})
    assert "layout" not in global_payload.get("workbench", {})
    assert "geometry" not in global_payload.get("workbench", {}).get("window", {})
    assert "state" not in global_payload.get("workbench", {}).get("window", {})
    assert "state_version" not in global_payload.get("workbench", {}).get("window", {})
    assert "layout" not in local_payload.get("workbench", {})
    assert "geometry" not in local_payload.get("workbench", {}).get("window", {})
    assert "state" not in local_payload.get("workbench", {}).get("window", {})
    assert "state_version" not in local_payload.get("workbench", {}).get("window", {})


def test_settings_manager_persists_femap_converter_values_in_local_scope(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)
    manager.set_local("tools.femap_converter.input_dir", str(workspace))
    manager.set_local("tools.femap_converter.output_dir", ".pyemsi")
    manager.set_local("tools.femap_converter.output_name", "transient")
    manager.set_local("tools.femap_converter.mesh", "post_geom")
    manager.set_local("tools.femap_converter.displacement", None)
    manager.set_local("tools.femap_converter.force_2d", True)
    manager.save()

    reloaded = SettingsManager(global_settings_path=global_settings_path)
    reloaded.load_workspace(workspace)

    assert reloaded.get_local("tools.femap_converter.input_dir") == os.path.abspath(os.path.normpath(str(workspace)))
    assert reloaded.get_local("tools.femap_converter.output_dir") == ".pyemsi"
    assert reloaded.get_local("tools.femap_converter.output_name") == "transient"
    assert reloaded.get_local("tools.femap_converter.mesh") == "post_geom"
    assert reloaded.get_local("tools.femap_converter.displacement") is None
    assert reloaded.get_local("tools.femap_converter.force_2d") is True
