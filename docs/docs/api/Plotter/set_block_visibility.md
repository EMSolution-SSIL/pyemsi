---
title: set_block_visibility()
sidebar_position: 22
---

Sets the visibility for all actors associated with a block.

Updates the visibility state in the internal dictionary and applies it to all actors (feature edges, scalar field, contours, vector field) associated with the specified block, then renders the scene. Works in both desktop and notebook modes.

:::tip[Parameters]
- **`block_name`** (`str`) — The name of the block to update.
- **`visible`** (`bool`) — `True` to show the block, `False` to hide it.
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("mesh.vtm")
p.set_scalar("B-Mag (T)")
p.show()

# Hide a specific block
p.set_block_visibility("air", False)

# Show it again
p.set_block_visibility("air", True)
```

### See Also

- [`get_block_visibility()`](./get_block_visibility) — Check visibility of a block.
- [`set_blocks_visibility()`](./set_blocks_visibility) — Set visibility for multiple blocks in batch.
- [`get_block_names()`](./get_block_names) — Get list of block names.
