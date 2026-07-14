import {useColorMode} from '@docusaurus/theme-common';
import Editor, {loader, type Monaco, type OnMount} from '@monaco-editor/react';
import * as monacoEditor from 'monaco-editor';
import React, {
  type ChangeEvent,
  type DragEvent,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import {createPortal} from 'react-dom';

import {
  buildJsonSymbolTree,
  editorWindowTitle,
  findJsonSymbolTrail,
  type JsonSymbol,
  uniqueDisplayName,
} from './jsonSymbols';
import styles from './styles.module.css';

loader.config({monaco: monacoEditor});

interface WritableStreamLike {
  write(data: string): Promise<void>;
  close(): Promise<void>;
}

interface FileHandleLike {
  kind?: string;
  name: string;
  getFile(): Promise<File>;
  createWritable(): Promise<WritableStreamLike>;
}

interface WindowWithFilePicker extends Window {
  showOpenFilePicker?: (options: {
    multiple: boolean;
    types: Array<{
      description: string;
      accept: Record<string, string[]>;
    }>;
  }) => Promise<FileHandleLike[]>;
}

interface DataTransferItemWithHandle extends DataTransferItem {
  getAsFileSystemHandle?: () => Promise<FileHandleLike | null>;
}

interface FileCandidate {
  file: File;
  handle?: FileHandleLike;
}

interface OpenDocument {
  id: string;
  name: string;
  displayName: string;
  size: number;
  lastModified: number;
  text: string;
  savedText: string;
  modelUri: string;
  errorCount: number;
  handle?: FileHandleLike;
  relativePath?: string;
}

interface EditorPaneProps {
  documentItem: OpenDocument;
  paneLabel: string;
  theme: 'light' | 'vs-dark';
  onChange: (id: string, value: string) => void;
  onErrors: (id: string, count: number) => void;
  onFocus: (id: string) => void;
  onMonacoReady: (monaco: Monaco) => void;
  onSave: (id: string) => void;
  comparisonDocuments?: OpenDocument[];
  onComparisonChange?: (id: string) => void;
  onCloseComparison?: () => void;
}

let fallbackId = 0;

function nextDocumentId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  fallbackId += 1;
  return `input-control-file-${fallbackId}`;
}

function isJsonFile(file: File): boolean {
  const mime = file.type.toLowerCase();
  return file.name.toLowerCase().endsWith('.json') || mime === 'application/json' || mime === 'text/json';
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileTooltip(documentItem: OpenDocument): string {
  const modified = documentItem.lastModified
    ? new Date(documentItem.lastModified).toLocaleString()
    : 'Unknown';
  return `${documentItem.name}\nSize: ${formatBytes(documentItem.size)}\nLast modified: ${modified}\nThe browser does not expose the source path.`;
}

function downloadText(filename: string, text: string): void {
  const blob = new Blob([text], {type: 'application/json;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.hidden = true;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

export default function InputControlFileEditorClient(): ReactNode {
  const {colorMode} = useColorMode();
  const [documents, setDocuments] = useState<OpenDocument[]>([]);
  const [primaryId, setPrimaryId] = useState<string>();
  const [comparisonId, setComparisonId] = useState<string>();
  const [focusedDocumentId, setFocusedDocumentId] = useState<string>();
  const [status, setStatus] = useState('No files are open.');
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const monacoRef = useRef<Monaco | undefined>(undefined);
  const originalTitleRef = useRef(document.title);
  const documentsRef = useRef<OpenDocument[]>([]);

  const primaryDocument = documents.find((item) => item.id === primaryId);
  const comparisonDocument = documents.find((item) => item.id === comparisonId);
  const pageTitle = editorWindowTitle(
    primaryDocument?.displayName,
    comparisonDocument?.displayName,
  );

  useEffect(() => {
    documentsRef.current = documents;
  }, [documents]);

  useEffect(() => {
    return () => {
      for (const item of documentsRef.current) {
        monacoRef.current?.editor.getModel(monacoRef.current.Uri.parse(item.modelUri))?.dispose();
      }
    };
  }, []);

  useEffect(() => {
    document.title = pageTitle;
  }, [pageTitle]);

  useEffect(() => {
    return () => {
      document.title = originalTitleRef.current;
    };
  }, []);

  const hasDirtyDocuments = documents.some((item) => item.text !== item.savedText);
  useEffect(() => {
    if (!hasDirtyDocuments) return undefined;
    const warnBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warnBeforeUnload);
    return () => window.removeEventListener('beforeunload', warnBeforeUnload);
  }, [hasDirtyDocuments]);

  const addCandidates = useCallback(async (candidates: FileCandidate[]) => {
    const accepted = candidates.filter(({file}) => isJsonFile(file));
    const rejected = candidates.filter(({file}) => !isJsonFile(file));
    if (accepted.length === 0) {
      setStatus(rejected.length > 0
        ? `No JSON files were opened. Rejected: ${rejected.map(({file}) => file.name).join(', ')}.`
        : 'No files were selected.');
      return;
    }

    const loaded: Array<Omit<OpenDocument, 'displayName'>> = [];
    const failures: string[] = [];
    for (const {file, handle} of accepted) {
      try {
        const text = await file.text();
        const id = nextDocumentId();
        loaded.push({
          id,
          name: file.name,
          size: file.size,
          lastModified: file.lastModified,
          text,
          savedText: text,
          modelUri: `inmemory://input-control-files/${id}/${encodeURIComponent(file.name)}`,
          errorCount: 0,
          handle,
        });
      } catch {
        failures.push(file.name);
      }
    }

    if (loaded.length === 0) {
      setStatus(`The selected files could not be read: ${failures.join(', ')}.`);
      return;
    }

    setDocuments((current) => {
      const names = current.map((item) => item.displayName);
      const additions = loaded.map((item) => {
        const displayName = uniqueDisplayName(item.name, names);
        names.push(displayName);
        return {...item, displayName};
      });
      return [...current, ...additions];
    });
    setPrimaryId(loaded[0].id);
    setFocusedDocumentId(loaded[0].id);

    const notes: string[] = [`Opened ${loaded.length} ${loaded.length === 1 ? 'file' : 'files'}.`];
    if (rejected.length > 0) notes.push(`Rejected ${rejected.map(({file}) => file.name).join(', ')}.`);
    if (failures.length > 0) notes.push(`Could not read ${failures.join(', ')}.`);
    setStatus(notes.join(' '));
  }, []);

  const openFiles = useCallback(async () => {
    const picker = (window as WindowWithFilePicker).showOpenFilePicker;
    if (!picker) {
      inputRef.current?.click();
      return;
    }

    try {
      const handles = await picker({
        multiple: true,
        types: [{
          description: 'JSON input control files',
          accept: {'application/json': ['.json']},
        }],
      });
      const candidates = await Promise.all(handles.map(async (handle) => ({
        file: await handle.getFile(),
        handle,
      })));
      await addCandidates(candidates);
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') return;
      setStatus('The enhanced file picker was unavailable. Use the standard file picker instead.');
      inputRef.current?.click();
    }
  }, [addCandidates]);

  const onInputChange = useCallback(async (event: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    event.target.value = '';
    await addCandidates(files.map((file) => ({file})));
  }, [addCandidates]);

  const onDrop = useCallback(async (event: DragEvent<HTMLElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const candidates: FileCandidate[] = [];
    const items = Array.from(event.dataTransfer.items ?? []) as DataTransferItemWithHandle[];

    for (const item of items) {
      if (item.kind !== 'file') continue;
      try {
        const handle = await item.getAsFileSystemHandle?.();
        if (handle?.kind === 'file') {
          candidates.push({file: await handle.getFile(), handle});
          continue;
        }
      } catch {
        // The standard File fallback below remains available.
      }
      const file = item.getAsFile();
      if (file) candidates.push({file});
    }

    if (candidates.length === 0) {
      candidates.push(...Array.from(event.dataTransfer.files).map((file) => ({file})));
    }
    await addCandidates(candidates);
  }, [addCandidates]);

  const updateText = useCallback((id: string, value: string) => {
    setDocuments((current) => current.map((item) => item.id === id ? {...item, text: value} : item));
  }, []);

  const updateErrors = useCallback((id: string, errorCount: number) => {
    setDocuments((current) => current.map((item) => (
      item.id === id && item.errorCount !== errorCount ? {...item, errorCount} : item
    )));
  }, []);

  const saveDocument = useCallback(async (id: string) => {
    const item = documents.find((candidate) => candidate.id === id);
    if (!item) return;

    let savedByDownload = false;
    if (item.handle) {
      try {
        const writable = await item.handle.createWritable();
        await writable.write(item.text);
        await writable.close();
        setStatus(`Saved ${item.displayName} to the selected file.`);
      } catch {
        downloadText(item.name, item.text);
        savedByDownload = true;
        setStatus(`Direct writing was unavailable. Downloaded ${item.displayName} instead.`);
      }
    } else {
      downloadText(item.name, item.text);
      savedByDownload = true;
      setStatus(`Downloaded ${item.displayName}.`);
    }

    setDocuments((current) => current.map((candidate) => (
      candidate.id === id ? {...candidate, savedText: item.text} : candidate
    )));
    if (savedByDownload) setFocusedDocumentId(id);
  }, [documents]);

  useEffect(() => {
    const onKeyDown = (event: globalThis.KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== 's') return;
      const targetId = focusedDocumentId ?? primaryId;
      if (!targetId) return;
      event.preventDefault();
      void saveDocument(targetId);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [focusedDocumentId, primaryId, saveDocument]);

  const selectPrimary = useCallback((id: string) => {
    if (id === comparisonId) {
      setComparisonId(primaryId);
    }
    setPrimaryId(id);
    setFocusedDocumentId(id);
  }, [comparisonId, primaryId]);

  const closeDocument = useCallback((id: string) => {
    const index = documents.findIndex((item) => item.id === id);
    const item = documents[index];
    if (!item) return;
    if (item.text !== item.savedText && !window.confirm(`Close ${item.displayName} without saving?`)) {
      return;
    }

    monacoRef.current?.editor.getModel(monacoRef.current.Uri.parse(item.modelUri))?.dispose();
    const remaining = documents.filter((candidate) => candidate.id !== id);
    setDocuments(remaining);
    if (comparisonId === id) setComparisonId(undefined);
    if (primaryId === id) {
      const next = remaining[Math.min(index, Math.max(remaining.length - 1, 0))];
      setPrimaryId(next?.id);
      setFocusedDocumentId(next?.id);
      if (next?.id === comparisonId) setComparisonId(undefined);
    } else if (focusedDocumentId === id) {
      setFocusedDocumentId(primaryId);
    }
    setStatus(`Closed ${item.displayName}.`);
  }, [comparisonId, documents, focusedDocumentId, primaryId]);

  const identity = primaryDocument
    ? comparisonDocument
      ? `${primaryDocument.displayName} ↔ ${comparisonDocument.displayName}`
      : primaryDocument.displayName
    : 'No input control file open';

  return (
    <section
      className={`${styles.shell} ${isDragging ? styles.dragging : ''}`}
      onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setIsDragging(false);
      }}
      onDrop={(event) => void onDrop(event)}>
      <input
        ref={inputRef}
        className={styles.hiddenInput}
        type="file"
        accept=".json,application/json,text/json"
        multiple
        onChange={(event) => void onInputChange(event)}
      />

      <div className={styles.windowBar}>
        <div className={styles.identity} title={identity}>{identity}</div>
        <div className={styles.windowActions}>
          <button className="button button--sm button--secondary" type="button" onClick={() => void openFiles()}>
            Open files
          </button>
          {documents.length >= 2 && (
            <select
              className={styles.select}
              aria-label="Split editor with"
              value={comparisonId ?? ''}
              onChange={(event) => {
                setComparisonId(event.target.value || undefined);
                if (event.target.value) setFocusedDocumentId(event.target.value);
              }}>
              <option value="">Split editor…</option>
              {documents.filter((item) => item.id !== primaryId).map((item) => (
                <option key={item.id} value={item.id}>{item.displayName}</option>
              ))}
            </select>
          )}
          {comparisonDocument && (
            <button className="button button--sm button--secondary" type="button" onClick={() => setComparisonId(undefined)}>
              Close split
            </button>
          )}
        </div>
      </div>

      {documents.length > 0 && (
        <div className={styles.tabs} role="tablist" aria-label="Open input control files">
          {documents.map((item) => {
            const dirty = item.text !== item.savedText;
            return (
              <div
                key={item.id}
                className={`${styles.tabGroup} ${item.id === primaryId ? styles.activeTab : ''}`}>
                <button
                  type="button"
                  role="tab"
                  aria-selected={item.id === primaryId}
                  className={styles.tab}
                  title={fileTooltip(item)}
                  onClick={() => selectPrimary(item.id)}>
                  <span className={styles.tabName}>{item.displayName}</span>
                  {dirty && <span className={styles.dirtyMark} aria-label="Modified">●</span>}
                </button>
                <button
                  type="button"
                  className={styles.closeTab}
                  aria-label={`Close ${item.displayName}`}
                  onClick={() => closeDocument(item.id)}>×</button>
              </div>
            );
          })}
        </div>
      )}

      {!primaryDocument ? (
        <div className={styles.dropZone}>
          <div className={styles.dropIcon} aria-hidden="true">{'{ }'}</div>
          <h2>Open input control files</h2>
          <p>Drag and drop one or more JSON files here, or choose them from your computer.</p>
          <button className="button button--primary button--lg" type="button" onClick={() => void openFiles()}>
            Open Input Control Files
          </button>
        </div>
      ) : (
        <div className={`${styles.editorGrid} ${comparisonDocument ? styles.split : ''}`}>
          <EditorPane
            paneLabel="Primary editor"
            documentItem={primaryDocument}
            theme={colorMode === 'dark' ? 'vs-dark' : 'light'}
            onChange={updateText}
            onErrors={updateErrors}
            onFocus={setFocusedDocumentId}
            onMonacoReady={(monaco) => { monacoRef.current = monaco; }}
            onSave={(id) => void saveDocument(id)}
          />
          {comparisonDocument && (
            <EditorPane
              paneLabel="Comparison editor"
              documentItem={comparisonDocument}
              theme={colorMode === 'dark' ? 'vs-dark' : 'light'}
              onChange={updateText}
              onErrors={updateErrors}
              onFocus={setFocusedDocumentId}
              onMonacoReady={(monaco) => { monacoRef.current = monaco; }}
              onSave={(id) => void saveDocument(id)}
              comparisonDocuments={documents.filter((item) => item.id !== primaryId)}
              onComparisonChange={setComparisonId}
              onCloseComparison={() => setComparisonId(undefined)}
            />
          )}
        </div>
      )}

      <div className={styles.globalStatus} role="status" aria-live="polite">{status}</div>
      {isDragging && <div className={styles.dropOverlay}>Drop JSON files to open them</div>}
    </section>
  );
}

function EditorPane({
  documentItem,
  paneLabel,
  theme,
  onChange,
  onErrors,
  onFocus,
  onMonacoReady,
  onSave,
  comparisonDocuments,
  onComparisonChange,
  onCloseComparison,
}: EditorPaneProps): ReactNode {
  const editorRef = useRef<monacoEditor.editor.IStandaloneCodeEditor | undefined>(undefined);
  const documentIdRef = useRef(documentItem.id);
  const [cursorOffset, setCursorOffset] = useState(0);
  const [symbolTree, setSymbolTree] = useState(() => buildJsonSymbolTree(documentItem.text));

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSymbolTree(buildJsonSymbolTree(documentItem.text));
    }, 220);
    return () => window.clearTimeout(timer);
  }, [documentItem.text]);

  useEffect(() => {
    documentIdRef.current = documentItem.id;
    const model = editorRef.current?.getModel();
    const position = editorRef.current?.getPosition();
    setCursorOffset(model && position ? model.getOffsetAt(position) : 0);
  }, [documentItem.id]);

  const onMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    onMonacoReady(monaco);
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      allowComments: false,
      trailingCommas: 'error',
    });
    const updateCursor = () => {
      const model = editor.getModel();
      const position = editor.getPosition();
      if (model && position) setCursorOffset(model.getOffsetAt(position));
    };
    editor.onDidChangeCursorPosition(updateCursor);
    editor.onDidChangeModel(updateCursor);
    editor.onDidFocusEditorText(() => onFocus(documentIdRef.current));
    updateCursor();
  };

  const formatDocument = () => {
    void editorRef.current?.getAction('editor.action.formatDocument')?.run();
    editorRef.current?.focus();
  };

  const navigateToOffset = (offset: number) => {
    const editor = editorRef.current;
    const model = editor?.getModel();
    if (!editor || !model) return;
    const position = model.getPositionAt(offset);
    editor.setPosition(position);
    editor.revealPositionInCenter(position);
    editor.focus();
  };

  const dirty = documentItem.text !== documentItem.savedText;
  const validationText = documentItem.errorCount === 0
    ? 'Valid JSON'
    : `${documentItem.errorCount} JSON ${documentItem.errorCount === 1 ? 'problem' : 'problems'}`;

  return (
    <section className={styles.pane} aria-label={paneLabel} onMouseDown={() => onFocus(documentItem.id)}>
      <div className={styles.paneHeader}>
        {comparisonDocuments && onComparisonChange ? (
          <select
            className={styles.documentSelect}
            aria-label="Comparison document"
            value={documentItem.id}
            onChange={(event) => onComparisonChange(event.target.value)}>
            {comparisonDocuments.map((item) => (
              <option key={item.id} value={item.id}>{item.displayName}</option>
            ))}
          </select>
        ) : (
          <span className={styles.paneFilename} title={fileTooltip(documentItem)}>
            {documentItem.displayName}{dirty ? ' ●' : ''}
          </span>
        )}
        <div className={styles.paneActions}>
          <button
            type="button"
            className={styles.smallButton}
            disabled={documentItem.errorCount > 0}
            title={documentItem.errorCount > 0 ? 'Fix JSON problems before formatting' : 'Format JSON'}
            onClick={formatDocument}>Format</button>
          <button type="button" className={styles.smallButton} onClick={() => onSave(documentItem.id)}>Save</button>
          {onCloseComparison && (
            <button type="button" className={styles.smallButton} onClick={onCloseComparison}>Close</button>
          )}
        </div>
      </div>

      <Breadcrumbs
        filename={documentItem.displayName}
        roots={symbolTree.roots}
        cursorOffset={cursorOffset}
        onNavigate={navigateToOffset}
      />

      <div className={styles.monacoHost}>
        <Editor
          path={documentItem.modelUri}
          language="json"
          value={documentItem.text}
          theme={theme}
          keepCurrentModel
          saveViewState
          loading={<div className={styles.editorLoading}>Loading Monaco…</div>}
          onMount={onMount}
          onChange={(value) => onChange(documentItem.id, value ?? '')}
          onValidate={(markers) => onErrors(documentItem.id, markers.length)}
          options={{
            automaticLayout: true,
            bracketPairColorization: {enabled: true},
            folding: true,
            formatOnPaste: true,
            minimap: {enabled: false},
            scrollBeyondLastLine: false,
            stickyScroll: {enabled: true},
            tabSize: 2,
            wordWrap: 'on',
          }}
        />
      </div>
      <div className={`${styles.validation} ${documentItem.errorCount > 0 ? styles.invalid : ''}`} role="status">
        {validationText}
      </div>
    </section>
  );
}

interface BreadcrumbsProps {
  filename: string;
  roots: JsonSymbol[];
  cursorOffset: number;
  onNavigate: (offset: number) => void;
}

interface BreadcrumbEntry {
  key: string;
  name: string;
  detail?: string;
  targetOffset?: number;
  menuItems: JsonSymbol[];
  currentId?: string;
  isChildMenu?: boolean;
}

function Breadcrumbs({filename, roots, cursorOffset, onNavigate}: BreadcrumbsProps): ReactNode {
  const trail = useMemo(() => findJsonSymbolTrail(roots, cursorOffset), [cursorOffset, roots]);
  const entries = useMemo<BreadcrumbEntry[]>(() => {
    const result: BreadcrumbEntry[] = [{
      key: 'file',
      name: filename,
      targetOffset: 0,
      menuItems: [],
    }];
    for (const level of trail) {
      result.push({
        key: level.symbol.id,
        name: level.symbol.name,
        detail: level.symbol.detail,
        targetOffset: level.symbol.selectionOffset,
        menuItems: level.siblings,
        currentId: level.symbol.id,
      });
    }
    const children = trail.length > 0 ? trail[trail.length - 1].children : roots;
    if (children.length > 0) {
      result.push({
        key: 'children',
        name: '…',
        detail: 'Show child entries',
        menuItems: children,
        isChildMenu: true,
      });
    }
    return result;
  }, [filename, roots, trail]);

  const [openIndex, setOpenIndex] = useState<number>();
  const [menuPosition, setMenuPosition] = useState({left: 0, top: 0, width: 180});
  const breadcrumbRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const triggerRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const closeMenu = useCallback((restoreFocus = false) => {
    if (restoreFocus && openIndex !== undefined) triggerRefs.current[openIndex]?.focus();
    setOpenIndex(undefined);
  }, [openIndex]);

  useEffect(() => {
    if (openIndex === undefined) return undefined;
    const closeOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (breadcrumbRef.current?.contains(target) || menuRef.current?.contains(target)) return;
      closeMenu();
    };
    document.addEventListener('mousedown', closeOutside);
    return () => document.removeEventListener('mousedown', closeOutside);
  }, [closeMenu, openIndex]);

  useEffect(() => {
    if (openIndex === undefined) return;
    window.requestAnimationFrame(() => {
      menuRef.current?.querySelector<HTMLButtonElement>('[role="menuitem"]')?.focus();
    });
  }, [openIndex]);

  const openMenu = (index: number) => {
    const trigger = triggerRefs.current[index];
    if (!trigger) return;
    const rect = trigger.getBoundingClientRect();
    setMenuPosition({
      left: Math.min(rect.left, Math.max(8, window.innerWidth - 330)),
      top: Math.min(rect.bottom + 4, window.innerHeight - 260),
      width: Math.max(rect.width, 180),
    });
    setOpenIndex(index);
  };

  const activateEntry = (entry: BreadcrumbEntry, index: number) => {
    const hasMenu = entry.isChildMenu || entry.menuItems.length > 1;
    if (hasMenu) {
      if (openIndex === index) closeMenu(); else openMenu(index);
      return;
    }
    if (entry.targetOffset !== undefined) onNavigate(entry.targetOffset);
  };

  const onMenuKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    const buttons = Array.from(menuRef.current?.querySelectorAll<HTMLButtonElement>('[role="menuitem"]') ?? []);
    const current = buttons.indexOf(document.activeElement as HTMLButtonElement);
    if (event.key === 'Escape') {
      event.preventDefault();
      closeMenu(true);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      buttons[(current + 1) % buttons.length]?.focus();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      buttons[(current - 1 + buttons.length) % buttons.length]?.focus();
    } else if (event.key === 'Home') {
      event.preventDefault();
      buttons[0]?.focus();
    } else if (event.key === 'End') {
      event.preventDefault();
      buttons.at(-1)?.focus();
    }
  };

  const openEntry = openIndex === undefined ? undefined : entries[openIndex];
  return (
    <>
      <div ref={breadcrumbRef} className={styles.breadcrumbs} aria-label="JSON breadcrumbs">
        {entries.map((entry, index) => (
          <React.Fragment key={entry.key}>
            <button
              ref={(element) => { triggerRefs.current[index] = element; }}
              type="button"
              className={`${styles.breadcrumbButton} ${openIndex === index ? styles.openBreadcrumb : ''}`}
              title={entry.detail ? `${entry.name} — ${entry.detail}` : entry.name}
              aria-haspopup={entry.isChildMenu || entry.menuItems.length > 1 ? 'menu' : undefined}
              aria-expanded={openIndex === index ? true : undefined}
              onClick={() => activateEntry(entry, index)}
              onKeyDown={(event) => {
                if ((event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ') && (entry.isChildMenu || entry.menuItems.length > 1)) {
                  event.preventDefault();
                  openMenu(index);
                }
              }}>
              {entry.name}
            </button>
            {index < entries.length - 1 && <span className={styles.separator} aria-hidden="true">›</span>}
          </React.Fragment>
        ))}
      </div>
      {openEntry && createPortal(
        <div
          ref={menuRef}
          className={styles.breadcrumbMenu}
          role="menu"
          aria-label={`${openEntry.name} entries`}
          style={{left: menuPosition.left, top: menuPosition.top, minWidth: menuPosition.width}}
          onKeyDown={onMenuKeyDown}>
          {openEntry.menuItems.map((item) => (
            <button
              key={item.id}
              type="button"
              role="menuitem"
              className={`${styles.menuItem} ${item.id === openEntry.currentId ? styles.currentMenuItem : ''}`}
              onClick={() => {
                onNavigate(item.selectionOffset);
                closeMenu();
              }}>
              <span className={styles.menuName}>{item.name}</span>
              <span className={styles.menuMeta}>
                {item.id === openEntry.currentId && <span className={styles.currentBadge}>Current</span>}
                <span>{item.detail}</span>
              </span>
            </button>
          ))}
        </div>,
        document.body,
      )}
    </>
  );
}
