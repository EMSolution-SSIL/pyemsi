import json
import os

from pyemsi.settings import SettingsManager


def test_settings_manager_merges_defaults_global_and_local(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.set_global("app.last_workspace_path", str(workspace))
    manager.set_global("workbench.window.dock_visibility", {"ipython": True})
    manager.load_workspace(workspace)
    manager.set_local("workbench.window.dock_visibility", {"external_terminal": True})
    manager.set_local("workbench.layout.splitter_sizes", [320, 1080])
    manager.save()

    reloaded = SettingsManager(global_settings_path=global_settings_path)
    reloaded.load_workspace(workspace)

    assert reloaded.get_effective("app.last_workspace_path") == os.path.abspath(os.path.normpath(str(workspace)))
    assert reloaded.get_effective("workbench.layout.splitter_sizes") == [320, 1080]
    assert reloaded.get_effective("workbench.window.dock_visibility") == {
        "explorer": True,
        "external_terminal": True,
        "ipython": True,
    }


def test_settings_manager_falls_back_when_json_is_malformed(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    global_settings_path.parent.mkdir(parents=True)
    global_settings_path.write_text("{not valid json", encoding="utf-8")

    manager = SettingsManager(global_settings_path=global_settings_path)

    assert manager.get_effective("app.last_workspace_path") is None
    assert any("failed to read global settings" in warning for warning in manager.warnings)


def test_settings_manager_ignores_invalid_workspace_values(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"
    local_settings_path = workspace / ".pyemsi" / "workspace.json"
    local_settings_path.parent.mkdir(parents=True)
    local_settings_path.write_text(
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
    manager.load_workspace(workspace)

    assert manager.get_effective("workbench.window.dock_visibility") == {
        "explorer": True,
        "external_terminal": False,
        "ipython": False,
    }
    assert any("ignored invalid value for workbench.window.dock_visibility" in warning for warning in manager.warnings)
