from __future__ import annotations


def build_completion_item_metadata_js() -> str:
    """Return Monaco completion metadata fields preserved from the LSP response."""
    return "\n".join(
        [
            "                        sortText:      item.sortText || item.label,",
            "                        filterText:    item.filterText || item.label,",
            "                        preselect:     !!item.preselect,",
        ]
    )
