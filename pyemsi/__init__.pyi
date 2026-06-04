from . import examples as examples
from .io import EMSolutionOutput as EMSolutionOutput
from .plotter import Plotter as Plotter
from .tools.FemapConverter import FemapConverter as FemapConverter

__version__: str
__all__: list[str]

def is_gui_running() -> bool: ...
def configure_logging(
    level: int = ...,
    handler: object | None = ...,
    format_string: str | None = ...,
) -> object: ...
