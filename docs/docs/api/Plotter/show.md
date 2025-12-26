---
title: show
sidebar_position: 6
---

## `show()`

Displays the plot.

If a file was loaded (via `filepath` or `set_file()`), `show()` refreshes the scene in this order:

1. Scalar field (`set_scalar()`)
2. Contours (`set_contour()`)
3. Vector glyphs (`set_vector()`)
4. Feature edges (`set_feature_edges()`)
5. Camera reset

### Returns

- Desktop mode (`notebook=False`): `None` (starts the Qt event loop; blocking).
- Notebook mode (`notebook=True`): returns the PyVista notebook display output/widget.

### Example

```python
from pyemsi import Plotter

Plotter("mesh.vtm").set_scalar("B-Mag (T)", mode="element", cell2point=True).show()
```

