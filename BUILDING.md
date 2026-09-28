# Building From Source

This guide covers the Windows development workflow for `pyemsi`. The checked-in Pixi configuration currently targets `win-64` and provides Python 3.11, the native dependencies, the editable `pyemsi` install, and the developer tools.

## Set Up The Development Environment

Install [Pixi](https://pixi.sh/) and run the following command from the repository root:

```powershell
pixi install
```

Pixi creates the environment under `.pixi/` and installs `pyemsi` in editable mode. A separate virtual environment and `pip install -e .` are not required.

Re-run `pixi install` after pulling changes to `pyproject.toml` or `pixi.lock`.

Then install the Git pre-commit hook once per clone:

```powershell
pixi run install-hooks
```

This installs the [pre-commit](https://pre-commit.com/) hook and configures `git blame` to skip the formatting-only commits listed in `.git-blame-ignore-revs`.

## Code Style

Formatting and linting use [Ruff](https://docs.astral.sh/ruff/), pinned in `pyproject.toml` and `pixi.lock`. Settings live in the `[tool.ruff]` section of `pyproject.toml`: 120-character lines, double quotes, and LF line endings.

```powershell
pixi run format
pixi run lint
```

- Do not use Black, isort, or autopep8. They use different settings and would reformat code that Ruff has already formatted.
- Import sorting is intentionally disabled. FreeCAD modules are sensitive to import order, so keep existing imports in place and add new ones without reordering.
- The lint rule set is intentionally minimal (`E4`, `E7`, `E9`, `F`).
- The pre-commit hook runs `ruff format` and `ruff check` on staged Python files. If the formatter rewrites a file, the commit stops. Review the change, run `git add` again, and commit.
- Line endings are normalized to LF by `.gitattributes`.
- If you make a formatting-only commit, add its hash to `.git-blame-ignore-revs`.

## Common Development Commands

Start the GUI:

```powershell
pixi run gui
```

Run the test suite:

```powershell
pixi run test
```

Run a specific test or pass additional arguments to pytest:

```powershell
pixi run pytest tests/test_main_window_settings.py -k external_terminal
```

Run an arbitrary Python command inside the Pixi environment:

```powershell
pixi run python --version
pixi run python path/to/script.py
```

You can also activate the environment for a longer development session:

```powershell
pixi shell
```

After activation, commands such as `python`, `pytest`, and `pyside6-rcc` use the Pixi environment directly. Exit the shell when finished:

```powershell
exit
```

## Manage Dependencies

Use Pixi rather than `pip` so changes are recorded in both `pyproject.toml` and `pixi.lock`.

Add a package from conda-forge:

```powershell
pixi add package-name
```

Add a package from PyPI when it is not available or suitable from conda-forge:

```powershell
pixi add --pypi package-name
```

After changing dependencies, commit both `pyproject.toml` and `pixi.lock`.

## Qt Resources

If you modify Qt resources such as icons or UI assets, regenerate the compiled resource module:

```powershell
pixi run pyside6-rcc .\pyemsi\resources\resources.qrc -g python -o .\pyemsi\resources\resources.py
```

## Cython Extension

The `femap_parser` module is implemented in Cython for performance. Cython is required to build it: the generated C file is written to `build/` and is not tracked in Git. When you edit the `.pyx` implementation, rebuild the extension.

Compile the extension in place:

```powershell
pixi run python setup.py build_ext --inplace
```

The compiled extension is written to `pyemsi/core/`.

The Windows private-runtime packager also depends on this in-place extension artifact. Re-run the command before invoking [tools/build_windows_private_runtime.py](./tools/build_windows_private_runtime.py) if the compiled module is missing or stale.

## Related Guides

- For user installation, see [INSTALLATION.md](./INSTALLATION.md).
- For wheel and installer builds, see [PACKAGING.md](./PACKAGING.md).
