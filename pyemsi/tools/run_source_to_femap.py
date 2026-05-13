from __future__ import annotations

import os
import sys


def _ensure_repo_root_on_sys_path() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_ensure_repo_root_on_sys_path()

import argparse  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402

import pyemsi  # noqa: E402
from pyemsi.tools.source_to_femap import convert_source_to_femap, load_source_to_femap_config  # noqa: E402

LOGGER = logging.getLogger("pyemsi.tools.run_source_to_femap")


def _load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("converter config must be a JSON object")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a pyemsi source-to-FEMAP conversion job from a JSON config.")
    parser.add_argument("--config", required=True, help="Path to a JSON config file produced by the GUI.")
    args = parser.parse_args()

    config_path = os.path.abspath(os.path.normpath(args.config))
    payload = _load_config(config_path)
    config = load_source_to_femap_config(payload)

    pyemsi.configure_logging(logging.INFO)

    LOGGER.info(
        "Running %s to FEMAP conversion for %s",
        config.source_format,
        config.input_dir,
    )
    written_paths = convert_source_to_femap(config)
    LOGGER.info("Source-to-FEMAP conversion completed: %s", written_paths)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        LOGGER.exception("Source-to-FEMAP conversion failed")
        raise
