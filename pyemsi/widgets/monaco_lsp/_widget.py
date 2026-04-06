import sys
import os
import json
import subprocess
import socket
import logging
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from qtpy.QtCore import Signal, QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWebChannel import QWebChannel
from qtpy.QtWidgets import QFileDialog, QMessageBox

from ..file_sync import DocumentSyncState, FileSyncController
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


def normalize_uri_key(uri: str | None) -> str:
    if not uri:
        return ""

    normalized = str(uri)
    try:
        normalized = unquote(normalized)
    except Exception:
        pass

    normalized = normalized.replace("\\", "/")
    if normalized.startswith("file:///") and len(normalized) > 9 and normalized[8].isalpha() and normalized[9] == ":":
        normalized = f"file:///{normalized[8].lower()}{normalized[9:]}"
    return normalized.lower()


def _to_monaco_range(range_data: dict[str, Any] | None) -> dict[str, int]:
    if not isinstance(range_data, dict):
        return {
            "startLineNumber": 1,
            "startColumn": 1,
            "endLineNumber": 1,
            "endColumn": 1,
        }

    start = range_data.get("start") or {}
    end = range_data.get("end") or start
    return {
        "startLineNumber": int(start.get("line", 0)) + 1,
        "startColumn": int(start.get("character", 0)) + 1,
        "endLineNumber": int(end.get("line", 0)) + 1,
        "endColumn": int(end.get("character", 0)) + 1,
    }


def _range_contains_position(range_data: dict[str, int], position: dict[str, int]) -> bool:
    start = (range_data["startLineNumber"], range_data["startColumn"])
    end = (range_data["endLineNumber"], range_data["endColumn"])
    current = (position["lineNumber"], position["column"])
    return start <= current <= end


def _range_contains_range(outer: dict[str, int], inner: dict[str, int]) -> bool:
    outer_start = (outer["startLineNumber"], outer["startColumn"])
    outer_end = (outer["endLineNumber"], outer["endColumn"])
    inner_start = (inner["startLineNumber"], inner["startColumn"])
    inner_end = (inner["endLineNumber"], inner["endColumn"])
    return outer_start <= inner_start and outer_end >= inner_end


def _normalize_document_symbol(symbol: dict[str, Any]) -> dict[str, Any]:
    children = symbol.get("children")
    return {
        "name": symbol.get("name") or "",
        "detail": symbol.get("detail") or "",
        "kind": int(symbol.get("kind", 13)),
        "tags": list(symbol.get("tags") or []),
        "range": _to_monaco_range(symbol.get("range")),
        "selectionRange": _to_monaco_range(symbol.get("selectionRange") or symbol.get("range")),
        "children": [_normalize_document_symbol(child) for child in children if isinstance(child, dict)]
        if isinstance(children, list)
        else [],
    }


def _normalize_symbol_information(symbol: dict[str, Any]) -> dict[str, Any] | None:
    location = symbol.get("location")
    if not isinstance(location, dict):
        return None
    return {
        "name": symbol.get("name") or "",
        "detail": "",
        "kind": int(symbol.get("kind", 13)),
        "tags": list(symbol.get("tags") or []),
        "range": _to_monaco_range(location.get("range")),
        "selectionRange": _to_monaco_range(location.get("range")),
        "children": [],
    }


def normalize_lsp_document_symbols(symbols: Any, active_uri: str | None) -> list[dict[str, Any]]:
    if not isinstance(symbols, list) or not symbols:
        return []

    if isinstance(symbols[0], dict) and "location" not in symbols[0]:
        return [_normalize_document_symbol(symbol) for symbol in symbols if isinstance(symbol, dict)]

    normalized_active_uri = normalize_uri_key(active_uri)
    flat_symbols: list[dict[str, Any]] = []
    for symbol in symbols:
        if not isinstance(symbol, dict):
            continue
        location = symbol.get("location")
        if not isinstance(location, dict):
            continue
        symbol_uri = normalize_uri_key(location.get("uri"))
        if normalized_active_uri and symbol_uri and symbol_uri != normalized_active_uri:
            continue
        converted = _normalize_symbol_information(symbol)
        if converted is not None:
            flat_symbols.append(converted)

    flat_symbols.sort(
        key=lambda item: (
            item["range"]["startLineNumber"],
            item["range"]["startColumn"],
            -item["range"]["endLineNumber"],
            -item["range"]["endColumn"],
            item["name"],
        )
    )

    roots: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    for symbol in flat_symbols:
        while stack and not _range_contains_range(stack[-1]["range"], symbol["range"]):
            stack.pop()
        if stack:
            stack[-1]["children"].append(symbol)
        else:
            roots.append(symbol)
        stack.append(symbol)
    return roots


def find_containing_symbol_trail(
    symbols: list[dict[str, Any]],
    position: dict[str, int],
) -> list[dict[str, Any]]:
    def _find(symbol: dict[str, Any]) -> list[dict[str, Any]]:
        if not _range_contains_position(symbol["range"], position):
            return []
        for child in symbol.get("children") or []:
            child_trail = _find(child)
            if child_trail:
                return [symbol, *child_trail]
        return [symbol]

    for symbol in symbols:
        trail = _find(symbol)
        if trail:
            return trail
    return []


def build_symbol_breadcrumb_items(
    symbols: list[dict[str, Any]],
    position: dict[str, int],
) -> list[dict[str, Any]]:
    trail = find_containing_symbol_trail(symbols, position)
    if not trail:
        return []

    items: list[dict[str, Any]] = []
    siblings: list[dict[str, Any]] = symbols
    for index, symbol in enumerate(trail):
        level_siblings = [candidate for candidate in siblings if isinstance(candidate, dict)]
        children = symbol.get("children")
        level_children = (
            [candidate for candidate in children if isinstance(candidate, dict)] if isinstance(children, list) else []
        )
        items.append(
            {
                "symbol": symbol,
                "siblings": level_siblings,
                "children": level_children,
                "isLeaf": index == len(trail) - 1,
            }
        )
        siblings = children if isinstance(children, list) else []
    return items


def should_show_breadcrumbs(
    active_language: str | None,
    lsp_language: str | None,
    has_document_symbol_support: bool,
    symbols: list[dict[str, Any]] | None,
) -> bool:
    if not has_document_symbol_support:
        return False
    if not active_language or active_language != lsp_language:
        return False
    return bool(symbols)


def build_json_document_symbols(symbols: Any) -> list[dict[str, Any]]:
    if not isinstance(symbols, list) or not symbols:
        return []
    return [_normalize_document_symbol(symbol) for symbol in symbols if isinstance(symbol, dict)]


_HTML = r"""<!DOCTYPE html>
<style>
    * { padding: 0; margin: 0; }
    :root {
        --breadcrumb-font-family: "Consolas", "Cascadia Code", "JetBrains Mono", "Fira Code", "Courier New", monospace;
        --breadcrumb-font-size: 12px;
        --breadcrumb-line-height: 1.35;
        --breadcrumb-text: #1f2937;
        --breadcrumb-muted: #5b6b80;
        --breadcrumb-accent: #1d4ed8;
        --breadcrumb-hover-bg: rgba(37, 99, 235, 0.10);
        --breadcrumb-active-bg: linear-gradient(180deg, rgba(37, 99, 235, 0.14), rgba(37, 99, 235, 0.08));
        --breadcrumb-active-border: rgba(37, 99, 235, 0.22);
        --breadcrumb-panel-border: rgba(148, 163, 184, 0.35);
        --breadcrumb-panel-bg: rgba(255, 255, 255, 0.98);
        --breadcrumb-radius: 8px;
        --breadcrumb-panel-radius: 12px;
        --breadcrumb-badge-bg: rgba(37, 99, 235, 0.10);
    }
    html, body { min-height: 100% !important; height: 100%; overflow: hidden; }
    body {
        display: flex;
        flex-direction: column;
        background: #ffffff;
        color: var(--breadcrumb-text);
    }
    #breadcrumbs {
        display: none;
        align-items: center;
        gap: 2px;
        min-height: 16px;
        padding: 0px 3px;
        border-bottom: 1px solid #d6dce5;
        background: white;
        font-family: var(--breadcrumb-font-family);
        font-size: var(--breadcrumb-font-size);
        font-weight: 400;
        line-height: var(--breadcrumb-line-height);
        letter-spacing: 0.01em;
        white-space: nowrap;
        overflow-x: auto;
        overflow-y: hidden;
    }
    #breadcrumbs.visible { display: flex; }
    .breadcrumb-item {
        position: relative;
        display: inline-flex;
        align-items: center;
        min-width: 0;
        font: inherit;
    }
    .breadcrumb-segment-group {
        display: inline-flex;
        align-items: center;
        border: 1px solid transparent;
        border-radius: var(--breadcrumb-radius);
        transition: background 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
    }
    .breadcrumb-segment-group.open {
        background: var(--breadcrumb-active-bg);
        border-color: var(--breadcrumb-active-border);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
    }
    .breadcrumb-segment {
        appearance: none;
        border: 0;
        background: transparent;
        border-radius: calc(var(--breadcrumb-radius) - 2px);
        color: var(--breadcrumb-text);
        cursor: pointer;
        font: inherit;
        line-height: inherit;
        padding: 0px 4px;
    }
    .breadcrumb-segment:hover,
    .breadcrumb-segment:focus-visible {
        background: var(--breadcrumb-hover-bg);
        color: var(--breadcrumb-accent);
        outline: none;
    }
    .breadcrumb-segment-label {
        max-width: 220px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .breadcrumb-separator {
        color: var(--breadcrumb-muted);
        font-size: 14px;
        padding: 0;
        user-select: none;
    }
    #breadcrumb-menu {
        display: none;
        position: fixed;
        z-index: 1000;
        min-width: 180px;
        max-width: min(320px, calc(100vw - 16px));
        max-height: min(320px, calc(100vh - 16px));
        overflow: auto;
        border: 1px solid var(--breadcrumb-panel-border);
        border-radius: var(--breadcrumb-panel-radius);
        background: var(--breadcrumb-panel-bg);
        backdrop-filter: blur(14px);
        color: var(--breadcrumb-text);
        font-family: var(--breadcrumb-font-family);
        font-size: var(--breadcrumb-font-size);
        font-weight: 400;
        line-height: var(--breadcrumb-line-height);
        letter-spacing: 0.01em;
        padding: 2px;
    }
    #breadcrumb-menu.visible {
        display: block;
    }
    .breadcrumb-menu-surface {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .breadcrumb-menu-item {
        display: flex;
        width: 100%;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        appearance: none;
        border: 0;
        border-radius: var(--breadcrumb-radius);
        background: transparent;
        color: var(--breadcrumb-text);
        cursor: pointer;
        font: inherit;
        line-height: inherit;
        padding: 2px 4px;
        text-align: left;
        transition: background 120ms ease, color 120ms ease;
    }
    .breadcrumb-menu-item:hover,
    .breadcrumb-menu-item:focus-visible {
        background: var(--breadcrumb-hover-bg);
        color: var(--breadcrumb-accent);
        outline: none;
    }
    .breadcrumb-menu-item.active {
        background: var(--breadcrumb-active-bg);
        color: var(--breadcrumb-accent);
    }
    .breadcrumb-menu-item-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font: inherit;
    }
    .breadcrumb-menu-item-meta {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        flex: 0 0 auto;
        margin-left: 12px;
    }
    .breadcrumb-menu-item-badge {
        border-radius: 999px;
        background: var(--breadcrumb-badge-bg);
        color: var(--breadcrumb-accent);
        font-family: var(--breadcrumb-font-family);
        font-size: 10px;
        font-weight: 400;
        letter-spacing: 0.04em;
        line-height: 1.2;
        padding: 2px 6px;
        text-transform: uppercase;
    }
    .breadcrumb-menu-item-detail {
        color: var(--breadcrumb-muted);
        flex: 0 0 auto;
        font-family: var(--breadcrumb-font-family);
        font-size: 11px;
        line-height: 1.2;
    }
    .monaco-editor .parameter-hints-widget.pyemsi-prefer-top {
        z-index: 41;
    }
    #container {
        width: 100%;
        flex: 1 1 auto;
        overflow: hidden;
        position: relative;
    }
</style>
<html>
<head>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
</head>
<body>
    <div id="breadcrumbs" aria-label="Document breadcrumbs"></div>
    <div id="breadcrumb-menu" aria-label="Breadcrumb sibling symbols"></div>
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
            this._documentSymbolProvider = null;
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
                            documentSymbol: {
                                dynamicRegistration: false,
                                hierarchicalDocumentSymbolSupport: true,
                                tagSupport: { valueSet: [1] }
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
                this._documentSymbolProvider = caps.documentSymbolProvider || null;

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

        supportsDocumentSymbols() {
            return !!this._documentSymbolProvider;
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

        async documentSymbols() {
            if (!this._initialized || !this.supportsDocumentSymbols()) return [];
            try {
                const result = await this._request('textDocument/documentSymbol', {
                    textDocument: { uri: this._fileUri }
                });
                return Array.isArray(result) ? result : [];
            } catch (_) {
                return [];
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

    function toMonacoRange(range) {
        if (!range || !range.start) {
            return {
                startLineNumber: 1,
                startColumn: 1,
                endLineNumber: 1,
                endColumn: 1,
            };
        }
        const end = range.end || range.start;
        return {
            startLineNumber: range.start.line + 1,
            startColumn: range.start.character + 1,
            endLineNumber: end.line + 1,
            endColumn: end.character + 1,
        };
    }

    function rangeContainsPosition(range, position) {
        const startsBefore = position.lineNumber > range.startLineNumber ||
            (position.lineNumber === range.startLineNumber && position.column >= range.startColumn);
        const endsAfter = position.lineNumber < range.endLineNumber ||
            (position.lineNumber === range.endLineNumber && position.column <= range.endColumn);
        return startsBefore && endsAfter;
    }

    function rangeContainsRange(outer, inner) {
        const startsBefore = inner.startLineNumber > outer.startLineNumber ||
            (inner.startLineNumber === outer.startLineNumber && inner.startColumn >= outer.startColumn);
        const endsAfter = inner.endLineNumber < outer.endLineNumber ||
            (inner.endLineNumber === outer.endLineNumber && inner.endColumn <= outer.endColumn);
        return startsBefore && endsAfter;
    }

    function normalizeDocumentSymbol(symbol) {
        const children = Array.isArray(symbol.children) ? symbol.children.map(normalizeDocumentSymbol) : [];
        return {
            name: symbol.name || '',
            detail: symbol.detail || '',
            kind: symbol.kind || monaco.languages.SymbolKind.Variable,
            tags: Array.isArray(symbol.tags) ? symbol.tags : [],
            range: toMonacoRange(symbol.range),
            selectionRange: toMonacoRange(symbol.selectionRange || symbol.range),
            children,
        };
    }

    function normalizeSymbolInformation(symbol) {
        if (!symbol || !symbol.location) return null;
        return {
            name: symbol.name || '',
            detail: '',
            kind: symbol.kind || monaco.languages.SymbolKind.Variable,
            tags: Array.isArray(symbol.tags) ? symbol.tags : [],
            range: toMonacoRange(symbol.location.range),
            selectionRange: toMonacoRange(symbol.location.range),
            children: [],
        };
    }

    function normalizeLspDocumentSymbols(symbols, activeUri) {
        if (!Array.isArray(symbols) || symbols.length === 0) return [];

        if (!symbols[0] || !Object.prototype.hasOwnProperty.call(symbols[0], 'location')) {
            return symbols.map((symbol) => normalizeDocumentSymbol(symbol));
        }

        const normalizedActiveUri = normalizeUriKey(activeUri);
        const flatSymbols = symbols
            .filter((symbol) => symbol && symbol.location)
            .filter((symbol) => {
                const symbolUri = normalizeUriKey(symbol.location.uri);
                return !normalizedActiveUri || !symbolUri || symbolUri === normalizedActiveUri;
            })
            .map((symbol) => normalizeSymbolInformation(symbol))
            .filter(Boolean)
            .sort((left, right) => {
                if (left.range.startLineNumber !== right.range.startLineNumber) {
                    return left.range.startLineNumber - right.range.startLineNumber;
                }
                if (left.range.startColumn !== right.range.startColumn) {
                    return left.range.startColumn - right.range.startColumn;
                }
                if (left.range.endLineNumber !== right.range.endLineNumber) {
                    return right.range.endLineNumber - left.range.endLineNumber;
                }
                if (left.range.endColumn !== right.range.endColumn) {
                    return right.range.endColumn - left.range.endColumn;
                }
                return left.name.localeCompare(right.name);
            });

        const roots = [];
        const stack = [];
        flatSymbols.forEach((symbol) => {
            while (stack.length > 0 && !rangeContainsRange(stack[stack.length - 1].range, symbol.range)) {
                stack.pop();
            }
            if (stack.length > 0) {
                stack[stack.length - 1].children.push(symbol);
            } else {
                roots.push(symbol);
            }
            stack.push(symbol);
        });
        return roots;
    }

    function findContainingSymbolTrail(position, symbols) {
        function findInSymbol(symbol) {
            if (!rangeContainsPosition(symbol.range, position)) return [];
            const children = Array.isArray(symbol.children) ? symbol.children : [];
            for (const child of children) {
                const trail = findInSymbol(child);
                if (trail.length > 0) {
                    return [symbol].concat(trail);
                }
            }
            return [symbol];
        }

        for (const symbol of symbols || []) {
            const trail = findInSymbol(symbol);
            if (trail.length > 0) {
                return trail;
            }
        }
        return [];
    }

    function buildSymbolBreadcrumbItems(position, symbols) {
        const trail = findContainingSymbolTrail(position, symbols);
        if (trail.length === 0) return [];

        const items = [];
        let siblings = Array.isArray(symbols) ? symbols : [];
        trail.forEach((symbol, index) => {
            const levelSiblings = siblings.filter(Boolean);
            const levelChildren = Array.isArray(symbol.children) ? symbol.children.filter(Boolean) : [];
            items.push({
                symbol,
                siblings: levelSiblings,
                children: levelChildren,
                isLeaf: index === trail.length - 1,
            });
            siblings = Array.isArray(symbol.children) ? symbol.children : [];
        });
        return items;
    }

    function buildLineStarts(text) {
        const starts = [0];
        for (let index = 0; index < text.length; index += 1) {
            const ch = text.charCodeAt(index);
            if (ch === 13) {
                if (index + 1 < text.length && text.charCodeAt(index + 1) === 10) {
                    index += 1;
                }
                starts.push(index + 1);
            } else if (ch === 10) {
                starts.push(index + 1);
            }
        }
        return starts;
    }

    function offsetToMonacoPosition(offset, lineStarts) {
        const clamped = Math.max(0, offset);
        let low = 0;
        let high = lineStarts.length - 1;
        while (low <= high) {
            const mid = Math.floor((low + high) / 2);
            if (lineStarts[mid] <= clamped) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        const lineIndex = Math.max(0, high);
        return {
            lineNumber: lineIndex + 1,
            column: clamped - lineStarts[lineIndex] + 1,
        };
    }

    function offsetsToMonacoRange(startOffset, endOffset, lineStarts) {
        const safeStart = Math.max(0, startOffset);
        const safeEnd = Math.max(safeStart + 1, endOffset);
        const start = offsetToMonacoPosition(safeStart, lineStarts);
        const end = offsetToMonacoPosition(safeEnd, lineStarts);
        return {
            startLineNumber: start.lineNumber,
            startColumn: start.column,
            endLineNumber: end.lineNumber,
            endColumn: end.column,
        };
    }

    function buildJsonDocumentSymbols(text) {
        const source = typeof text === 'string' ? text : '';
        if (!source.trim()) {
            return [];
        }

        const lineStarts = buildLineStarts(source);
        let index = 0;

        function isWhitespace(charCode) {
            return charCode === 32 || charCode === 9 || charCode === 10 || charCode === 13;
        }

        function skipTrivia() {
            while (index < source.length) {
                const charCode = source.charCodeAt(index);
                if (isWhitespace(charCode)) {
                    index += 1;
                    continue;
                }

                if (charCode === 47 && index + 1 < source.length) {
                    const nextCode = source.charCodeAt(index + 1);
                    if (nextCode === 47) {
                        index += 2;
                        while (index < source.length) {
                            const lineCode = source.charCodeAt(index);
                            if (lineCode === 10 || lineCode === 13) {
                                break;
                            }
                            index += 1;
                        }
                        continue;
                    }
                    if (nextCode === 42) {
                        index += 2;
                        while (index + 1 < source.length) {
                            if (source.charCodeAt(index) === 42 && source.charCodeAt(index + 1) === 47) {
                                index += 2;
                                break;
                            }
                            index += 1;
                        }
                        continue;
                    }
                }

                break;
            }
        }

        function parseStringToken() {
            if (source.charCodeAt(index) !== 34) {
                return null;
            }

            const start = index;
            index += 1;
            let value = '';
            while (index < source.length) {
                const charCode = source.charCodeAt(index);
                if (charCode === 34) {
                    const end = index + 1;
                    index = end;
                    return {
                        value,
                        start,
                        end,
                        contentStart: Math.min(start + 1, end - 1),
                        contentEnd: Math.max(start + 1, end - 1),
                    };
                }
                if (charCode === 92) {
                    if (index + 1 >= source.length) {
                        return null;
                    }
                    const escapeCode = source.charCodeAt(index + 1);
                    switch (escapeCode) {
                        case 34:
                            value += '"';
                            break;
                        case 92:
                            value += '\\';
                            break;
                        case 47:
                            value += '/';
                            break;
                        case 98:
                            value += '\b';
                            break;
                        case 102:
                            value += '\f';
                            break;
                        case 110:
                            value += '\n';
                            break;
                        case 114:
                            value += '\r';
                            break;
                        case 116:
                            value += '\t';
                            break;
                        case 117: {
                            const hex = source.slice(index + 2, index + 6);
                            if (!/^[0-9a-fA-F]{4}$/.test(hex)) {
                                return null;
                            }
                            value += String.fromCharCode(parseInt(hex, 16));
                            index += 4;
                            break;
                        }
                        default:
                            value += source.charAt(index + 1);
                            break;
                    }
                    index += 2;
                    continue;
                }

                value += source.charAt(index);
                index += 1;
            }

            return null;
        }

        function parseNumberToken() {
            const match = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/.exec(source.slice(index));
            if (!match) {
                return null;
            }
            const start = index;
            index += match[0].length;
            return {
                type: 'number',
                start,
                end: index,
                selectionStart: start,
                selectionEnd: index,
                children: [],
            };
        }

        function parseKeyword(keyword, type) {
            if (!source.startsWith(keyword, index)) {
                return null;
            }
            const start = index;
            index += keyword.length;
            return {
                type,
                start,
                end: index,
                selectionStart: start,
                selectionEnd: index,
                children: [],
            };
        }

        function buildSymbolKind(type, isProperty) {
            const kinds = monaco.languages.SymbolKind;
            if (isProperty) {
                return kinds.Property;
            }
            switch (type) {
                case 'object':
                    return kinds.Object;
                case 'array':
                    return kinds.Array;
                case 'string':
                    return kinds.String;
                case 'number':
                    return kinds.Number;
                case 'boolean':
                    return kinds.Boolean;
                case 'null':
                    return kinds.Null;
                default:
                    return kinds.Variable;
            }
        }

        function buildDetail(type) {
            if (type === 'object' || type === 'array') {
                return type;
            }
            return '';
        }

        function createSymbol(name, type, rangeStart, rangeEnd, selectionStart, selectionEnd, children, isProperty) {
            return {
                name,
                detail: buildDetail(type),
                kind: buildSymbolKind(type, isProperty),
                tags: [],
                range: offsetsToMonacoRange(rangeStart, rangeEnd, lineStarts),
                selectionRange: offsetsToMonacoRange(selectionStart, selectionEnd, lineStarts),
                children: Array.isArray(children) ? children : [],
            };
        }

        function parseValue() {
            skipTrivia();
            if (index >= source.length) {
                return null;
            }

            const charCode = source.charCodeAt(index);
            if (charCode === 123) {
                return parseObject();
            }
            if (charCode === 91) {
                return parseArray();
            }
            if (charCode === 34) {
                const token = parseStringToken();
                if (!token) {
                    return null;
                }
                return {
                    type: 'string',
                    start: token.start,
                    end: token.end,
                    selectionStart: token.contentStart,
                    selectionEnd: token.contentEnd,
                    children: [],
                };
            }
            if (charCode === 116) {
                return parseKeyword('true', 'boolean');
            }
            if (charCode === 102) {
                return parseKeyword('false', 'boolean');
            }
            if (charCode === 110) {
                return parseKeyword('null', 'null');
            }
            return parseNumberToken();
        }

        function parseObject() {
            const start = index;
            index += 1;
            const children = [];

            while (index <= source.length) {
                skipTrivia();
                if (index >= source.length) {
                    return null;
                }
                if (source.charCodeAt(index) === 125) {
                    index += 1;
                    return {
                        type: 'object',
                        start,
                        end: index,
                        selectionStart: start,
                        selectionEnd: start + 1,
                        children,
                    };
                }

                const keyToken = parseStringToken();
                if (!keyToken) {
                    return null;
                }

                skipTrivia();
                if (source.charCodeAt(index) !== 58) {
                    return null;
                }
                index += 1;

                const valueNode = parseValue();
                if (!valueNode) {
                    return null;
                }

                const selectionEnd = Math.max(keyToken.contentStart + 1, keyToken.contentEnd);
                children.push(
                    createSymbol(
                        keyToken.value,
                        valueNode.type,
                        keyToken.start,
                        valueNode.end,
                        keyToken.contentStart,
                        selectionEnd,
                        valueNode.children,
                        true,
                    )
                );

                skipTrivia();
                if (source.charCodeAt(index) === 44) {
                    index += 1;
                    skipTrivia();
                    if (source.charCodeAt(index) === 125) {
                        continue;
                    }
                    continue;
                }
                if (source.charCodeAt(index) === 125) {
                    continue;
                }
                return null;
            }

            return null;
        }

        function parseArray() {
            const start = index;
            index += 1;
            const children = [];
            let itemIndex = 0;

            while (index <= source.length) {
                skipTrivia();
                if (index >= source.length) {
                    return null;
                }
                if (source.charCodeAt(index) === 93) {
                    index += 1;
                    return {
                        type: 'array',
                        start,
                        end: index,
                        selectionStart: start,
                        selectionEnd: start + 1,
                        children,
                    };
                }

                const valueNode = parseValue();
                if (!valueNode) {
                    return null;
                }

                const selectionEnd = Math.max(valueNode.selectionStart + 1, valueNode.selectionEnd);
                children.push(
                    createSymbol(
                        `[${itemIndex}]`,
                        valueNode.type,
                        valueNode.start,
                        valueNode.end,
                        valueNode.selectionStart,
                        selectionEnd,
                        valueNode.children,
                        false,
                    )
                );
                itemIndex += 1;

                skipTrivia();
                if (source.charCodeAt(index) === 44) {
                    index += 1;
                    skipTrivia();
                    if (source.charCodeAt(index) === 93) {
                        continue;
                    }
                    continue;
                }
                if (source.charCodeAt(index) === 93) {
                    continue;
                }
                return null;
            }

            return null;
        }

        try {
            const root = parseValue();
            if (!root) {
                return [];
            }
            skipTrivia();
            if (index < source.length) {
                return [];
            }
            return Array.isArray(root.children) ? root.children : [];
        } catch (_) {
            return [];
        }
    }

    // ── Editor + Monaco providers ───────────────────────────────────────────────
    var bridge = null;
    var editor = null;
    var lspClient = null;
    var registeredLspLanguages = new Set();
    var registeredSemanticLanguages = new Set();
    var registeredDocumentSymbolLanguages = new Set();
    var _bridgeChannel = null;   // stash QWebChannel result until editor ready
    var _editorReady = false;    // true once require callback completed
    var _bridgeReady = false;    // true once QWebChannel callback completed
    var _documentSymbols = [];
    var _documentSymbolRefreshTimer = null;
    var _documentSymbolRefreshPromise = null;
    var _activeDocumentUri = '';
    var _breadcrumbTrail = [];
    var _openBreadcrumbMenuState = null;
    var _signatureHelpLayoutFrame = 0;
    var _signatureHelpObserver = null;
    const breadcrumbsEl = document.getElementById('breadcrumbs');
    const breadcrumbMenuEl = document.getElementById('breadcrumb-menu');

    function resolveThemeName(themeName) {
        if (!(PY_SEMANTIC_FEATURE && LSP_LANGUAGE === 'python')) return themeName;
        if (themeName === 'vs') return 'pyemsi-vs';
        return themeName;
    }

    function getEditorDomNode() {
        return editor ? editor.getDomNode() : null;
    }

    function isWidgetVisible(element) {
        if (!element || !element.isConnected) {
            return false;
        }
        const style = window.getComputedStyle(element);
        if (style.display === 'none' || style.visibility === 'hidden') {
            return false;
        }
        return element.getClientRects().length > 0;
    }

    function getParameterHintsWidget() {
        const editorNode = getEditorDomNode();
        return editorNode ? editorNode.querySelector('.parameter-hints-widget') : null;
    }

    function getSuggestWidget() {
        const editorNode = getEditorDomNode();
        return editorNode ? editorNode.querySelector('.suggest-widget') : null;
    }

    function clearSignatureHelpPreferredTopLayout(widget) {
        if (!widget) {
            return;
        }
        widget.classList.remove('pyemsi-prefer-top');
        if (widget.dataset.pyemsiPreferredTop === 'true') {
            widget.style.removeProperty('top');
            delete widget.dataset.pyemsiPreferredTop;
        }
    }

    function applySignatureHelpPreferredTopLayout() {
        const widget = getParameterHintsWidget();
        if (!editor || !widget || !isWidgetVisible(widget)) {
            clearSignatureHelpPreferredTopLayout(widget);
            return;
        }

        const editorNode = getEditorDomNode();
        const position = editor.getPosition();
        const cursorBox = position ? editor.getScrolledVisiblePosition(position) : null;
        if (!editorNode || !cursorBox) {
            clearSignatureHelpPreferredTopLayout(widget);
            return;
        }

        const editorRect = editorNode.getBoundingClientRect();
        const widgetRect = widget.getBoundingClientRect();
        if (!editorRect.height || !widgetRect.height) {
            clearSignatureHelpPreferredTopLayout(widget);
            return;
        }

        const suggestWidget = getSuggestWidget();
        const suggestRect = isWidgetVisible(suggestWidget) ? suggestWidget.getBoundingClientRect() : null;
        const lineHeight = typeof editor.getOption === 'function' && monaco.editor && monaco.editor.EditorOption
            ? editor.getOption(monaco.editor.EditorOption.lineHeight)
            : 20;
        const gap = 8;
        const cursorTop = cursorBox.top;
        const cursorBottom = cursorBox.top + Math.max(cursorBox.height || lineHeight, lineHeight);
        let preferredTop = cursorTop - widgetRect.height - gap;
        if (suggestRect) {
            preferredTop = Math.min(preferredTop, suggestRect.top - editorRect.top - widgetRect.height - gap);
        }

        const fallbackTop = suggestRect
            ? Math.max(cursorBottom + gap, suggestRect.bottom - editorRect.top + gap)
            : cursorBottom + gap;
        const maxTop = Math.max(0, editorRect.height - widgetRect.height - gap);
        const topToUse = preferredTop >= 0
            ? Math.min(preferredTop, maxTop)
            : Math.min(fallbackTop, maxTop);
        const nextTop = `${Math.round(topToUse)}px`;
        const alreadyApplied = widget.dataset.pyemsiPreferredTop === 'true';

        widget.classList.toggle('pyemsi-prefer-top', preferredTop >= 0);
        if (!alreadyApplied || widget.style.top !== nextTop) {
            widget.style.top = nextTop;
        }
        widget.dataset.pyemsiPreferredTop = 'true';
    }

    function scheduleSignatureHelpLayout() {
        if (_signatureHelpLayoutFrame) {
            window.cancelAnimationFrame(_signatureHelpLayoutFrame);
        }
        _signatureHelpLayoutFrame = window.requestAnimationFrame(() => {
            _signatureHelpLayoutFrame = 0;
            applySignatureHelpPreferredTopLayout();
        });
    }

    function observeSignatureHelpWidget() {
        const editorNode = getEditorDomNode();
        if (!editorNode || _signatureHelpObserver) {
            return;
        }

        _signatureHelpObserver = new MutationObserver(() => {
            scheduleSignatureHelpLayout();
        });
        _signatureHelpObserver.observe(editorNode, {
            subtree: true,
            childList: true,
            attributes: true,
            attributeFilter: ['class', 'style'],
        });
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

    function getActiveDocumentUri() {
        if (_activeDocumentUri) return _activeDocumentUri;
        if (editor) {
            const model = editor.getModel();
            if (model && model.uri) return model.uri.toString();
        }
        if (lspClient && lspClient._fileUri) return lspClient._fileUri;
        return '';
    }

    function getDocumentLabelFromUri(uri) {
        if (!uri) return '';

        let decoded = String(uri);
        try {
            decoded = decodeURIComponent(decoded);
        } catch (_) {
            // Keep original when URI is not percent-encoded.
        }

        decoded = decoded.replace(/\\/g, '/');
        const segments = decoded.split('/').filter(Boolean);
        return segments.length > 0 ? segments[segments.length - 1] : decoded;
    }

    function buildFileBreadcrumb() {
        const label = getDocumentLabelFromUri(getActiveDocumentUri());
        if (!label) return null;
        return {
            name: label,
            detail: '',
            isFile: true,
        };
    }

    function hasLocalDocumentSymbolSupport(languageId) {
        return languageId === 'json';
    }

    function hasLspDocumentSymbolSupport(languageId) {
        if (!lspClient || !lspClient.supportsDocumentSymbols()) {
            return false;
        }
        return languageId === LSP_LANGUAGE;
    }

    function hasDocumentSymbolSupportForLanguage(languageId) {
        return hasLocalDocumentSymbolSupport(languageId) || hasLspDocumentSymbolSupport(languageId);
    }

    function hasDocumentSymbolSupportForActiveLanguage() {
        if (!editor) {
            return false;
        }
        return hasDocumentSymbolSupportForLanguage(editor.getModel().getLanguageId());
    }

    function shouldShowBreadcrumbs() {
        return hasDocumentSymbolSupportForActiveLanguage() && Array.isArray(_documentSymbols) && _documentSymbols.length > 0;
    }

    function navigateToFileStart() {
        if (!editor) return;
        const target = { lineNumber: 1, column: 1 };
        editor.setPosition(target);
        editor.revealPositionInCenter(target);
        editor.focus();
    }

    function navigateToSymbol(symbol) {
        if (!editor || !symbol || !symbol.selectionRange) return;
        const target = {
            lineNumber: symbol.selectionRange.startLineNumber,
            column: symbol.selectionRange.startColumn,
        };
        editor.setPosition(target);
        editor.revealPositionInCenter(target);
        editor.focus();
    }

    function hideBreadcrumbMenu() {
        breadcrumbMenuEl.replaceChildren();
        breadcrumbMenuEl.classList.remove('visible');
        breadcrumbMenuEl.style.left = '0px';
        breadcrumbMenuEl.style.top = '0px';
        breadcrumbMenuEl.style.minWidth = '180px';
    }

    function closeBreadcrumbMenu() {
        if (_openBreadcrumbMenuState === null) {
            hideBreadcrumbMenu();
            return;
        }
        _openBreadcrumbMenuState = null;
        renderBreadcrumbStrip(_breadcrumbTrail);
    }

    function setBreadcrumbMenuState(state) {
        _openBreadcrumbMenuState = state;
        renderBreadcrumbStrip(_breadcrumbTrail);
    }

    function getBreadcrumbMenuSymbols(entry) {
        if (!entry || entry.isFile) {
            return [];
        }
        if (entry.isChildMenu) {
            return Array.isArray(entry.menuSymbols) ? entry.menuSymbols : [];
        }
        return Array.isArray(entry.siblings) ? entry.siblings : [];
    }

    function breadcrumbEntryHasMenu(entry) {
        const menuSymbols = getBreadcrumbMenuSymbols(entry);
        if (entry && entry.isChildMenu) {
            return menuSymbols.length > 0;
        }
        return menuSymbols.length > 1;
    }

    function toggleBreadcrumbMenu(index, anchorEl) {
        if (!anchorEl) return;
        if (_openBreadcrumbMenuState && _openBreadcrumbMenuState.index === index) {
            closeBreadcrumbMenu();
            return;
        }

        const rect = anchorEl.getBoundingClientRect();
        setBreadcrumbMenuState({
            index,
            left: rect.left,
            top: rect.bottom + 4,
            width: Math.max(rect.width, 180),
        });
    }

    function renderBreadcrumbMenu(trail) {
        breadcrumbMenuEl.replaceChildren();
        if (!_openBreadcrumbMenuState) {
            hideBreadcrumbMenu();
            return;
        }

        const entry = trail[_openBreadcrumbMenuState.index];
        const menuSymbols = getBreadcrumbMenuSymbols(entry);
        if (!entry || entry.isFile || menuSymbols.length === 0 || (!entry.isChildMenu && menuSymbols.length <= 1)) {
            _openBreadcrumbMenuState = null;
            hideBreadcrumbMenu();
            return;
        }

        const surface = document.createElement('div');
        surface.className = 'breadcrumb-menu-surface';

        menuSymbols.forEach((menuSymbol) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'breadcrumb-menu-item';
            if (!entry.isChildMenu && menuSymbol === entry.symbol) {
                button.classList.add('active');
            }

            const name = document.createElement('span');
            name.className = 'breadcrumb-menu-item-name';
            name.textContent = menuSymbol.name || '(symbol)';
            button.appendChild(name);

            if (menuSymbol.detail || (!entry.isChildMenu && menuSymbol === entry.symbol)) {
                const meta = document.createElement('span');
                meta.className = 'breadcrumb-menu-item-meta';

                if (!entry.isChildMenu && menuSymbol === entry.symbol) {
                    const badge = document.createElement('span');
                    badge.className = 'breadcrumb-menu-item-badge';
                    badge.textContent = 'Current';
                    meta.appendChild(badge);
                }

                if (menuSymbol.detail) {
                    const detail = document.createElement('span');
                    detail.className = 'breadcrumb-menu-item-detail';
                    detail.textContent = menuSymbol.detail;
                    meta.appendChild(detail);
                }

                button.appendChild(meta);
            }

            button.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                _openBreadcrumbMenuState = null;
                navigateToSymbol(menuSymbol);
                updateBreadcrumbsForActivePosition();
            });
            surface.appendChild(button);
        });

        breadcrumbMenuEl.appendChild(surface);

        const maxLeft = Math.max(8, window.innerWidth - 340);
        breadcrumbMenuEl.style.left = `${Math.min(_openBreadcrumbMenuState.left, maxLeft)}px`;
        breadcrumbMenuEl.style.top = `${Math.min(_openBreadcrumbMenuState.top, window.innerHeight - 12)}px`;
        breadcrumbMenuEl.style.minWidth = `${_openBreadcrumbMenuState.width}px`;
        breadcrumbMenuEl.classList.add('visible');
    }

    function renderBreadcrumbStrip(trail) {
        breadcrumbsEl.replaceChildren();
        if (!Array.isArray(trail) || trail.length === 0) {
            _openBreadcrumbMenuState = null;
            hideBreadcrumbMenu();
            breadcrumbsEl.classList.remove('visible');
            return;
        }

        trail.forEach((entry, index) => {
            const item = document.createElement('div');
            item.className = 'breadcrumb-item';

            if (entry.isFile) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'breadcrumb-segment';
                button.textContent = entry.name || '(symbol)';
                button.title = entry.detail ? `${entry.name} - ${entry.detail}` : (entry.name || 'Symbol');
                button.addEventListener('click', () => {
                    navigateToFileStart();
                });
                item.appendChild(button);
            } else {
                const group = document.createElement('div');
                group.className = 'breadcrumb-segment-group';
                if (_openBreadcrumbMenuState && _openBreadcrumbMenuState.index === index) {
                    group.classList.add('open');
                }

                const labelButton = document.createElement('button');
                labelButton.type = 'button';
                labelButton.className = 'breadcrumb-segment';
                const hasMenu = breadcrumbEntryHasMenu(entry);
                if (entry.isChildMenu) {
                    const parentName = entry.parentName || 'symbol';
                    labelButton.title = `Show child symbols of ${parentName}`;
                    labelButton.setAttribute('aria-label', `Show child symbols of ${parentName}`);
                } else {
                    labelButton.title = entry.detail ? `${entry.name} - ${entry.detail}` : (entry.name || 'Symbol');
                }
                labelButton.setAttribute('aria-haspopup', hasMenu ? 'menu' : 'false');
                labelButton.setAttribute('aria-expanded', _openBreadcrumbMenuState && _openBreadcrumbMenuState.index === index ? 'true' : 'false');
                labelButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    if (hasMenu) {
                        toggleBreadcrumbMenu(index, labelButton);
                        return;
                    }
                    if (entry.isChildMenu) {
                        return;
                    }
                    navigateToSymbol(entry.symbol);
                });

                const labelSpan = document.createElement('span');
                labelSpan.className = 'breadcrumb-segment-label';
                labelSpan.textContent = entry.name || '(symbol)';
                labelButton.appendChild(labelSpan);
                group.appendChild(labelButton);

                item.appendChild(group);
            }

            breadcrumbsEl.appendChild(item);

            if (index < trail.length - 1) {
                const separator = document.createElement('span');
                separator.className = 'breadcrumb-separator';
                separator.textContent = '>';
                breadcrumbsEl.appendChild(separator);
            }
        });

        breadcrumbsEl.classList.add('visible');
        renderBreadcrumbMenu(trail);
    }

    function buildBreadcrumbTrailForActivePosition() {
        if (!shouldShowBreadcrumbs()) {
            return [];
        }

        const trail = [];
        const fileBreadcrumb = buildFileBreadcrumb();
        if (fileBreadcrumb) {
            trail.push(fileBreadcrumb);
        }

        if (!editor) {
            return trail;
        }

        const position = editor.getPosition();
        if (!position) {
            return trail;
        }

        const symbolTrail = buildSymbolBreadcrumbItems(position, _documentSymbols).map((item) => ({
            name: item.symbol.name || '',
            detail: item.symbol.detail || '',
            isFile: false,
            symbol: item.symbol,
            siblings: item.siblings,
            children: item.children,
            isLeaf: item.isLeaf,
        }));

        if (symbolTrail.length === 0 && Array.isArray(_documentSymbols) && _documentSymbols.length > 0) {
            symbolTrail.push({
                name: '...',
                detail: '',
                isFile: false,
                isChildMenu: true,
                parentName: fileBreadcrumb ? (fileBreadcrumb.name || 'file') : 'file',
                symbol: null,
                menuSymbols: _documentSymbols,
            });
        } else if (symbolTrail.length > 0) {
            const currentEntry = symbolTrail[symbolTrail.length - 1];
            const childSymbols = Array.isArray(currentEntry.children) ? currentEntry.children : [];
            if (childSymbols.length > 0) {
                symbolTrail.push({
                    name: '...',
                    detail: '',
                    isFile: false,
                    isChildMenu: true,
                    parentName: currentEntry.name || 'symbol',
                    symbol: currentEntry.symbol,
                    menuSymbols: childSymbols,
                });
            }
        }

        return trail.concat(symbolTrail);
    }

    function updateBreadcrumbsForActivePosition() {
        _breadcrumbTrail = buildBreadcrumbTrailForActivePosition();
        renderBreadcrumbStrip(_breadcrumbTrail);
    }

    async function resolveDocumentSymbolsForModel(model) {
        if (!model) {
            return [];
        }

        const languageId = model.getLanguageId();
        if (!hasDocumentSymbolSupportForLanguage(languageId)) {
            return [];
        }

        if (languageId === 'json') {
            return buildJsonDocumentSymbols(model.getValue());
        }

        if (!lspClient || !lspClient._initialized || !lspClient.supportsDocumentSymbols()) {
            return [];
        }

        const activeUri = getActiveDocumentUri() || (model.uri ? model.uri.toString() : lspClient._fileUri);
        if (normalizeUriKey(activeUri) !== normalizeUriKey(lspClient._fileUri)) {
            return [];
        }

        const result = await lspClient.documentSymbols();
        return normalizeLspDocumentSymbols(result, lspClient._fileUri);
    }

    async function refreshDocumentSymbols(options) {
        const force = !!(options && options.force);
        const skipBreadcrumbUpdate = !!(options && options.skipBreadcrumbUpdate);
        const model = editor ? editor.getModel() : null;
        if (!model || !hasDocumentSymbolSupportForLanguage(model.getLanguageId())) {
            _documentSymbols = [];
            _openBreadcrumbMenuState = null;
            if (!skipBreadcrumbUpdate) updateBreadcrumbsForActivePosition();
            return [];
        }
        if (!force && _documentSymbolRefreshPromise) {
            return _documentSymbolRefreshPromise;
        }

        const activeUri = model.uri ? model.uri.toString() : getActiveDocumentUri();
        const refreshPromise = resolveDocumentSymbolsForModel(model)
            .then((symbols) => {
                const currentModel = editor ? editor.getModel() : null;
                const currentUri = currentModel && currentModel.uri ? currentModel.uri.toString() : getActiveDocumentUri();
                if (normalizeUriKey(activeUri) !== normalizeUriKey(currentUri)) {
                    return _documentSymbols;
                }
                _documentSymbols = Array.isArray(symbols) ? symbols : [];
                _openBreadcrumbMenuState = null;
                if (!skipBreadcrumbUpdate) updateBreadcrumbsForActivePosition();
                return _documentSymbols;
            })
            .catch(() => {
                _documentSymbols = [];
                _openBreadcrumbMenuState = null;
                if (!skipBreadcrumbUpdate) updateBreadcrumbsForActivePosition();
                return [];
            })
            .finally(() => {
                if (_documentSymbolRefreshPromise === refreshPromise) {
                    _documentSymbolRefreshPromise = null;
                }
            });

        _documentSymbolRefreshPromise = refreshPromise;
        return refreshPromise;
    }

    function scheduleDocumentSymbolRefresh(delayMs) {
        if (_documentSymbolRefreshTimer) {
            clearTimeout(_documentSymbolRefreshTimer);
        }
        if (!hasDocumentSymbolSupportForActiveLanguage()) {
            _documentSymbols = [];
            _openBreadcrumbMenuState = null;
            updateBreadcrumbsForActivePosition();
            return;
        }
        _documentSymbolRefreshTimer = setTimeout(() => {
            _documentSymbolRefreshTimer = null;
            refreshDocumentSymbols({ force: true });
        }, typeof delayMs === 'number' ? delayMs : 180);
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

    function registerDocumentSymbolProvider(langId) {
        if (registeredDocumentSymbolLanguages.has(langId)) return;
        if (!hasDocumentSymbolSupportForLanguage(langId)) return;

        registeredDocumentSymbolLanguages.add(langId);
        monaco.languages.registerDocumentSymbolProvider(langId, {
            provideDocumentSymbols: async (model) => {
                if (!model || !hasDocumentSymbolSupportForLanguage(model.getLanguageId())) {
                    return [];
                }
                if (editor && model !== editor.getModel()) {
                    return [];
                }

                const symbols = await refreshDocumentSymbols({ force: true, skipBreadcrumbUpdate: true });
                return Array.isArray(symbols) ? symbols : [];
            }
        });
    }

    require.config({ paths: { 'vs': 'monaco-editor/min/vs' } });

    require(['vs/editor/editor.main'], () => {
        defineSemanticTheme();

        if (monaco.languages.json && monaco.languages.json.jsonDefaults) {
            const modeConfiguration = monaco.languages.json.jsonDefaults.modeConfiguration || {};
            if (modeConfiguration.documentSymbols) {
                monaco.languages.json.jsonDefaults.setModeConfiguration({
                    ...modeConfiguration,
                    documentSymbols: false,
                });
            }
        }

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
            scheduleDocumentSymbolRefresh(220);
            scheduleSignatureHelpLayout();
        });

        editor.onDidChangeModelLanguage((event) => {
            sendToPython('language', event.newLanguage);
        });

        editor.onDidChangeCursorPosition(() => {
            updateBreadcrumbsForActivePosition();
            scheduleSignatureHelpLayout();
        });

        editor.onDidScrollChange(() => {
            scheduleSignatureHelpLayout();
        });

        editor.onDidLayoutChange(() => {
            scheduleSignatureHelpLayout();
        });

        observeSignatureHelpWidget();

        // Start LSP client only if a server is configured for this language
        if (LSP_PORT > 0) {
            const langExtMap = { 'python': '.py', 'json': '.json', 'yaml': '.yaml',
                                 'javascript': '.js', 'typescript': '.ts' };
            const fileExt = langExtMap[LSP_LANGUAGE] || '.txt';
            lspClient = new LspClient('ws://127.0.0.1:' + LSP_PORT, LSP_LANGUAGE, fileExt);
            _activeDocumentUri = lspClient._fileUri || '';

            lspClient.onReady = () => {
                lspClient.openDocument(editor.getModel().getValue());
                registerLspProviders(LSP_LANGUAGE);
                registerSemanticProvider(LSP_LANGUAGE);
                registerDocumentSymbolProvider(LSP_LANGUAGE);
                scheduleDocumentSymbolRefresh(0);

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

        registerDocumentSymbolProvider(editor.getModel().getLanguageId());
        scheduleDocumentSymbolRefresh(0);
        scheduleSignatureHelpLayout();

        _editorReady = true;
        _finishInit();
    });

    function init() {
        if (!editor) return;
        sendToPython('value',    editor.getModel().getValue());
        sendToPython('language', editor.getModel().getLanguageId());
        sendToPython('theme',    editor._themeService._theme.themeName);
    }

    document.addEventListener('mousedown', (event) => {
        if (!_openBreadcrumbMenuState) return;
        if (breadcrumbsEl.contains(event.target) || breadcrumbMenuEl.contains(event.target)) return;
        closeBreadcrumbMenu();
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape' || !_openBreadcrumbMenuState) return;
        event.preventDefault();
        closeBreadcrumbMenu();
    });

    window.addEventListener('resize', () => {
        scheduleSignatureHelpLayout();
    });

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
            case 'readOnly':
                editor.updateOptions({ readOnly: !!data });
                break;
            case 'language':
                monaco.editor.setModelLanguage(editor.getModel(), data);
                if (hasDocumentSymbolSupportForLanguage(data)) {
                    registerDocumentSymbolProvider(data);
                    scheduleDocumentSymbolRefresh(0);
                } else {
                    _documentSymbols = [];
                    _openBreadcrumbMenuState = null;
                    updateBreadcrumbsForActivePosition();
                }
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
                _activeDocumentUri = data || '';
                _openBreadcrumbMenuState = null;
                if (lspClient) {
                    lspClient.changeFileUri(data, editor.getModel().getValue());
                    scheduleDocumentSymbolRefresh(0);
                } else {
                    updateBreadcrumbsForActivePosition();
                }
                break;
            case 'pythonAnalysisPaths':
                if (lspClient) lspClient.updatePythonAnalysisPaths(data);
                break;
            case 'editorAction':
                editor.trigger('keyboard', data, null);
                editor.focus();
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
    syncStateChanged = Signal(str)
    externalChangeChanged = Signal(bool)
    fileMissingChanged = Signal(bool)

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
        self._read_only = False
        self._file_sync = FileSyncController(self)
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
        self._bridge.setLanguage(language)
        self._bridge.send_to_js("language", language)

        self._file_sync.stateChanged.connect(self._on_sync_state_changed)
        self._file_sync.missingChanged.connect(self._on_missing_changed)
        self._file_sync.reloadRequested.connect(self._on_reload_requested)

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
            self._file_sync.set_dirty(new_dirty)
            self.dirtyChanged.emit(self._dirty)

    def _on_sync_state_changed(self, state: str) -> None:
        self.syncStateChanged.emit(state)
        self.externalChangeChanged.emit(
            state in {DocumentSyncState.EXTERNALLY_MODIFIED.value, DocumentSyncState.CONFLICT.value}
        )

    def _on_missing_changed(self, missing: bool) -> None:
        self.fileMissingChanged.emit(missing)

    def _on_reload_requested(self, path: str) -> None:
        if self._dirty:
            return
        self.load_file(path)

    @property
    def dirty(self) -> bool:
        return self._dirty

    def _mark_clean(self) -> None:
        self._initial_text = self._bridge.value
        self._file_sync.set_dirty(False)
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
        self.textChanged.emit(text)
        self._update_python_analysis_paths(resolved_path)
        self._bridge.send_to_js("fileUri", Path(resolved_path).as_uri())
        self._dirty = False
        self._file_sync.monitor_file(resolved_path)

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
        resolved_target = str(Path(target).resolve())
        resolved_target = self._prompt_conflicted_save(resolved_target)
        if resolved_target is None:
            return
        with open(resolved_target, "w", encoding="utf-8") as f:
            f.write(self.text())
        self._file_path = resolved_target
        self._bridge.send_to_js("fileUri", Path(resolved_target).as_uri())
        self._mark_clean()
        self._file_sync.mark_saved(resolved_target)

    def _prompt_conflicted_save(self, target: str) -> str | None:
        if not self.has_external_change or self._file_path is None:
            return target
        if target != self._file_path:
            return target

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("File Changed On Disk")
        dialog.setText("This file changed on disk after you started editing it.")
        dialog.setInformativeText(
            "Choose Overwrite to replace the on-disk file, or Save As to keep your edits in a new file."
        )
        overwrite_button = dialog.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
        save_as_button = dialog.addButton("Save As...", QMessageBox.ButtonRole.ActionRole)
        cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked is overwrite_button:
            return target
        if clicked is save_as_button:
            selected_path, _selected_filter = QFileDialog.getSaveFileName(
                self,
                "Save As",
                target,
                "All Files (*)",
            )
            if selected_path:
                return str(Path(selected_path).resolve())
        if clicked is cancel_button:
            return None
        return None

    @property
    def file_path(self) -> str | None:
        return self._file_path

    @property
    def sync_state(self) -> str:
        return self._file_sync.state.value

    @property
    def has_external_change(self) -> bool:
        return self._file_sync.has_external_change

    @property
    def file_missing(self) -> bool:
        return self._file_sync.missing

    # -- public API --------------------------------------------------------

    def closeEvent(self, event):
        if self._pylsp_proc is not None:
            self._pylsp_proc.terminate()
        super().closeEvent(event)

    def text(self):
        return self._bridge.value

    def setText(self, text):
        self._bridge.setValue(text)
        self._bridge.send_to_js("value", text)

    def language(self):
        return self._bridge.language

    def setLanguage(self, language):
        self._bridge.setLanguage(language)
        self._bridge.send_to_js("language", language)

    def theme(self):
        return self._bridge.theme

    def setTheme(self, theme):
        self._bridge.setTheme(theme)
        self._bridge.send_to_js("theme", theme)

    def isReadOnly(self) -> bool:
        return self._read_only

    def setReadOnly(self, read_only: bool) -> None:
        self._read_only = read_only
        self._bridge.send_to_js("readOnly", read_only)

    def insertAtCursor(self, text: str) -> None:
        """Insert *text* at the current cursor position."""
        self._bridge.send_to_js("insertAtCursor", text)

    def wrapSelection(self, prefix: str, suffix: str) -> None:
        """Wrap the current selection with *prefix* and *suffix*.

        If no text is selected the markers are inserted at the cursor.
        """
        self._bridge.send_to_js("wrapSelection", {"prefix": prefix, "suffix": suffix})

    def execute_editor_action(self, action_id: str) -> None:
        """Trigger a built-in Monaco editor action by its action ID."""
        self._bridge.send_to_js("editorAction", action_id)
