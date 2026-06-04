# TODO: Add the related documentation for the module and its components.
from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._emsolution_output import (
        AnalysisCondition,
        CircuitData,
        CircuitElement,
        EMSolutionOutput,
        ForceNodalData,
        ForceNodalEntry,
        MetaData,
        NetworkData,
        NetworkElement,
        PlotAxisOption,
        PlotSeriesDescriptor,
    )

__all__ = [
    "EMSolutionOutput",
    "MetaData",
    "AnalysisCondition",
    "CircuitElement",
    "CircuitData",
    "NetworkElement",
    "NetworkData",
    "ForceNodalEntry",
    "ForceNodalData",
    "PlotAxisOption",
    "PlotSeriesDescriptor",
]

_LAZY_EXPORTS = {name: ("pyemsi.io._emsolution_output", name) for name in __all__}


def __getattr__(name: str) -> Any:
    """Resolve heavy IO exports on first access."""
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'pyemsi.io' has no attribute {name!r}")

    module_name, attr_name = target
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose lazy exports to interactive tooling."""
    return sorted(set(globals()) | set(__all__))
