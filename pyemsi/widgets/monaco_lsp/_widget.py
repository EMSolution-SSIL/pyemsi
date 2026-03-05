import sys
import os
import subprocess
import socket
from pathlib import Path

from qtpy.QtCore import Signal, QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWebChannel import QWebChannel

from ._bridge import EditorBridge, MonacoPage

_PKG_DIR = Path(__file__).parent

# Extension-to-Monaco language mapping (also used by file_viewers)
EXT_TO_LANG: dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".pyx": "python",
    ".pxd": "python",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".md": "markdown",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".xml": "xml",
    ".xsl": "xml",
    ".xsd": "xml",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cxx": "cpp",
    ".hxx": "cpp",
    ".cc": "cpp",
    ".java": "java",
    ".rs": "rust",
    ".go": "go",
    ".rb": "ruby",
    ".sql": "sql",
    ".sh": "shell",
    ".bash": "shell",
    ".bat": "bat",
    ".cmd": "bat",
    ".ps1": "powershell",
    ".toml": "ini",
    ".cfg": "ini",
    ".ini": "ini",
    ".csv": "plaintext",
    ".log": "plaintext",
    ".txt": "plaintext",
    ".rst": "restructuredtext",
    ".tex": "latex",
}

# Languages for which an LSP server can be spawned
_LSP_SERVERS: dict[str, list[str]] = {
    "python": [sys.executable, "-m", "pylsp", "--ws", "--port", "{port}"],
}


def _find_free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


_HTML = r"""<!DOCTYPE html>
<style>
    * { padding: 0; margin: 0; }
    html, body { min-height: 100% !important; height: 100%; overflow: hidden; }
    #container { width: 100%; height: 100%; overflow: hidden; position: relative; }
</style>
<html>
<head>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
</head>
<body>
    <div id="container"></div>
    <script src="monaco-editor/min/vs/loader.js"></script>
    <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
    'use strict';
    const LSP_PORT = __LSP_PORT__;
    const LSP_LANGUAGE = '__LSP_LANGUAGE__';

    // ── LSP JSON-RPC client over WebSocket ──────────────────────────────────────
    class LspClient {
        constructor(wsUrl, languageId, fileExt) {
            this._wsUrl = wsUrl;
            this._msgId = 1;
            this._pending = {};
            this._initialized = false;
            this._stopping = false;
            this._languageId = languageId || 'python';
            this._fileUri = 'file:///untitled' + (fileExt || '.py');
            this._version = 0;
            this.onDiagnostics = null;
            this.onReady = null;
            this._connect();
        }

        _connect() {
            try { this._ws = new WebSocket(this._wsUrl); }
            catch (_) { setTimeout(() => { if (!this._stopping) this._connect(); }, 1500); return; }
            this._ws.onopen    = () => this._initialize();
            this._ws.onmessage = (evt) => { try { this._onMessage(JSON.parse(evt.data)); } catch (_) {} };
            this._ws.onerror   = () => {};
            this._ws.onclose   = () => { if (!this._stopping) setTimeout(() => this._connect(), 1500); };
        }

        _send(msg) {
            if (this._ws && this._ws.readyState === WebSocket.OPEN)
                this._ws.send(JSON.stringify(msg));
        }

        _request(method, params) {
            return new Promise((resolve, reject) => {
                const id = this._msgId++;
                this._pending[id] = { resolve, reject };
                this._send({ jsonrpc: '2.0', id, method, params });
                setTimeout(() => {
                    if (this._pending[id]) { delete this._pending[id]; reject(new Error('timeout')); }
                }, 8000);
            });
        }

        _notify(method, params) { this._send({ jsonrpc: '2.0', method, params }); }

        _onMessage(msg) {
            if (msg.id !== undefined && this._pending[msg.id]) {
                const { resolve, reject } = this._pending[msg.id];
                delete this._pending[msg.id];
                if (msg.error) reject(new Error(msg.error.message));
                else resolve(msg.result);
            }
            if (msg.method === 'textDocument/publishDiagnostics' && this.onDiagnostics)
                this.onDiagnostics(msg.params);
        }

        async _initialize() {
            try {
                await this._request('initialize', {
                    processId: null,
                    clientInfo: { name: 'monaco-lsp-client', version: '1.0' },
                    rootUri: null,
                    workspaceFolders: null,
                    capabilities: {
                        textDocument: {
                            synchronization: { dynamicRegistration: false, willSave: false, didSave: false },
                            completion: {
                                dynamicRegistration: false,
                                completionItem: { snippetSupport: false, documentationFormat: ['plaintext'] }
                            },
                            hover: { dynamicRegistration: false, contentFormat: ['plaintext'] },
                            signatureHelp: {
                                dynamicRegistration: false,
                                signatureInformation: { documentationFormat: ['plaintext'] }
                            },
                            publishDiagnostics: { relatedInformation: false }
                        }
                    }
                });
                this._notify('initialized', {});
                this._initialized = true;
                if (this.onReady) this.onReady();
            } catch (e) { console.error('LSP init failed:', e.message); }
        }

        openDocument(text) {
            this._version = 1;
            this._notify('textDocument/didOpen', {
                textDocument: { uri: this._fileUri, languageId: this._languageId, version: this._version, text }
            });
        }

        changeDocument(text) {
            this._version++;
            this._notify('textDocument/didChange', {
                textDocument: { uri: this._fileUri, version: this._version },
                contentChanges: [{ text }]
            });
        }

        async completion(line, character) {
            if (!this._initialized) return null;
            try { return await this._request('textDocument/completion', { textDocument: { uri: this._fileUri }, position: { line, character } }); }
            catch (_) { return null; }
        }

        async hover(line, character) {
            if (!this._initialized) return null;
            try { return await this._request('textDocument/hover', { textDocument: { uri: this._fileUri }, position: { line, character } }); }
            catch (_) { return null; }
        }

        async signatureHelp(line, character) {
            if (!this._initialized) return null;
            try { return await this._request('textDocument/signatureHelp', { textDocument: { uri: this._fileUri }, position: { line, character } }); }
            catch (_) { return null; }
        }

        stop() { this._stopping = true; this._initialized = false; if (this._ws) this._ws.close(); }

        changeFileUri(newUri, text) {
            if (this._initialized) {
                this._notify('textDocument/didClose', { textDocument: { uri: this._fileUri } });
            }
            this._fileUri = newUri;
            if (this._initialized) {
                this.openDocument(text);
            }
        }
    }

    function lspKindToMonaco(kind) {
        const k = monaco.languages.CompletionItemKind;
        const map = [, k.Text, k.Method, k.Function, k.Constructor, k.Field, k.Variable,
                      k.Class, k.Interface, k.Module, k.Property, k.Unit, k.Value, k.Enum,
                      k.Keyword, k.Snippet, k.Color, k.File, k.Reference, k.Folder,
                      k.EnumMember, k.Constant, k.Struct, k.Event, k.Operator, k.TypeParameter];
        return map[kind] !== undefined ? map[kind] : k.Text;
    }

    function extractDocString(doc) {
        if (!doc) return '';
        return typeof doc === 'string' ? doc : (doc.value || '');
    }

    // ── Editor + Monaco providers ───────────────────────────────────────────────
    var bridge = null;
    var editor = null;
    var lspClient = null;
    var registeredLspLanguages = new Set();
    var _bridgeChannel = null;   // stash QWebChannel result until editor ready
    var _editorReady = false;    // true once require callback completed
    var _bridgeReady = false;    // true once QWebChannel callback completed

    // Called after BOTH editor and bridge are available so that
    // queued Python→JS messages are only flushed when the editor exists.
    function _finishInit() {
        if (!_editorReady || !_bridgeReady) return;
        bridge = _bridgeChannel.objects.bridge;
        bridge.sendDataChanged.connect(updateFromPython);
        bridge.init();   // flush queue – editor guaranteed non-null
        init();
    }

    function registerLspProviders(langId) {
        if (registeredLspLanguages.has(langId)) return;
        registeredLspLanguages.add(langId);

        // Completion
        monaco.languages.registerCompletionItemProvider(langId, {
            triggerCharacters: ['.', '('],
            provideCompletionItems: async (model, position) => {
                if (!lspClient || !lspClient._initialized) return { suggestions: [] };
                const result = await lspClient.completion(position.lineNumber - 1, position.column - 1);
                if (!result) return { suggestions: [] };
                const items = Array.isArray(result) ? result : (result.items || []);
                const word  = model.getWordUntilPosition(position);
                const range = {
                    startLineNumber: position.lineNumber, endLineNumber: position.lineNumber,
                    startColumn: word.startColumn,        endColumn:    word.endColumn,
                };
                return {
                    suggestions: items.map(item => ({
                        label:         item.label,
                        kind:          lspKindToMonaco(item.kind),
                        insertText:    item.textEdit ? item.textEdit.newText : (item.insertText || item.label),
                        detail:        item.detail || '',
                        documentation: extractDocString(item.documentation),
                        range,
                    }))
                };
            }
        });

        // Hover
        monaco.languages.registerHoverProvider(langId, {
            provideHover: async (model, position) => {
                if (!lspClient || !lspClient._initialized) return null;
                const result = await lspClient.hover(position.lineNumber - 1, position.column - 1);
                if (!result || !result.contents) return null;
                const raw = Array.isArray(result.contents) ? result.contents : [result.contents];
                return { contents: raw.map(c => ({ value: extractDocString(c) })) };
            }
        });

        // Signature help
        monaco.languages.registerSignatureHelpProvider(langId, {
            signatureHelpTriggerCharacters: ['(', ','],
            provideSignatureHelp: async (model, position) => {
                if (!lspClient || !lspClient._initialized) return null;
                const result = await lspClient.signatureHelp(position.lineNumber - 1, position.column - 1);
                if (!result || !result.signatures || result.signatures.length === 0) return null;
                return {
                    value: {
                        signatures: result.signatures.map(s => ({
                            label:         s.label,
                            documentation: { value: extractDocString(s.documentation) },
                            parameters:    (s.parameters || []).map(p => ({
                                label:         p.label,
                                documentation: { value: extractDocString(p.documentation) }
                            }))
                        })),
                        activeSignature: result.activeSignature || 0,
                        activeParameter: result.activeParameter || 0,
                    },
                    dispose() {}
                };
            }
        });
    }

    require.config({ paths: { 'vs': 'monaco-editor/min/vs' } });

    require(['vs/editor/editor.main'], () => {
        editor = monaco.editor.create(document.getElementById('container'), {
            fontFamily: 'Consolas, "Courier New", monospace',
            automaticLayout: true,
        });

        editor.onDidChangeModelContent(() => {
            const text = editor.getModel().getValue();
            sendToPython('value', text);
            if (lspClient && lspClient._initialized) lspClient.changeDocument(text);
        });

        editor.onDidChangeModelLanguage((event) => {
            sendToPython('language', event.newLanguage);
        });

        // Start LSP client only if a server is configured for this language
        if (LSP_PORT > 0) {
            const langExtMap = { 'python': '.py', 'json': '.json', 'yaml': '.yaml',
                                 'javascript': '.js', 'typescript': '.ts' };
            const fileExt = langExtMap[LSP_LANGUAGE] || '.txt';
            lspClient = new LspClient('ws://127.0.0.1:' + LSP_PORT, LSP_LANGUAGE, fileExt);

            lspClient.onReady = () => {
                lspClient.openDocument(editor.getModel().getValue());
                registerLspProviders(LSP_LANGUAGE);

                // Wire up diagnostics → Monaco markers
                lspClient.onDiagnostics = (params) => {
                    const sev = monaco.MarkerSeverity;
                    const markers = params.diagnostics.map(d => ({
                        severity: [, sev.Error, sev.Warning, sev.Info, sev.Hint][d.severity] || sev.Info,
                        message:         d.message,
                        source:          d.source || 'lsp',
                        startLineNumber: d.range.start.line + 1,
                        startColumn:     d.range.start.character + 1,
                        endLineNumber:   d.range.end.line + 1,
                        endColumn:       d.range.end.character + 1,
                    }));
                    monaco.editor.setModelMarkers(editor.getModel(), 'lsp', markers);
                };
            };
        }

        _editorReady = true;
        _finishInit();
    });

    function init() {
        if (!editor) return;
        sendToPython('value',    editor.getModel().getValue());
        sendToPython('language', editor.getModel().getLanguageId());
        sendToPython('theme',    editor._themeService._theme.themeName);
    }

    function sendToPython(name, value) {
        bridge.receive_from_js(name, JSON.stringify(value));
    }

    function updateFromPython(name, value) {
        const data = JSON.parse(value);
        switch (name) {
            case 'value':
                editor.getModel().setValue(data);
                if (lspClient && lspClient._initialized) lspClient.changeDocument(data);
                break;
            case 'language':
                monaco.editor.setModelLanguage(editor.getModel(), data);
                break;
            case 'theme':
                monaco.editor.setTheme(data);
                sendToPython('theme', editor._themeService._theme.themeName);
                break;
            case 'insertAtCursor':
                editor.trigger('bridge', 'type', { text: data });
                break;
            case 'wrapSelection':
                var sel = editor.getSelection();
                var selText = editor.getModel().getValueInRange(sel);
                editor.executeEdits('bridge', [{ range: sel, text: data.prefix + selText + data.suffix }]);
                editor.focus();
                break;
            case 'fileUri':
                if (lspClient) lspClient.changeFileUri(data, editor.getModel().getValue());
                break;
        }
    }

    window.onload = function () {
        new QWebChannel(qt.webChannelTransport, function (channel) {
            _bridgeChannel = channel;
            _bridgeReady = true;
            _finishInit();
        });
    };
    </script>
</body>
</html>
"""


class MonacoLspWidget(QWebEngineView):
    """Monaco editor widget with optional LSP IntelliSense.

    When *language* matches a key in ``_LSP_SERVERS`` (e.g. ``"python"``),
    the corresponding language server is spawned and IntelliSense is active.
    For other languages Monaco still provides syntax highlighting.
    """

    _MAX_BYTES = 5 * 1024 * 1024  # 5 MB

    initialized = Signal()
    textChanged = Signal(str)
    dirtyChanged = Signal(bool)

    def __init__(self, language: str = "python", parent=None):
        super().__init__(parent=parent)
        self._file_path: str | None = None
        self._dirty = False
        self._initial_text: str = ""

        # Decide whether to spawn an LSP server
        self._pylsp_proc = None
        server_cmd = _LSP_SERVERS.get(language)
        if server_cmd is not None:
            self._lsp_port = _find_free_port()
            cmd = [c.replace("{port}", str(self._lsp_port)) for c in server_cmd]
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            # Set VIRTUAL_ENV so jedi ignores CONDA_PREFIX and uses the
            # correct venv (the one running this process).
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = str(Path(sys.executable).parent.parent)
            self._pylsp_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
                env=env,
            )
        else:
            self._lsp_port = 0  # signals JS to skip LSP

        page = MonacoPage(parent=self)
        self.setPage(page)

        html = _HTML.replace("__LSP_PORT__", str(self._lsp_port))
        html = html.replace("__LSP_LANGUAGE__", language)
        base_url = QUrl.fromLocalFile((_PKG_DIR / "index.html").as_posix())
        self.setHtml(html, base_url)

        self._channel = QWebChannel(self)
        self._bridge = EditorBridge()
        self.page().setWebChannel(self._channel)
        self._channel.registerObject("bridge", self._bridge)

        self._bridge.initialized.connect(self.initialized)
        self._bridge.valueChanged.connect(self._on_value_changed)

    # -- dirty tracking ----------------------------------------------------

    def _on_value_changed(self) -> None:
        self.textChanged.emit(self._bridge.value)
        new_dirty = self._bridge.value != self._initial_text
        if new_dirty != self._dirty:
            self._dirty = new_dirty
            self.dirtyChanged.emit(self._dirty)

    @property
    def dirty(self) -> bool:
        return self._dirty

    def _mark_clean(self) -> None:
        self._initial_text = self._bridge.value
        if self._dirty:
            self._dirty = False
            self.dirtyChanged.emit(False)

    # -- file I/O ----------------------------------------------------------

    def load_file(self, path: str) -> None:
        """Read *path* and populate the editor."""
        self._file_path = path
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read(self._MAX_BYTES)
        self._initial_text = text
        self.setText(text)
        self._bridge.send_to_js("fileUri", Path(path).as_uri())
        self._dirty = False

    def save(self, path: str | None = None) -> None:
        """Write editor contents to *path* (defaults to ``load_file`` path)."""
        target = path or self._file_path
        if target is None:
            raise ValueError("No file path specified for save")
        with open(target, "w", encoding="utf-8") as f:
            f.write(self.text())
        self._file_path = target
        self._mark_clean()

    @property
    def file_path(self) -> str | None:
        return self._file_path

    # -- public API --------------------------------------------------------

    def closeEvent(self, event):
        if self._pylsp_proc is not None:
            self._pylsp_proc.terminate()
        super().closeEvent(event)

    def text(self):
        return self._bridge.value

    def setText(self, text):
        self._bridge.send_to_js("value", text)

    def language(self):
        return self._bridge.language

    def setLanguage(self, language):
        self._bridge.send_to_js("language", language)

    def theme(self):
        return self._bridge.theme

    def setTheme(self, theme):
        self._bridge.send_to_js("theme", theme)

    def insertAtCursor(self, text: str) -> None:
        """Insert *text* at the current cursor position."""
        self._bridge.send_to_js("insertAtCursor", text)

    def wrapSelection(self, prefix: str, suffix: str) -> None:
        """Wrap the current selection with *prefix* and *suffix*.

        If no text is selected the markers are inserted at the cursor.
        """
        self._bridge.send_to_js("wrapSelection", {"prefix": prefix, "suffix": suffix})
