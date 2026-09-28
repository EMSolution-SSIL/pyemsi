import os

# Run Qt headless with an in-process clipboard. On the native Windows platform,
# the Clipboard User Service reads each clipboard write lazily from our process;
# with no event loop running between tests it holds the clipboard open and later
# writes silently fail. Must be set before any QApplication is created.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
