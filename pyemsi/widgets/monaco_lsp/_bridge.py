from qtpy.QtCore import QObject, Signal, Slot, Property
from qtpy.QtWebEngineWidgets import QWebEnginePage
import json


class BaseBridge(QObject):
    initialized = Signal()
    sendDataChanged = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.active = False
        self.queue = []

    def send_to_js(self, name, value):
        if self.active:
            data = json.dumps(value)
            self.sendDataChanged.emit(name, data)
        else:
            self.queue.append((name, value))

    @Slot(str, str)
    def receive_from_js(self, name, value):
        data = json.loads(value)
        self.setProperty(name, data)

    @Slot()
    def init(self):
        self.initialized.emit()
        self.active = True
        for name, value in self.queue:
            self.send_to_js(name, value)
        self.queue.clear()


class EditorBridge(BaseBridge):
    valueChanged = Signal()
    languageChanged = Signal()
    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._value = ""
        self._language = ""
        self._theme = ""

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self.valueChanged.emit()

    def getLanguage(self):
        return self._language

    def setLanguage(self, language):
        self._language = language
        self.languageChanged.emit()

    def getTheme(self):
        return self._theme

    def setTheme(self, theme):
        self._theme = theme
        self.themeChanged.emit()

    value = Property(str, fget=getValue, fset=setValue, notify=valueChanged)
    language = Property(str, fget=getLanguage, fset=setLanguage, notify=languageChanged)
    theme = Property(str, fget=getTheme, fset=setTheme, notify=themeChanged)


class MonacoPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        pass
