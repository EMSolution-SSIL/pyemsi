---
title: get_block_visibility()
sidebar_position: 21
---

Returns the visibility state of a block.

The visibility state is tracked internally and persists across render cycles. Defaults to `True` for blocks not yet tracked.

:::tip[Parameters]
- **`block_name`** (`str`) — The name of the block to check.
:::

:::info[Returns]
- `bool` — `True` if the block is visible, `False` otherwise.
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)

# The transient example has blocks '1', '3', and '4'
print(plt.get_block_visibility("4"))  # True

plt.set_block_visibility("4", False)
print(plt.get_block_visibility("4"))  # False
```

### See Also

- [`set_block_visibility()`](./set_block_visibility) — Set visibility for a single block.
- [`set_blocks_visibility()`](./set_blocks_visibility) — Set visibility for multiple blocks in batch.
- [`get_block_names()`](./get_block_names) — Get list of block names.
