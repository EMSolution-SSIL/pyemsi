from pathlib import Path
import os

dir_path = str(Path(os.path.realpath(__file__)).parent)


def transient_path() -> str:
    return os.path.join(dir_path, "transient.pvd")
