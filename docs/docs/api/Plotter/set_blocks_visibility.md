---
title: set_blocks_visibility()
sidebar_position: 23
---

Sets visibility for multiple blocks in batch.

Updates the visibility state for multiple blocks at once, then renders the scene. More efficient than calling [`set_block_visibility()`](../set_block_visibility) repeatedly. Works in both desktop and notebook modes.

:::tip[Parameters]
- **`visibility`** (`dict[str, bool]`) — Dictionary mapping block names to visibility states. `True` to show the block, `False` to hide it.
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)")
plt.render()

# Hide blocks '3' and '4' from the transient example
plt.set_blocks_visibility({
    "3": False,
    "4": False,
})

# Restore visibility
plt.set_blocks_visibility({
    "3": True,
    "4": True,
})
```

### Notebook Mode

This method works in notebook mode as well, making it useful for interactive visibility control in Jupyter:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path, notebook=True)
plt.set_scalar("B-Mag (T)")
plt.show()

# Toggle visibility in notebook
plt.set_blocks_visibility({"4": False})
```

### See Also

- [`get_block_visibility()`](../get_block_visibility) — Check visibility of a block.
- [`set_block_visibility()`](../set_block_visibility) — Set visibility for a single block.
- [`get_block_names()`](../get_block_names) — Get list of block names.
