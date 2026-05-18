from __future__ import annotations

from datetime import datetime, timezone
import json

from pyemsi.gui.update_checker import UpdateChecker
from pyemsi.gui.update_checker import (
    build_update_info_from_release,
    is_newer_version,
    should_check_for_updates,
)
from pyemsi.settings import SettingsManager


class _DummySignal:
    def __init__(self) -> None:
        self._callbacks = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)


class _DummyReply:
    def __init__(self) -> None:
        self.finished = _DummySignal()


class _DummyNetworkManager:
    def __init__(self) -> None:
        self.requests = []

    def get(self, request):
        self.requests.append(request)
        return _DummyReply()


def test_is_newer_version_uses_semantic_comparison():
    assert is_newer_version("0.3.1", "0.3.2") is True
    assert is_newer_version("0.9.0", "0.10.0") is True
    assert is_newer_version("0.3.2", "0.3.2") is False


def test_build_update_info_accepts_optional_v_prefix():
    info = build_update_info_from_release(
        "0.3.1",
        {
            "tag_name": " v0.3.2 ",
            "html_url": "https://github.com/EMSolution-SSIL/pyemsi/releases/tag/0.3.2",
            "body": "Bug fixes",
        },
    )

    assert info.available is True
    assert info.current_version == "0.3.1"
    assert info.latest_version == "0.3.2"
    assert info.release_url == "https://github.com/EMSolution-SSIL/pyemsi/releases/tag/0.3.2"
    assert info.release_notes == "Bug fixes"
    assert info.error is None


def test_build_update_info_rejects_invalid_remote_tag():
    info = build_update_info_from_release(
        "0.3.1",
        {
            "tag_name": "release-0.3.2",
        },
    )

    assert info.available is False
    assert info.latest_version is None
    assert info.error == "invalid release version tag: release-0.3.2"


def test_should_check_for_updates_respects_automatic_interval():
    now = datetime(2026, 5, 18, 12, 0, tzinfo=timezone.utc)

    assert should_check_for_updates(
        manual=False,
        check_automatically=True,
        last_check_utc="2026-05-17T11:59:00Z",
        now=now,
    ) is True
    assert should_check_for_updates(
        manual=False,
        check_automatically=True,
        last_check_utc="2026-05-18T11:00:00Z",
        now=now,
    ) is False


def test_should_check_for_updates_manual_ignores_throttle():
    now = datetime(2026, 5, 18, 12, 0, tzinfo=timezone.utc)

    assert should_check_for_updates(
        manual=True,
        check_automatically=False,
        last_check_utc="2026-05-18T11:59:00Z",
        now=now,
    ) is True


def test_update_checker_uses_effective_defaults_when_global_update_keys_are_missing(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    manager = SettingsManager(global_settings_path=global_settings_path)
    checker = UpdateChecker(manager)
    network_manager = _DummyNetworkManager()
    checker._network_manager = network_manager

    assert manager.get_global("app.updates.check_automatically") is True
    assert manager.get_effective("app.updates.check_automatically") is True

    started = checker.check_for_updates(manual=False)

    assert started is True
    assert len(network_manager.requests) == 1


def test_update_checker_bootstrap_persists_update_policy_defaults(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    manager = SettingsManager(global_settings_path=global_settings_path)
    UpdateChecker(manager)

    assert global_settings_path.is_file()

    payload = json.loads(global_settings_path.read_text(encoding="utf-8"))
    assert payload["app"]["updates"]["check_automatically"] is True
    assert "last_check_utc" not in payload["app"]["updates"]


def test_update_checker_persists_last_check_for_fresh_global_settings(tmp_path):
    global_settings_path = tmp_path / "config" / "settings.json"
    manager = SettingsManager(global_settings_path=global_settings_path)
    checker = UpdateChecker(manager)
    network_manager = _DummyNetworkManager()
    checker._network_manager = network_manager

    started = checker.check_for_updates(manual=False)

    assert started is True

    payload = json.loads(global_settings_path.read_text(encoding="utf-8"))
    assert payload["app"]["updates"]["check_automatically"] is True
    assert payload["app"]["updates"]["last_check_utc"]
    assert manager.get_global("app.updates.last_check_utc") == payload["app"]["updates"]["last_check_utc"]
