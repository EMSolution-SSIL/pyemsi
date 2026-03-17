from __future__ import annotations

import argparse
import json
import logging
import os
import sys


def _ensure_repo_root_on_sys_path() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_ensure_repo_root_on_sys_path()

import pyemsi
from pyemsi.tools.FemapConverter import FemapConverter


def _load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("converter config must be a JSON object")
    return payload


def _normalize_text(value: object, fallback: str) -> str:
    if value is None:
        return fallback
    if not isinstance(value, str):
        raise ValueError("expected a string value")
    normalized = value.strip()
    return normalized or fallback


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected a string or null value")
    normalized = value.strip()
    return normalized or None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a pyemsi FemapConverter job from a JSON config file.")
    parser.add_argument("--config", required=True, help="Path to a JSON config file produced by the GUI.")
    args = parser.parse_args()

    config_path = os.path.abspath(os.path.normpath(args.config))
    payload = _load_config(config_path)

    input_dir = _normalize_text(payload.get("input_dir"), "")
    if not input_dir:
        raise ValueError("input_dir is required")

    pyemsi.configure_logging(logging.INFO)

    converter = FemapConverter(
        input_dir=input_dir,
        output_dir=_normalize_text(payload.get("output_dir"), ".pyemsi"),
        output_name=_normalize_text(payload.get("output_name"), "output"),
        force_2d=bool(payload.get("force_2d", False)),
        ascii_mode=bool(payload.get("ascii_mode", False)),
        mesh=_normalize_text(payload.get("mesh"), "post_geom"),
        magnetic=_normalize_optional_text(payload.get("magnetic")),
        current=_normalize_optional_text(payload.get("current")),
        force=_normalize_optional_text(payload.get("force")),
        force_J_B=_normalize_optional_text(payload.get("force_J_B")),
        heat=_normalize_optional_text(payload.get("heat")),
        displacement=_normalize_optional_text(payload.get("displacement")),
    )

    logging.getLogger(__name__).info("Running FemapConverter for %s", input_dir)
    converter.run()
    logging.getLogger(__name__).info("FemapConverter run completed")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.getLogger(__name__).exception("FemapConverter run failed")
        raise
