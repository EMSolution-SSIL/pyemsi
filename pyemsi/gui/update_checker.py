from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from typing import Any, Mapping

from packaging.version import InvalidVersion, Version
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

import pyemsi
from pyemsi.settings import SettingsManager

_LATEST_RELEASE_API_URL = "https://api.github.com/repos/EMSolution-SSIL/pyemsi/releases/latest"
_UPDATE_CHECK_INTERVAL = timedelta(hours=24)


@dataclass(frozen=True)
class UpdateInfo:
    available: bool
    current_version: str
    latest_version: str | None = None
    release_url: str | None = None
    release_notes: str | None = None
    error: str | None = None


def utc_now_timestamp(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone information")
    return parsed.astimezone(timezone.utc)


def is_update_check_due(last_check_utc: str | None, now: datetime | None = None) -> bool:
    try:
        last_check = parse_utc_timestamp(last_check_utc)
    except ValueError:
        return True

    if last_check is None:
        return True

    current = now or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc) >= last_check + _UPDATE_CHECK_INTERVAL


def should_check_for_updates(
    *,
    manual: bool,
    check_automatically: bool,
    last_check_utc: str | None,
    now: datetime | None = None,
) -> bool:
    if manual:
        return True
    if not check_automatically:
        return False
    return is_update_check_due(last_check_utc, now=now)


def is_newer_version(current_version: str, latest_version: str) -> bool:
    return Version(latest_version) > Version(current_version)


def build_update_info_from_release(current_version: str, payload: Mapping[str, Any]) -> UpdateInfo:
    tag_name = payload.get("tag_name")
    if not isinstance(tag_name, str) or not tag_name.strip():
        return UpdateInfo(
            available=False,
            current_version=current_version,
            error="latest release did not include a valid tag_name",
        )

    release_url = payload.get("html_url") if isinstance(payload.get("html_url"), str) else None
    release_notes = payload.get("body") if isinstance(payload.get("body"), str) else None
    normalized_tag = tag_name.strip().lstrip("v")

    try:
        latest_version = str(Version(normalized_tag))
        current = str(Version(current_version))
    except InvalidVersion:
        return UpdateInfo(
            available=False,
            current_version=current_version,
            error=f"invalid release version tag: {tag_name.strip()}",
        )

    return UpdateInfo(
        available=is_newer_version(current, latest_version),
        current_version=current,
        latest_version=latest_version,
        release_url=release_url.strip() if release_url and release_url.strip() else None,
        release_notes=release_notes,
    )


class UpdateChecker(QObject):
    check_finished = Signal(object, bool)

    def __init__(self, settings_manager: SettingsManager, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings = settings_manager
        self._network_manager = QNetworkAccessManager(self)
        self._pending_reply: QNetworkReply | None = None
        self._pending_manual = False
        self._bootstrap_update_settings()

    def _bootstrap_update_settings(self) -> None:
        changed = False

        if self._settings.get_global("app.updates.check_automatically") is None:
            self._settings.set_global(
                "app.updates.check_automatically",
                self._settings.get_effective("app.updates.check_automatically"),
            )
            changed = True

        if changed:
            self._settings.save()

    def check_for_updates(self, manual: bool = False) -> bool:
        if self._pending_reply is not None:
            return False

        check_automatically = bool(self._settings.get_effective("app.updates.check_automatically"))
        last_check_utc = self._settings.get_effective("app.updates.last_check_utc")
        if not should_check_for_updates(
            manual=manual,
            check_automatically=check_automatically,
            last_check_utc=last_check_utc,
        ):
            return False

        if not manual:
            self._settings.set_global("app.updates.last_check_utc", utc_now_timestamp())
            self._settings.save()

        request = QNetworkRequest(QUrl(_LATEST_RELEASE_API_URL))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", f"pyemsi/{pyemsi.__version__}".encode("utf-8"))
        if hasattr(request, "setTransferTimeout"):
            request.setTransferTimeout(10000)

        reply = self._network_manager.get(request)
        self._pending_reply = reply
        self._pending_manual = manual
        reply.finished.connect(self._on_reply_finished)
        return True

    def _on_reply_finished(self) -> None:
        reply = self._pending_reply
        manual = self._pending_manual
        self._pending_reply = None
        self._pending_manual = False

        if reply is None:
            return

        try:
            info = self._build_result_from_reply(reply)
        finally:
            reply.deleteLater()

        self.check_finished.emit(info, manual)

    def _build_result_from_reply(self, reply: QNetworkReply) -> UpdateInfo:
        current_version = pyemsi.__version__
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code is not None and int(status_code) >= 400:
            return UpdateInfo(
                available=False,
                current_version=current_version,
                error=f"GitHub API returned HTTP {int(status_code)}",
            )

        if reply.error() != QNetworkReply.NetworkError.NoError:
            return UpdateInfo(
                available=False,
                current_version=current_version,
                error=reply.errorString(),
            )

        try:
            payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return UpdateInfo(
                available=False,
                current_version=current_version,
                error=f"failed to parse release payload: {exc}",
            )

        if not isinstance(payload, dict):
            return UpdateInfo(
                available=False,
                current_version=current_version,
                error="GitHub API returned an unexpected payload shape",
            )

        return build_update_info_from_release(current_version, payload)
