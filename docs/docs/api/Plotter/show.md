---
title: show()
sidebar_position: 6
---
Displays the plot.

If a file was loaded (via `filepath` or [`set_file()`](/docs/api/Plotter/set_file.md)), `show()` refreshes the scene in this order:

1. Scalar field ([`set_scalar()`](/docs/api/Plotter/set_scalar.md))
2. Contours ([`set_contour()`](/docs/api/Plotter/set_contour.md))
3. Vector glyphs ([`set_vector()`](/docs/api/Plotter/set_vector.md))
4. Feature edges ([`set_feature_edges()`](/docs/api/Plotter/set_feature_edges.md))
5. Camera reset

:::info[Returns]
- Desktop mode (`notebook=False`): `None` (starts the Qt event loop; blocking).
- Notebook mode (`notebook=True`): returns the PyVista notebook display output/widget.
:::

### Example

```python
from pyemsi import Plotter

Plotter("mesh.vtm").set_scalar("B-Mag (T)", mode="element", cell2point=True).show()
```

