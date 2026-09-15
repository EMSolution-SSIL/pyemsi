"""EMSolution input control file editor embedded from EMSolutionDocs.

The web bundle in ``editor/`` is built from the EMSolutionDocs submodule by
``tools/sync_input_control_editor.py``; do not edit it by hand.
"""

from ._widget import BUNDLE_DIR, InputControlEditorWidget

__all__ = ["BUNDLE_DIR", "InputControlEditorWidget"]
