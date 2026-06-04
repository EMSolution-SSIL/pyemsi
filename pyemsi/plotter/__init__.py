"""
pyemsi.plotter -- Shared visualization layer (PyVista + optional Qt).

Provides the dual-mode Plotter class usable from both the API (Jupyter/scripting)
and the GUI (embedded Qt interactor).
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .plotter import Plotter

__all__ = ["Plotter"]


def __getattr__(name: str) -> Any:
    """Resolve the heavy Plotter export on first access."""
    if name != "Plotter":
        raise AttributeError(f"module 'pyemsi.plotter' has no attribute {name!r}")

    value = getattr(import_module("pyemsi.plotter.plotter"), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose lazy exports to interactive tooling."""
    return sorted(set(globals()) | set(__all__))
