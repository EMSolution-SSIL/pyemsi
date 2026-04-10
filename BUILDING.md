# Building From Source

This guide covers the repository tasks needed when working on `pyemsi` locally.

## Development Install

Install the package in editable mode:

```bash
pip install -e .
```

If you want the test dependencies as well:

```bash
pip install -e ".[dev]"
```

## Qt Resources

If you modify Qt resources such as icons or UI assets, regenerate the compiled resource module manually:

```bash
pyside6-rcc.exe .\pyemsi\resources\resources.qrc -g python -o .\pyemsi\resources\resources.py
```

## Cython Extension

The `femap_parser` module is implemented in Cython for performance. Source distributions include a generated C fallback, but when you edit the `.pyx` implementation you should rebuild the extension.

Compile the extension in place:

```bash
python setup.py build_ext --inplace
```

The compiled extension will be written into `pyemsi/core/`.

The Windows private-runtime packager also depends on this in-place extension artifact. Re-run this command before invoking [tools/build_windows_private_runtime.py](./tools/build_windows_private_runtime.py) if the compiled module is missing or stale.

## Related Guides

- For user installation, see [INSTALLATION.md](./INSTALLATION.md).
- For wheel and installer builds, see [PACKAGING.md](./PACKAGING.md).