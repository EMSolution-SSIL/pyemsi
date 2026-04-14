---
sidebar_position: 1
title: Installation
---

## Windows GUI Installation

The pyemsi GUI is currently supported on Windows only.

Installing pyemsi for GUI-based EMSolution work has two steps:

1. Install the pyemsi GUI application.
2. Install the `pyemsol` Python package inside the pyemsi GUI environment so EMSolution simulations can run from the application.

## Step 1: Install The pyemsi GUI

Download the most recent Windows installer from the GitHub releases page:

- [pyemsi releases](https://github.com/EMSolution-SSIL/pyemsi/releases)

After downloading the latest `pyemsi-<version>-setup.exe` file:

1. Run the installer.
2. Review the license agreement.
3. Choose the installation folder if you do not want to use the default location.
4. Select the optional components you want to install.
5. Complete the installation and launch pyemsi.

By default, the installer performs a per-user installation under the local application data folder, so administrator privileges are typically not required.

## Installer Options

The installer provides one required component and several optional integrations.

| Option | Description |
| --- | --- |
| `pyemsi (required)` | Installs the application files. This component is mandatory and cannot be disabled. |
| `Desktop Shortcut` | Creates a shortcut to pyemsi on the Windows desktop. |
| `Start Menu Shortcut` | Creates a Start Menu folder containing shortcuts for pyemsi and the uninstaller. |
| `Explorer "Open with pyemsi"` | Adds a right-click menu entry in Windows Explorer so you can open a folder in pyemsi directly from the folder or its background context menu. |

When installation finishes, the final page also provides:

- A checkbox to launch pyemsi immediately.
- A link to open the online documentation.

## Step 2: Install pyemsol Inside pyemsi

The GUI installation alone does not enable EMSolution simulation execution. To run EMSolution simulations from pyemsi, install the `pyemsol` wheel inside the embedded Python environment used by the GUI.

Start pyemsi, then open the IPython terminal inside the application and run:

```python
%pip install path/to/pyemsol.whl
```

Replace `path/to/pyemsol.whl` with the path to your local `pyemsol` wheel file.

If the IPython Terminal is not visible, enable it from:

- `View -> IPython Terminal`
- `Ctrl + I`

After the `pyemsol` package is installed, restart pyemsi if needed and the GUI will be ready to run EMSolution simulations.

## Verify The Installation

You should now be able to:

1. Launch pyemsi from the installer finish page, desktop shortcut, or Start Menu.
2. Open the IPython Terminal in pyemsi.
3. Confirm that the `pyemsol` package installs successfully without errors.
4. Use the GUI with EMSolution simulation functionality enabled.

