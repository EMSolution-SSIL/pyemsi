"""Headless JSON-backed settings manager for pyemsi."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = 1
SCOPE_GLOBAL = "global"
SCOPE_LOCAL = "local"
SCOPE_BOTH = "both"


DEFAULT_SETTINGS: dict[str, Any] = {
    "app": {
        "recent_folders": [],
    },
    "tools": {
        "femap_converter": {
            "ascii_mode": False,
            "current": "current",
            "displacement": "disp",
            "force": "force",
            "force_2d": False,
            "force_J_B": "force_J_B",
            "heat": "heat",
            "input_dir": None,
            "magnetic": "magnetic",
            "mesh": "post_geom",
            "output_dir": ".pyemsi",
            "output_name": "output",
        },
    },
    "workbench": {
        "explorer": {
            "root_path": None,
        },
        "window": {
            "dock_visibility": {
                "explorer": True,
                "external_terminal": False,
                "ipython": False,
            },
            "maximized": False,
        },
    },
}


def _copy_default(value: Any) -> Any:
    return copy.deepcopy(value)


def _normalize_optional_path(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("expected a path string or null")
    return os.path.abspath(os.path.normpath(value))


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError("expected a boolean")


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected a string or null")
    normalized = value.strip()
    return normalized or None


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("expected a string")
    return value.strip()


def _normalize_recent_folders(value: Any) -> list[str]:
    if value in (None, []):
        return []
    if not isinstance(value, list):
        raise ValueError("expected a list of path strings")

    normalized: list[str] = []
    seen_paths: set[str] = set()
    for item in value:
        path = _normalize_optional_path(item)
        if path is None or not os.path.isdir(path) or path in seen_paths:
            continue
        normalized.append(path)
        seen_paths.add(path)
        if len(normalized) == 10:
            break
    return normalized


def _normalize_dock_visibility(value: Any) -> dict[str, bool]:
    default_keys = DEFAULT_SETTINGS["workbench"]["window"]["dock_visibility"].keys()
    if not isinstance(value, dict):
        raise ValueError("expected an object")
    normalized: dict[str, bool] = {}
    for key, item in value.items():
        if key not in default_keys:
            normalized[key] = item
            continue
        normalized[key] = _normalize_bool(item)
    return normalized


@dataclass(frozen=True)
class SettingDefinition:
    default: Any
    scope: str
    validator: Callable[[Any], Any]


SETTING_DEFINITIONS: dict[str, SettingDefinition] = {
    "app.recent_folders": SettingDefinition([], SCOPE_GLOBAL, _normalize_recent_folders),
    "tools.femap_converter.ascii_mode": SettingDefinition(False, SCOPE_BOTH, _normalize_bool),
    "tools.femap_converter.current": SettingDefinition("current", SCOPE_BOTH, _normalize_optional_text),
    "tools.femap_converter.displacement": SettingDefinition("disp", SCOPE_BOTH, _normalize_optional_text),
    "tools.femap_converter.force": SettingDefinition("force", SCOPE_BOTH, _normalize_optional_text),
    "tools.femap_converter.force_2d": SettingDefinition(False, SCOPE_BOTH, _normalize_bool),
    "tools.femap_converter.force_J_B": SettingDefinition("force_J_B", SCOPE_BOTH, _normalize_optional_text),
    "tools.femap_converter.heat": SettingDefinition("heat", SCOPE_BOTH, _normalize_optional_text),
    "tools.femap_converter.input_dir": SettingDefinition(None, SCOPE_BOTH, _normalize_optional_path),
    "tools.femap_converter.magnetic": SettingDefinition("magnetic", SCOPE_BOTH, _normalize_optional_text),
    "tools.femap_converter.mesh": SettingDefinition("post_geom", SCOPE_BOTH, _normalize_text),
    "tools.femap_converter.output_dir": SettingDefinition(".pyemsi", SCOPE_BOTH, _normalize_text),
    "tools.femap_converter.output_name": SettingDefinition("output", SCOPE_BOTH, _normalize_text),
    "workbench.explorer.root_path": SettingDefinition(None, SCOPE_LOCAL, _normalize_optional_path),
    "workbench.window.dock_visibility": SettingDefinition(
        _copy_default(DEFAULT_SETTINGS["workbench"]["window"]["dock_visibility"]),
        SCOPE_GLOBAL,
        _normalize_dock_visibility,
    ),
    "workbench.window.maximized": SettingDefinition(False, SCOPE_GLOBAL, _normalize_bool),
}

_CONTAINER_PATHS = {
    "app",
    "tools",
    "tools.femap_converter",
    "workbench",
    "workbench.explorer",
    "workbench.window",
}


def get_user_config_dir(app_name: str = "pyemsi") -> Path:
    """Return a platform-appropriate configuration directory."""
    if os.name == "nt":
        base_dir = os.environ.get("APPDATA")
        if not base_dir:
            base_dir = os.path.join(Path.home(), "AppData", "Roaming")
        return Path(base_dir) / app_name

    xdg_dir = os.environ.get("XDG_CONFIG_HOME")
    if xdg_dir:
        return Path(xdg_dir) / app_name
    return Path.home() / ".config" / app_name


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = {key: copy.deepcopy(value) for key, value in base.items()}
        for key, value in override.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged
    return copy.deepcopy(override)


def _path_parts(key: str) -> list[str]:
    return key.split(".")


def _has_path(data: Any, key: str) -> bool:
    current = data
    for part in _path_parts(key):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _get_path(data: dict[str, Any], key: str, default: Any = None) -> Any:
    current: Any = data
    for part in _path_parts(key):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def _set_path(data: dict[str, Any], key: str, value: Any) -> None:
    current = data
    parts = _path_parts(key)
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {}
            current[part] = child
        current = child
    current[parts[-1]] = value


def _delete_path(data: dict[str, Any], key: str) -> None:
    current = data
    parents: list[tuple[dict[str, Any], str]] = []
    parts = _path_parts(key)
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            return
        parents.append((current, part))
        current = child
    if not isinstance(current, dict) or parts[-1] not in current:
        return
    del current[parts[-1]]
    while parents and not current:
        parent, parent_key = parents.pop()
        del parent[parent_key]
        current = parent


class SettingsManager:
    """Manage layered global and workspace-local JSON settings."""

    def __init__(self, global_settings_path: str | os.PathLike[str] | None = None) -> None:
        self._global_settings_path = (
            Path(global_settings_path) if global_settings_path else get_user_config_dir() / "settings.json"
        )
        self._workspace_path: Path | None = None
        self._global_data: dict[str, Any] = {}
        self._local_data: dict[str, Any] = {}
        self._warnings: list[str] = []
        self.load()

    @property
    def global_settings_path(self) -> Path:
        return self._global_settings_path

    @property
    def local_settings_path(self) -> Path | None:
        if self._workspace_path is None:
            return None
        return self._workspace_path / ".pyemsi" / "workspace.json"

    @property
    def workspace_path(self) -> Path | None:
        return self._workspace_path

    @property
    def warnings(self) -> list[str]:
        return list(self._warnings)

    def load(self) -> None:
        """Reload global settings and the active workspace, if any."""
        self._warnings.clear()
        self._global_data = self._read_json_file(self.global_settings_path, label="global")
        if self._workspace_path is not None:
            local_path = self.local_settings_path
            assert local_path is not None
            self._local_data = self._read_json_file(local_path, label="local")
        else:
            self._local_data = {}

    def load_workspace(self, path: str | os.PathLike[str] | None) -> None:
        """Load local settings for *path* as the active workspace."""
        if path is None:
            self._workspace_path = None
            self._local_data = {}
            return
        normalized = Path(os.path.abspath(os.path.normpath(os.fspath(path))))
        self._workspace_path = normalized
        local_path = self.local_settings_path
        assert local_path is not None
        self._local_data = self._read_json_file(local_path, label="local")

    def get_effective(self, key: str | None = None) -> Any:
        """Return merged defaults, global settings, and local settings."""
        effective = _deep_merge(DEFAULT_SETTINGS, self.get_global())
        effective = _deep_merge(effective, self.get_local())
        if key is None:
            return effective
        return _get_path(effective, key)

    def get_global(self, key: str | None = None) -> Any:
        """Return sanitized global settings."""
        sanitized = self._sanitize_scope(self._global_data, SCOPE_GLOBAL)
        if key is None:
            return sanitized
        return _get_path(sanitized, key)

    def get_local(self, key: str | None = None) -> Any:
        """Return sanitized local settings."""
        sanitized = self._sanitize_scope(self._local_data, SCOPE_LOCAL)
        if key is None:
            return sanitized
        return _get_path(sanitized, key)

    def set_global(self, key: str, value: Any) -> None:
        """Set a validated global setting."""
        self._set_value(self._global_data, SCOPE_GLOBAL, key, value)

    def set_local(self, key: str, value: Any) -> None:
        """Set a validated local setting."""
        if self._workspace_path is None:
            raise RuntimeError("cannot set local settings without an active workspace")
        self._set_value(self._local_data, SCOPE_LOCAL, key, value)

    def add_recent_folder(self, path: str | os.PathLike[str]) -> list[str]:
        """Prepend *path* to the global recent-folders list and return the result."""
        normalized_path = _normalize_optional_path(os.fspath(path))
        if normalized_path is None or not os.path.isdir(normalized_path):
            return self.get_global("app.recent_folders") or []

        current = self.get_global("app.recent_folders") or []
        updated = [normalized_path, *[item for item in current if item != normalized_path]]
        self.set_global("app.recent_folders", updated)
        return self.get_global("app.recent_folders") or []

    def clear_recent_folders(self) -> None:
        """Clear the global recent-folders list."""
        self.set_global("app.recent_folders", [])

    def reset_key(self, key: str) -> None:
        """Remove *key* from both override layers so defaults apply again."""
        _delete_path(self._global_data, key)
        _delete_path(self._local_data, key)

    def save(self) -> None:
        """Persist global settings and the active workspace settings."""
        self._global_data = self._sanitize_scope(self._global_data, SCOPE_GLOBAL)
        self._write_json_file(self.global_settings_path, self._global_data)
        if self._workspace_path is not None:
            local_path = self.local_settings_path
            assert local_path is not None
            self._local_data = self._sanitize_scope(self._local_data, SCOPE_LOCAL)
            self._write_json_file(local_path, self._local_data)

    def _warn(self, message: str) -> None:
        if message not in self._warnings:
            self._warnings.append(message)

    def _set_value(self, layer: dict[str, Any], scope: str, key: str, value: Any) -> None:
        definition = SETTING_DEFINITIONS.get(key)
        if definition is None:
            raise KeyError(f"unknown setting key: {key}")
        if definition.scope not in {scope, SCOPE_BOTH}:
            raise ValueError(f"setting {key!r} is not valid in {scope} scope")
        normalized = definition.validator(value)
        _set_path(layer, key, normalized)

    def _sanitize_scope(self, data: dict[str, Any], scope: str) -> dict[str, Any]:
        if not isinstance(data, dict):
            self._warn(f"ignored malformed {scope} settings payload")
            return {}

        sanitized: dict[str, Any] = {}
        raw_data = copy.deepcopy(data)
        raw_data.pop("schemaVersion", None)

        for container_key in sorted(_CONTAINER_PATHS, key=lambda item: item.count(".")):
            if not _has_path(raw_data, container_key):
                continue
            value = _get_path(raw_data, container_key)
            if value is not None and not isinstance(value, dict):
                self._warn(f"ignored invalid object for {container_key}")

        for key, definition in SETTING_DEFINITIONS.items():
            if not _has_path(raw_data, key):
                continue
            if definition.scope not in {scope, SCOPE_BOTH}:
                self._warn(f"ignored {key} in {scope} settings")
                continue
            try:
                normalized = definition.validator(_get_path(raw_data, key))
            except ValueError:
                self._warn(f"ignored invalid value for {key}")
                continue
            _set_path(sanitized, key, normalized)

        return sanitized

    def _read_json_file(self, path: Path, label: str) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            self._warn(f"failed to read {label} settings: {exc}")
            return {}
        if not isinstance(payload, dict):
            self._warn(f"ignored non-object {label} settings file")
            return {}
        return payload

    def _write_json_file(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = copy.deepcopy(data)
        payload["schemaVersion"] = SCHEMA_VERSION
        serialized = json.dumps(payload, indent=2, sort_keys=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(serialized)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
