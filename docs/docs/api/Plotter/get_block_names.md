---
title: get_block_names()
sidebar_position: 20
---

Returns a list of block names from a multi-block mesh.

For [`MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.MultiBlock.html) datasets, returns all block names (or string indices for unnamed blocks). For single meshes, returns an empty list.

:::info[Returns]
- `list[str]` — List of block name strings.
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("mesh.vtm")
block_names = p.get_block_names()
print(block_names)  # e.g., ["coil", "core", "air"]
```
