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
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)

block_names = plt.get_block_names()
print(block_names)  # ['1', '3', '4']
```
