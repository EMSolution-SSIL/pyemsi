"""EMSolution input control file editor embedded from EMSolutionDocs.

The web bundle in ``editor/`` is built from a private EMSolutionDocs checkout by
``tools/sync_input_control_editor.py``; users do not need access to that repository.
Do not edit the generated bundle by hand.
"""

from ._widget import BUNDLE_DIR, InputControlEditorWidget

__all__ = ["BUNDLE_DIR", "InputControlEditorWidget"]
