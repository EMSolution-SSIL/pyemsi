from __future__ import annotations

from dataclasses import dataclass
import math
import os
from typing import Literal

import numpy as np

FieldAssociation = Literal["point", "cell"]

INTERNAL_ARRAY_NAMES: frozenset[str] = frozenset(
    {
        "vtkGhostType",
        "vtkOriginalCellIds",
        "vtkOriginalPointIds",
        "vtkValidPointMask",
    }
)


@dataclass(slots=True)
class FieldFileMetadata:
    resolved_path: str
    scalar_names: list[str]
    contour_names: list[str]
    vector_names: list[str]
    scale_names: list[str]
    mesh_length: float
    array_ranges: dict[str, dict[str, float]]
    scalar_associations: dict[str, frozenset[FieldAssociation]]
    vector_associations: dict[str, frozenset[FieldAssociation]]
    vector_scale_names: dict[str, list[str]]


def _iter_mesh_blocks(mesh: object):
    import pyvista as pv

    if isinstance(mesh, pv.MultiBlock):
        for block in mesh:
            if block is None:
                continue
            yield from _iter_mesh_blocks(block)
        return
    yield mesh


def _mesh_length(mesh: object) -> float:
    length = getattr(mesh, "length", None)
    if isinstance(length, (int, float)) and math.isfinite(length):
        return float(length)

    bounds = getattr(mesh, "bounds", None)
    if bounds is not None and len(bounds) == 6:
        try:
            dx = float(bounds[1]) - float(bounds[0])
            dy = float(bounds[3]) - float(bounds[2])
            dz = float(bounds[5]) - float(bounds[4])
        except (TypeError, ValueError):
            dx = dy = dz = 0.0
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    block_lengths = [_mesh_length(block) for block in _iter_mesh_blocks(mesh)]
    finite_lengths = [value for value in block_lengths if math.isfinite(value) and value > 0.0]
    return max(finite_lengths, default=0.0)


def _array_component_count(array: object) -> int | None:
    ndim = getattr(array, "ndim", None)
    shape = getattr(array, "shape", None)
    if ndim == 1:
        return 1
    if isinstance(ndim, int) and ndim >= 2 and shape is not None and len(shape) >= 2:
        try:
            return int(shape[1])
        except (TypeError, ValueError):
            return None
    return None


def _finite_array_values(array: object, component_count: int) -> np.ndarray:
    try:
        values = np.asarray(array, dtype=float)
    except (TypeError, ValueError):
        return np.asarray([], dtype=float)
    if values.size == 0:
        return np.asarray([], dtype=float)

    reduced = np.linalg.norm(values, axis=1) if component_count == 3 and values.ndim >= 2 else values.reshape(-1)
    return reduced[np.isfinite(reduced)]


def _append_unique(items: list[str], seen: set[str], name: str) -> None:
    if name not in seen:
        seen.add(name)
        items.append(name)


def _merge_range(
    ranges: dict[str, dict[str, float]],
    name: str,
    minimum: float,
    maximum: float,
) -> None:
    existing = ranges.get(name)
    if existing is None:
        ranges[name] = {"min": minimum, "max": maximum}
        return
    existing["min"] = min(existing["min"], minimum)
    existing["max"] = max(existing["max"], maximum)


def _read_mesh(reader: object) -> object:
    mesh = reader.read()
    return mesh


def inspect_field_file(filepath: str | os.PathLike[str]) -> FieldFileMetadata:
    """Inspect supported scalar/vector arrays without constructing a GUI plotter."""
    import pyvista as pv

    resolved_path = os.path.abspath(os.path.normpath(os.fspath(filepath)))
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError(f"Field file not found: {resolved_path}")

    try:
        reader = pv.get_reader(resolved_path)
    except Exception as exc:
        raise ValueError(f"Unable to open field file '{resolved_path}': {exc}") from exc

    scalar_names: list[str] = []
    vector_names: list[str] = []
    scalar_seen: set[str] = set()
    vector_seen: set[str] = set()
    scalar_associations_mutable: dict[str, set[FieldAssociation]] = {}
    vector_associations_mutable: dict[str, set[FieldAssociation]] = {}
    array_ranges: dict[str, dict[str, float]] = {}
    vector_scale_candidates: dict[str, set[str]] = {}
    mesh_length = 0.0

    def inspect_mesh(mesh: object) -> None:
        nonlocal mesh_length
        mesh_length = max(mesh_length, _mesh_length(mesh))

        for block in _iter_mesh_blocks(mesh):
            context_arrays: dict[FieldAssociation, dict[str, int]] = {"point": {}, "cell": {}}
            for association, attributes in (
                ("point", getattr(block, "point_data", None)),
                ("cell", getattr(block, "cell_data", None)),
            ):
                if attributes is None:
                    continue
                for raw_name in getattr(attributes, "keys", lambda: [])():
                    name = str(raw_name)
                    if not name or name in INTERNAL_ARRAY_NAMES:
                        continue
                    array = attributes[raw_name]
                    component_count = _array_component_count(array)
                    if component_count not in (1, 3):
                        continue

                    context_arrays[association][name] = component_count
                    if component_count == 1:
                        _append_unique(scalar_names, scalar_seen, name)
                    else:
                        _append_unique(vector_names, vector_seen, name)
                        vector_associations_mutable.setdefault(name, set()).add(association)

                    finite_values = _finite_array_values(array, component_count)
                    if finite_values.size:
                        _merge_range(
                            array_ranges,
                            name,
                            float(finite_values.min()),
                            float(finite_values.max()),
                        )

            context_scalar_names = {
                name
                for arrays in context_arrays.values()
                for name, component_count in arrays.items()
                if component_count == 1
            }
            for name in context_scalar_names:
                context_associations = {
                    association
                    for association, arrays in context_arrays.items()
                    if arrays.get(name) == 1
                }
                existing_associations = scalar_associations_mutable.get(name)
                if existing_associations is None:
                    scalar_associations_mutable[name] = context_associations
                else:
                    existing_associations.intersection_update(context_associations)

            for arrays in context_arrays.values():
                compatible_names = set(arrays)
                for name, component_count in arrays.items():
                    if component_count != 3:
                        continue
                    existing = vector_scale_candidates.get(name)
                    if existing is None:
                        vector_scale_candidates[name] = compatible_names.copy()
                    else:
                        existing.intersection_update(compatible_names)

    time_reader_type = getattr(pv, "TimeReader", None)
    time_reader = reader if time_reader_type is not None and isinstance(reader, time_reader_type) else None
    original_time_value = getattr(time_reader, "active_time_value", None) if time_reader is not None else None

    try:
        number_time_points = int(getattr(time_reader, "number_time_points", 0)) if time_reader is not None else 0
        if number_time_points > 0:
            for time_point in range(number_time_points):
                time_reader.set_active_time_point(time_point)
                inspect_mesh(_read_mesh(reader))
        else:
            inspect_mesh(_read_mesh(reader))
    except Exception as exc:
        raise ValueError(f"Unable to inspect field file '{resolved_path}': {exc}") from exc
    finally:
        if time_reader is not None and original_time_value is not None:
            try:
                time_reader.set_active_time_value(original_time_value)
            except Exception:
                pass

    inconsistent_names = scalar_seen & vector_seen
    unsafe_scalar_names = {
        name for name, associations in scalar_associations_mutable.items() if not associations
    }
    excluded_names = inconsistent_names | unsafe_scalar_names
    scalar_names = [name for name in scalar_names if name not in excluded_names]
    vector_names = [name for name in vector_names if name not in inconsistent_names]
    for name in excluded_names:
        array_ranges.pop(name, None)

    scalar_associations = {
        name: frozenset(associations)
        for name, associations in scalar_associations_mutable.items()
        if name not in excluded_names
    }
    vector_associations = {
        name: frozenset(associations)
        for name, associations in vector_associations_mutable.items()
        if name not in inconsistent_names
    }
    contour_names = [
        name for name in scalar_names if "point" in scalar_associations.get(name, frozenset())
    ]
    visible_scalar_names = set(scalar_names)
    scale_names = [*scalar_names, *(name for name in vector_names if name not in visible_scalar_names)]
    vector_scale_names = {
        name: [candidate for candidate in scale_names if candidate in vector_scale_candidates.get(name, set())]
        for name in vector_names
    }

    return FieldFileMetadata(
        resolved_path=resolved_path,
        scalar_names=scalar_names,
        contour_names=contour_names,
        vector_names=vector_names,
        scale_names=scale_names,
        mesh_length=mesh_length,
        array_ranges=array_ranges,
        scalar_associations=scalar_associations,
        vector_associations=vector_associations,
        vector_scale_names=vector_scale_names,
    )
