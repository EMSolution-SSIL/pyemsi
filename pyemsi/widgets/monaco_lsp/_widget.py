import sys
import os
import json
import subprocess
import socket
import logging
from pathlib import Path

from qtpy.QtCore import Signal, QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWebChannel import QWebChannel

from ._bridge import EditorBridge, MonacoPage
from ._completion import build_completion_item_metadata_js
from ._config import (
    LSP_DEBUG_ENV,
    PY_SEMANTIC_FEATURE_ENV,
    PY_TYPE_CHECKING_MODE_ENV,
    as_js_bool_literal,
    build_python_lsp_launch_command,
    read_bool_env,
    read_str_env,
    resolve_basedpyright_executable,
    semantic_theme_enabled,
)

_PKG_DIR = Path(__file__).parent
LOGGER = logging.getLogger(__name__)

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


_PROJECT_ROOT_MARKERS = ("pyproject.toml", "setup.py", "setup.cfg", ".git")


def _find_project_root(start_path: Path) -> Path:
    """Best-effort project root detection for Python import resolution."""
    current = start_path.resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in _PROJECT_ROOT_MARKERS):
            return candidate
    return current


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
    const PY_SEMANTIC_FEATURE = __PY_SEMANTIC_FEATURE__;
    const PY_SEMANTIC_DEBUG = __PY_SEMANTIC_DEBUG__;
    const PY_TYPE_CHECKING_MODE = '__PY_TYPE_CHECKING_MODE__';
    const LSP_ROOT_URI = __LSP_ROOT_URI__;
    const LSP_WORKSPACE_FOLDERS = __LSP_WORKSPACE_FOLDERS__;
    const PY_EXTRA_PATHS = __PY_EXTRA_PATHS__;

    const DEFAULT_SEMANTIC_TYPES = [
        'namespace', 'type', 'class', 'enum', 'interface', 'struct', 'typeParameter',
        'parameter', 'variable', 'property', 'enumMember', 'event', 'function', 'method',
        'macro', 'keyword', 'modifier', 'comment', 'string', 'number', 'regexp',
        'operator', 'decorator'
    ];
    const DEFAULT_SEMANTIC_MODIFIERS = [
        'declaration', 'definition', 'readonly', 'static', 'deprecated', 'abstract',
        'async', 'modification', 'documentation', 'defaultLibrary'
    ];

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
            this._semanticTokensProvider = null;
            this._semanticLegend = { tokenTypes: [], tokenModifiers: [] };
            this._supportsSemanticTokens = false;
            this._semanticFailureLogged = false;
            this._rootUri = LSP_ROOT_URI || null;
            this._workspaceFolders = Array.isArray(LSP_WORKSPACE_FOLDERS) ? LSP_WORKSPACE_FOLDERS : null;
            this._pythonAnalysisPaths = Array.isArray(PY_EXTRA_PATHS) ? PY_EXTRA_PATHS : [];
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
                const initResult = await this._request('initialize', {
                    processId: null,
                    clientInfo: { name: 'monaco-lsp-client', version: '1.0' },
                    rootUri: this._rootUri,
                    workspaceFolders: this._workspaceFolders,
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
                            publishDiagnostics: { relatedInformation: false },
                            semanticTokens: {
                                dynamicRegistration: false,
                                requests: { full: { delta: false }, range: false },
                                tokenTypes: DEFAULT_SEMANTIC_TYPES,
                                tokenModifiers: DEFAULT_SEMANTIC_MODIFIERS,
                                formats: ['relative'],
                                overlappingTokenSupport: false,
                                multilineTokenSupport: false
                            }
                        }
                    }
                });

                const caps = (initResult && initResult.capabilities) || {};
                this._semanticTokensProvider = caps.semanticTokensProvider || null;

                if (
                    PY_SEMANTIC_FEATURE &&
                    this._languageId === 'python' &&
                    this._semanticTokensProvider &&
                    this._semanticTokensProvider.legend
                ) {
                    const legend = this._semanticTokensProvider.legend;
                    this._semanticLegend = {
                        tokenTypes: Array.isArray(legend.tokenTypes) ? legend.tokenTypes : [],
                        tokenModifiers: Array.isArray(legend.tokenModifiers) ? legend.tokenModifiers : [],
                    };
                    this._supportsSemanticTokens = this._semanticLegend.tokenTypes.length > 0;
                    if (PY_SEMANTIC_DEBUG) {
                        console.info('LSP semanticTokensProvider available', this._semanticLegend);
                    }
                } else {
                    this._supportsSemanticTokens = false;
                    if (PY_SEMANTIC_DEBUG && this._languageId === 'python') {
                        console.info('LSP semanticTokensProvider unavailable; syntax highlighting only');
                    }
                }

                this._notify('initialized', {});
                this._applyPythonConfiguration();

                this._initialized = true;
                if (this.onReady) this.onReady();
            } catch (e) { console.error('LSP init failed:', e.message); }
        }

        supportsSemanticTokens() {
            return this._supportsSemanticTokens;
        }

        semanticLegend() {
            return this._semanticLegend;
        }

        async semanticTokensFull() {
            if (!this._initialized || !this._supportsSemanticTokens) return null;
            try {
                return await this._request('textDocument/semanticTokens/full', {
                    textDocument: { uri: this._fileUri }
                });
            } catch (e) {
                if (!this._semanticFailureLogged) {
                    this._semanticFailureLogged = true;
                    if (PY_SEMANTIC_DEBUG) {
                        console.warn('semanticTokens/full failed; falling back to syntax highlighting:', e.message);
                    }
                }
                return null;
            }
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

        _buildPythonAnalysisSettings() {
            return {
                typeCheckingMode: PY_TYPE_CHECKING_MODE,
                diagnosticMode: 'openFilesOnly',
                extraPaths: this._pythonAnalysisPaths,
            };
        }

        _applyPythonConfiguration() {
            if (this._languageId !== 'python') return;
            this._notify('workspace/didChangeConfiguration', {
                settings: {
                    python: { analysis: this._buildPythonAnalysisSettings() },
                    pyright: { analysis: this._buildPythonAnalysisSettings() },
                    basedpyright: { analysis: this._buildPythonAnalysisSettings() },
                }
            });
        }

        updatePythonAnalysisPaths(paths) {
            if (!Array.isArray(paths)) return;
            this._pythonAnalysisPaths = paths;
            if (this._initialized) {
                this._applyPythonConfiguration();
            }
        }

        changeFileUri(newUri, text) {
            if (this._initialized) {
                this._notify('textDocument/didClose', { textDocument: { uri: this._fileUri } });
            }
            this._fileUri = newUri;
            if (editor) {
                monaco.editor.setModelMarkers(editor.getModel(), 'lsp', []);
            }
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

    function normalizeUriKey(uri) {
        if (!uri) return '';
        let normalized = String(uri);
        try {
            normalized = decodeURIComponent(normalized);
        } catch (_) {
            // Keep original when URI is not percent-encoded.
        }
        normalized = normalized.replace(/\\/g, '/');

        // Canonicalize Windows file URIs to reduce case/encoding mismatches.
        if (normalized.startsWith('file:///') && /^[A-Za-z]:/.test(normalized.slice(8))) {
            normalized = 'file:///' + normalized.slice(8, 9).toLowerCase() + normalized.slice(9);
        }

        return normalized.toLowerCase();
    }

    // ── Editor + Monaco providers ───────────────────────────────────────────────
    var bridge = null;
    var editor = null;
    var lspClient = null;
    var registeredLspLanguages = new Set();
    var registeredSemanticLanguages = new Set();
    var _bridgeChannel = null;   // stash QWebChannel result until editor ready
    var _editorReady = false;    // true once require callback completed
    var _bridgeReady = false;    // true once QWebChannel callback completed

    function resolveThemeName(themeName) {
        if (!(PY_SEMANTIC_FEATURE && LSP_LANGUAGE === 'python')) return themeName;
        if (themeName === 'vs') return 'pyemsi-vs';
        return themeName;
    }

    function defineSemanticTheme() {
        if (!(PY_SEMANTIC_FEATURE && LSP_LANGUAGE === 'python')) return;
        monaco.editor.defineTheme('pyemsi-vs', {
            base: 'vs',
            inherit: true,
            // This bundled monaco version styles semantic tokens through token rules.
            rules: [
                { token: 'class', foreground: '267f99' },
                { token: 'type', foreground: '267f99' },
                { token: 'namespace', foreground: '267f99' },
                { token: 'variable', foreground: '001080' },
                { token: 'parameter', foreground: '001080' },
                { token: 'property', foreground: '0451a5' },
                { token: 'function', foreground: '795E26' },
                { token: 'method', foreground: '795E26' },
            ],
            colors: {},
            semanticHighlighting: true,
        });
    }

    function getDiagnosticsHoverMarkdown(model, position) {
        const markers = monaco.editor.getModelMarkers({
            owner: 'lsp',
            resource: model.uri,
        });
        const matching = markers.filter((m) => {
            const afterStart = position.lineNumber > m.startLineNumber ||
                (position.lineNumber === m.startLineNumber && position.column >= m.startColumn);
            const beforeEnd = position.lineNumber < m.endLineNumber ||
                (position.lineNumber === m.endLineNumber && position.column <= m.endColumn);
            return afterStart && beforeEnd;
        });
        if (matching.length === 0) return [];
        return matching.map((m) => {
            const source = m.source ? ` (${m.source})` : '';
            return { value: `**${m.message}**${source}` };
        });
    }

    // Called after BOTH editor and bridge are available so that
    // queued Python→JS messages are only flushed when the editor exists.
    function _finishInit() {
        if (!_editorReady || !_bridgeReady) return;
        bridge = _bridgeChannel.objects.bridge;
        bridge.sendDataChanged.connect(updateFromPython);
        bridge.init();   // flush queue - editor guaranteed non-null
        init();
    }

    function registerLspProviders(langId) {
        if (registeredLspLanguages.has(langId)) return;
        registeredLspLanguages.add(langId);

        // Completion
        monaco.languages.registerCompletionItemProvider(langId, {
            triggerCharacters: ['.'],
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
__LSP_COMPLETION_ITEM_METADATA__
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
                const contents = getDiagnosticsHoverMarkdown(model, position);

                if (lspClient && lspClient._initialized) {
                    const result = await lspClient.hover(position.lineNumber - 1, position.column - 1);
                    if (result && result.contents) {
                        const raw = Array.isArray(result.contents) ? result.contents : [result.contents];
                        contents.push(...raw.map(c => ({ value: extractDocString(c) })));
                    }
                }

                if (contents.length === 0) return null;
                return { contents };
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

    function registerSemanticProvider(langId) {
        if (registeredSemanticLanguages.has(langId)) return;
        if (!lspClient || !lspClient.supportsSemanticTokens()) return;

        const legend = lspClient.semanticLegend();
        if (!legend || !Array.isArray(legend.tokenTypes) || legend.tokenTypes.length === 0) {
            return;
        }

        registeredSemanticLanguages.add(langId);
        monaco.languages.registerDocumentSemanticTokensProvider(langId, {
            getLegend: () => legend,
            provideDocumentSemanticTokens: async () => {
                if (!lspClient || !lspClient._initialized) return { data: new Uint32Array(0) };
                const response = await lspClient.semanticTokensFull();
                if (!response || !Array.isArray(response.data)) return { data: new Uint32Array(0) };
                return {
                    resultId: response.resultId,
                    data: new Uint32Array(response.data),
                };
            },
            releaseDocumentSemanticTokens: () => {},
        });
    }

    require.config({ paths: { 'vs': 'monaco-editor/min/vs' } });

    require(['vs/editor/editor.main'], () => {
        defineSemanticTheme();

        editor = monaco.editor.create(document.getElementById('container'), {
            fontFamily: 'Consolas, "Courier New", monospace',
            automaticLayout: true,
            theme: resolveThemeName('vs'),
            'semanticHighlighting.enabled': PY_SEMANTIC_FEATURE && LSP_LANGUAGE === 'python',
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
                registerSemanticProvider(LSP_LANGUAGE);

                // Wire up diagnostics → Monaco markers
                lspClient.onDiagnostics = (params) => {
                    // Only apply diagnostics for the active LSP document.
                    if (!params || normalizeUriKey(params.uri) !== normalizeUriKey(lspClient._fileUri)) {
                        if (PY_SEMANTIC_DEBUG && params && params.uri) {
                            console.info('Ignoring diagnostics for non-active URI', params.uri, lspClient._fileUri);
                        }
                        return;
                    }

                    const sev = monaco.MarkerSeverity;
                    const diagnostics = (params.diagnostics || []).filter((d) => {
                        // Keep only errors and warnings to avoid excessive strictness.
                        const lspSeverity = d.severity || 2;
                        return lspSeverity <= 2;
                    });

                    const markers = diagnostics.map(d => ({
                        severity: [, sev.Error, sev.Warning, sev.Info, sev.Hint][d.severity] || sev.Info,
                        message:         d.message,
                        source:          d.source || 'lsp',
                        startLineNumber: d.range.start.line + 1,
                        startColumn:     d.range.start.character + 1,
                        endLineNumber:   d.range.end.line + 1,
                        endColumn:       Math.max(d.range.start.character + 2, d.range.end.character + 1),
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
                monaco.editor.setTheme(resolveThemeName(data));
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
            case 'pythonAnalysisPaths':
                if (lspClient) lspClient.updatePythonAnalysisPaths(data);
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

    def __init__(
        self,
        language: str = "python",
        parent=None,
        enable_python_semantic_highlighting: bool = False,
    ):
        super().__init__(parent=parent)
        self._language = language
        self._file_path: str | None = None
        self._dirty = False
        self._initial_text: str = ""
        self._semantic_requested = enable_python_semantic_highlighting
        self._semantic_enabled = semantic_theme_enabled(
            language,
            semantic_requested=self._semantic_requested,
        )
        self._python_analysis_paths: list[str] = []
        if language == "python":
            self._python_analysis_paths = [str(_find_project_root(Path.cwd()))]

        # Decide whether to spawn an LSP server
        self._pylsp_proc = None
        self._lsp_mode = "none"
        server_cmd = _LSP_SERVERS.get(language)
        if server_cmd is not None:
            self._lsp_port = _find_free_port()
            if language == "python":
                command, mode = self._resolve_python_server_command()
            else:
                command = [c.replace("{port}", str(self._lsp_port)) for c in server_cmd]
                mode = "legacy"

            self._start_lsp_process(command=command, mode=mode)
        else:
            self._lsp_port = 0  # signals JS to skip LSP

        page = MonacoPage(parent=self)
        self.setPage(page)

        html = _HTML.replace("__LSP_PORT__", str(self._lsp_port))
        html = html.replace("__LSP_LANGUAGE__", language)
        html = html.replace("__PY_SEMANTIC_FEATURE__", as_js_bool_literal(self._semantic_enabled))
        html = html.replace(
            "__PY_SEMANTIC_DEBUG__",
            as_js_bool_literal(read_bool_env(LSP_DEBUG_ENV, default=False)),
        )
        html = html.replace(
            "__PY_TYPE_CHECKING_MODE__",
            read_str_env(PY_TYPE_CHECKING_MODE_ENV, default="basic"),
        )
        root_uri = Path(self._python_analysis_paths[0]).as_uri() if self._python_analysis_paths else None
        workspace_folders = [{"uri": root_uri, "name": Path(self._python_analysis_paths[0]).name}] if root_uri else None
        html = html.replace("__LSP_ROOT_URI__", json.dumps(root_uri))
        html = html.replace("__LSP_WORKSPACE_FOLDERS__", json.dumps(workspace_folders))
        html = html.replace("__PY_EXTRA_PATHS__", json.dumps(self._python_analysis_paths))
        html = html.replace("__LSP_COMPLETION_ITEM_METADATA__", build_completion_item_metadata_js())
        base_url = QUrl.fromLocalFile((_PKG_DIR / "index.html").as_posix())
        self.setHtml(html, base_url)

        self._channel = QWebChannel(self)
        self._bridge = EditorBridge()
        self.page().setWebChannel(self._channel)
        self._channel.registerObject("bridge", self._bridge)

        self._bridge.initialized.connect(self.initialized)
        self._bridge.valueChanged.connect(self._on_value_changed)

    def _resolve_python_server_command(self) -> tuple[list[str], str]:
        basedpyright_executable = resolve_basedpyright_executable(python_executable=sys.executable)
        command, mode = build_python_lsp_launch_command(
            self._lsp_port,
            semantic_requested=self._semantic_requested,
            basedpyright_executable=basedpyright_executable,
        )
        if (
            mode == "legacy-pylsp"
            and self._semantic_requested
            and read_bool_env(
                PY_SEMANTIC_FEATURE_ENV,
                default=False,
            )
        ):
            LOGGER.warning(
                "Python semantic highlighting requested but basedpyright-langserver was not found; "
                "falling back to legacy pylsp WebSocket mode"
            )
        return command, mode

    def _start_lsp_process(self, command: list[str], mode: str) -> None:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(Path(sys.executable).parent.parent)

        try:
            self._pylsp_proc = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
                env=env,
            )
            self._lsp_mode = mode
            if read_bool_env(LSP_DEBUG_ENV, default=False):
                LOGGER.debug("Started Monaco LSP process mode=%s command=%s", mode, command)
        except OSError:
            self._pylsp_proc = None
            self._lsp_mode = "none"
            LOGGER.exception("Failed to start Monaco LSP process for mode=%s", mode)
            if mode == "relay-basedpyright":
                # Fail open to legacy behavior if the relay path cannot be launched.
                fallback = [
                    sys.executable,
                    "-m",
                    "pylsp",
                    "--ws",
                    "--port",
                    str(self._lsp_port),
                ]
                self._start_lsp_process(command=fallback, mode="legacy-pylsp")

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
        resolved_path = str(Path(path).resolve())
        self._file_path = resolved_path
        with open(resolved_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read(self._MAX_BYTES)
        self._initial_text = text
        self.setText(text)
        self._update_python_analysis_paths(resolved_path)
        self._bridge.send_to_js("fileUri", Path(resolved_path).as_uri())
        self._dirty = False

    def _update_python_analysis_paths(self, path: str) -> None:
        if self._language != "python":
            return
        project_root = _find_project_root(Path(path))
        paths = [str(project_root)]
        if paths == self._python_analysis_paths:
            return
        self._python_analysis_paths = paths
        self._bridge.send_to_js("pythonAnalysisPaths", paths)

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
