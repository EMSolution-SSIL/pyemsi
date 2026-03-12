"""JSON-backed settings management for pyemsi."""

from .manager import (
    DEFAULT_SETTINGS,
    SCHEMA_VERSION,
    SettingsManager,
    decode_qt_state,
    encode_qt_state,
    get_user_config_dir,
)

__all__ = [
    "DEFAULT_SETTINGS",
    "SCHEMA_VERSION",
    "SettingsManager",
    "decode_qt_state",
    "encode_qt_state",
    "get_user_config_dir",
]
