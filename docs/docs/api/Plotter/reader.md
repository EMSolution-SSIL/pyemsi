title: reader
sidebar_position: 12
---

PyVista reader stored on [`Plotter`](./index.md) after configuring a file with [`set_file()`](./set_file.md) or the `filepath` constructor argument.

Like [`set_file()`](./set_file.md), passing `filepath` to [`Plotter`](./index.md) creates the reader immediately via [`pyvista.get_reader(...)`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.get_reader), but does not read the dataset yet.

The dataset itself is still loaded lazily when you access [`mesh`](/docs/api/Plotter/mesh.md) or when [`show()`](/docs/api/Plotter/show.md) / [`export()`](/docs/api/Plotter/export.md) rebuild the scene.

:::info[Returns]
- [`pyvista.BaseReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.basereader) | `None`
    - `None` until you load a file.
    - For `*.pvd`, the reader is a [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader), which is time-aware.
:::

### Example

```python
from pyemsi import Plotter

file_path = examples.transient_path()
plt = Plotter(file_path)
print(plt.reader.__class__) # <class 'pyvista.core.utilities.reader.PVDReader'>
```
