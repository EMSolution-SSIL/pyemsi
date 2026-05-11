from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Literal

from ems_file_format_converter import atlas, femap, unv

SourceFormat = Literal["atlas", "unv"]


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


def _normalize_bool(value: object, fallback: bool = False) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    raise ValueError("expected a boolean value")


def _resolve_path(input_dir: str, value: str) -> str:
    candidate = value
    if not os.path.isabs(candidate):
        candidate = os.path.join(input_dir, candidate)
    return os.path.abspath(os.path.normpath(candidate))


def _default_output_path(input_dir: str, source_path: str) -> str:
    resolved_source = _resolve_path(input_dir, source_path)
    source_dir = os.path.dirname(resolved_source)
    stem, _suffix = os.path.splitext(os.path.basename(resolved_source))
    return os.path.join(source_dir, stem)


@dataclass(frozen=True)
class SourceConversionEntry:
    source_path: str
    output_path: str


@dataclass(frozen=True)
class SourceToFemapConfig:
    source_format: SourceFormat
    input_dir: str
    overwrite: bool
    mesh: SourceConversionEntry
    magnetic: SourceConversionEntry | None = None
    current: SourceConversionEntry | None = None
    electric: SourceConversionEntry | None = None
    force: SourceConversionEntry | None = None
    force_J_B: SourceConversionEntry | None = None
    heat: SourceConversionEntry | None = None
    displacement: SourceConversionEntry | None = None

    def post_entries(self) -> dict[str, SourceConversionEntry]:
        entries = {
            "magnetic": self.magnetic,
            "current": self.current,
            "electric": self.electric,
            "force": self.force,
            "force_J_B": self.force_J_B,
            "heat": self.heat,
            "displacement": self.displacement,
        }
        return {name: entry for name, entry in entries.items() if entry is not None}


def _normalize_entry(
    payload: dict[str, object],
    input_dir: str,
    source_key: str,
    output_key: str,
    *,
    required: bool,
    overwrite: bool,
) -> SourceConversionEntry | None:
    source_path = _normalize_optional_text(payload.get(source_key))
    if source_path is None:
        if required:
            raise ValueError(f"{source_key} is required")
        return None

    if overwrite:
        output_path = _resolve_path(input_dir, source_path)
    else:
        configured_output = _normalize_optional_text(payload.get(output_key))
        output_path = (
            _resolve_path(input_dir, configured_output)
            if configured_output is not None
            else _default_output_path(input_dir, source_path)
        )

    return SourceConversionEntry(
        source_path=source_path,
        output_path=os.path.abspath(os.path.normpath(output_path)),
    )


def load_source_to_femap_config(payload: dict[str, object]) -> SourceToFemapConfig:
    source_format = _normalize_text(payload.get("source_format"), "")
    if source_format not in {"atlas", "unv"}:
        raise ValueError("source_format must be 'atlas' or 'unv'")

    input_dir = _normalize_text(payload.get("input_dir"), "")
    if not input_dir:
        raise ValueError("input_dir is required")
    input_dir = os.path.abspath(os.path.normpath(input_dir))

    overwrite = _normalize_bool(payload.get("overwrite"), True)

    return SourceToFemapConfig(
        source_format=source_format,
        input_dir=input_dir,
        overwrite=overwrite,
        mesh=_normalize_entry(payload, input_dir, "mesh", "mesh_output", required=True, overwrite=overwrite),
        magnetic=_normalize_entry(
            payload, input_dir, "magnetic", "magnetic_output", required=False, overwrite=overwrite
        ),
        current=_normalize_entry(payload, input_dir, "current", "current_output", required=False, overwrite=overwrite),
        electric=_normalize_entry(
            payload, input_dir, "electric", "electric_output", required=False, overwrite=overwrite
        ),
        force=_normalize_entry(payload, input_dir, "force", "force_output", required=False, overwrite=overwrite),
        force_J_B=_normalize_entry(
            payload, input_dir, "force_J_B", "force_J_B_output", required=False, overwrite=overwrite
        ),
        heat=_normalize_entry(payload, input_dir, "heat", "heat_output", required=False, overwrite=overwrite),
        displacement=_normalize_entry(
            payload, input_dir, "displacement", "displacement_output", required=False, overwrite=overwrite
        ),
    )


ReaderPair = tuple[Callable[[str], object], Callable[[str], object]]


def _reader_pair(source_format: SourceFormat) -> ReaderPair:
    if source_format == "atlas":
        return atlas.read_mesh, atlas.read_post
    return unv.read_mesh, unv.read_post


def convert_source_to_femap(config: SourceToFemapConfig) -> list[str]:
    read_mesh, read_post = _reader_pair(config.source_format)

    written_paths: list[str] = []

    mesh_source = _resolve_path(config.input_dir, config.mesh.source_path)
    mesh = read_mesh(mesh_source)
    femap.write_neu(config.mesh.output_path, mesh)
    written_paths.append(config.mesh.output_path)

    for entry in config.post_entries().values():
        post_source = _resolve_path(config.input_dir, entry.source_path)
        steps = read_post(post_source)
        femap.write_neu_post(entry.output_path, steps, mode="components")
        written_paths.append(entry.output_path)

    return written_paths
