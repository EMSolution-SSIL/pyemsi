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

import BhCurveEditorModal from './BhCurveEditorModal';
import {hasMalformedBhCurveRoot} from './bhCurveModel';
import EditorIcon from './EditorIcon';
import FieldSourceEditorModal from './FieldSourceEditorModal';
import {hasMalformedFieldSourceRoot} from './fieldSourceModel';
import MaterialPropertyEditorModal from './MaterialPropertyEditorModal';
import {hasMalformedMaterialPropertyRoot} from './materialPropertyModel';
import {isEmSolutionInput} from './emSolutionModel';
import TimeFunctionEditorModal from './TimeFunctionEditorModal';
import {hasMalformedTimeFunctionRoot} from './timeFunctionModel';
import {
  editorWindowTitle,
  findSymbolTrail,
  type StructuredSymbol,
  uniqueDisplayName,
} from './jsonSymbols';
import {
  type EditorFormat,
  FORMAT_LABELS,
  type ParsedFormat,
  findTomlCompatibilityIssue,
  formatStructuredText,
  parseStructuredFormat,
  serializeStructuredFormat,
} from './structuredFormats';
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
  revision: number;
  activeFormat: EditorFormat;
  canonicalValue?: unknown;
  formatDrafts: Partial<Record<EditorFormat, FormatDraft>>;
  handle?: FileHandleLike;
  relativePath?: string;
}

interface FormatDraft {
  text: string;
  lastValidText: string;
  modelUri: string;
  sourceRevision: number;
  issues: ParsedFormat['issues'];
  roots: StructuredSymbol[];
}

interface EditorPaneProps {
  documentItem: OpenDocument;
  draft: FormatDraft;
  paneLabel: string;
  theme: 'light' | 'vs-dark';
  isFocused: boolean;
  onChange: (id: string, format: EditorFormat, value: string) => void;
  onParsed: (id: string, format: EditorFormat, text: string, parsed: ParsedFormat) => void;
  onEditorReady: (
    id: string,
    format: EditorFormat,
    editor: monacoEditor.editor.IStandaloneCodeEditor,
  ) => void;
  onFocus: (id: string) => void;
  onMonacoReady: (monaco: Monaco) => void;
  onSelectFormat: (id: string, format: EditorFormat) => void;
  onDiscardInvalid: (id: string) => void;
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

function editorKey(id: string, format: EditorFormat): string {
  return `${id}:${format}`;
}

function documentHasUncommittedDraft(documentItem: OpenDocument): boolean {
  return Object.entries(documentItem.formatDrafts).some(([format, draft]) => (
    format !== 'json'
    && draft !== undefined
    && draft.text !== draft.lastValidText
  ));
}

function documentIsDirty(documentItem: OpenDocument): boolean {
  return documentItem.text !== documentItem.savedText || documentHasUncommittedDraft(documentItem);
}

function configureTomlLanguage(monaco: Monaco): void {
  if (monaco.languages.getLanguages().some(({id}) => id === 'toml')) return;
  monaco.languages.register({id: 'toml', extensions: ['.toml'], aliases: ['TOML', 'toml']});
  monaco.languages.setLanguageConfiguration('toml', {
    comments: {lineComment: '#'},
    brackets: [['[', ']'], ['{', '}']],
    autoClosingPairs: [
      {open: '[', close: ']'},
      {open: '{', close: '}'},
      {open: '"', close: '"'},
      {open: "'", close: "'"},
    ],
  });
  monaco.languages.setMonarchTokensProvider('toml', {
    tokenizer: {
      root: [
        [/#.*$/, 'comment'],
        [/^\s*\[\[.*\]\]\s*$/, 'type.identifier'],
        [/^\s*\[.*\]\s*$/, 'type.identifier'],
        [/"""/, {token: 'string.quote', next: '@multiBasic'}],
        [/'{3}/, {token: 'string.quote', next: '@multiLiteral'}],
        [/"([^"\\]|\\.)*"/, 'string'],
        [/'[^']*'/, 'string'],
        [/\b(true|false)\b/, 'keyword'],
        [/\b(inf|nan)\b/, 'number.float'],
        [/[+-]?(0x[0-9a-fA-F_]+|0o[0-7_]+|0b[01_]+|\d[\d_]*)(?![\w-])/, 'number'],
        [/[+-]?\d[\d_]*(\.\d[\d_]*)?([eE][+-]?\d[\d_]*)?/, 'number.float'],
        [/[A-Za-z0-9_-]+(?=\s*=)/, 'key'],
        [/[=,.\[\]{}]/, 'delimiter'],
      ],
      multiBasic: [
        [/[^\\"]+/, 'string'],
        [/\\./, 'string.escape'],
        [/"""/, {token: 'string.quote', next: '@pop'}],
        [/"/, 'string'],
      ],
      multiLiteral: [
        [/[^']+/, 'string'],
        [/'{3}/, {token: 'string.quote', next: '@pop'}],
        [/'/, 'string'],
      ],
    },
  });
}

export default function InputControlFileEditorClient(): ReactNode {
  const {colorMode} = useColorMode();
  const [documents, setDocuments] = useState<OpenDocument[]>([]);
  const [primaryId, setPrimaryId] = useState<string>();
  const [comparisonId, setComparisonId] = useState<string>();
  const [focusedDocumentId, setFocusedDocumentId] = useState<string>();
  const [status, setStatus] = useState('No files are open.');
  const [isDragging, setIsDragging] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fieldSourceEditorDocumentId, setFieldSourceEditorDocumentId] = useState<string>();
  const [materialPropertyEditorDocumentId, setMaterialPropertyEditorDocumentId] = useState<string>();
  const [timeFunctionEditorDocumentId, setTimeFunctionEditorDocumentId] = useState<string>();
  const [bhCurveEditorDocumentId, setBhCurveEditorDocumentId] = useState<string>();
  const inputRef = useRef<HTMLInputElement>(null);
  const shellRef = useRef<HTMLElement>(null);
  const monacoRef = useRef<Monaco | undefined>(undefined);
  const editorsRef = useRef(new Map<string, monacoEditor.editor.IStandaloneCodeEditor>());
  const originalTitleRef = useRef(document.title);
  const documentsRef = useRef<OpenDocument[]>([]);

  const primaryDocument = documents.find((item) => item.id === primaryId);
  const comparisonDocument = documents.find((item) => item.id === comparisonId);
  const focusedVisibleDocument = documents.find((item) => (
    item.id === focusedDocumentId
    && (item.id === primaryId || item.id === comparisonId)
  ));
  const actionDocument = focusedVisibleDocument ?? primaryDocument;
  const actionDraft = actionDocument?.formatDrafts[actionDocument.activeFormat];
  const actionFormatLabel = actionDocument ? FORMAT_LABELS[actionDocument.activeFormat] : 'JSON';
  const actionHasInvalidAlternate = Boolean(
    actionDocument
    && actionDocument.activeFormat !== 'json'
    && actionDraft
    && (actionDraft.issues.length > 0 || actionDraft.text !== actionDraft.lastValidText),
  );
  const pageTitle = editorWindowTitle(
    primaryDocument?.displayName,
    comparisonDocument?.displayName,
  );
  const actionIsEmSolution = actionDocument?.canonicalValue !== undefined && isEmSolutionInput(actionDocument.canonicalValue);
  const actionHasMalformedFieldSources = actionDocument?.canonicalValue !== undefined
    && hasMalformedFieldSourceRoot(actionDocument.canonicalValue);
  const actionHasMalformedMaterialProperties = actionDocument?.canonicalValue !== undefined
    && hasMalformedMaterialPropertyRoot(actionDocument.canonicalValue);
  const actionHasMalformedTimeFunctions = actionDocument?.canonicalValue !== undefined
    && hasMalformedTimeFunctionRoot(actionDocument.canonicalValue);
  const actionHasMalformedBhCurves = actionDocument?.canonicalValue !== undefined
    && hasMalformedBhCurveRoot(actionDocument.canonicalValue);
  const fieldSourceEditorDocument = documents.find((item) => item.id === fieldSourceEditorDocumentId);
  const materialPropertyEditorDocument = documents.find((item) => item.id === materialPropertyEditorDocumentId);
  const timeFunctionEditorDocument = documents.find((item) => item.id === timeFunctionEditorDocumentId);
  const bhCurveEditorDocument = documents.find((item) => item.id === bhCurveEditorDocumentId);

  useEffect(() => {
    documentsRef.current = documents;
  }, [documents]);

  useEffect(() => {
    return () => {
      for (const item of documentsRef.current) {
        for (const draft of Object.values(item.formatDrafts)) {
          monacoRef.current?.editor.getModel(monacoRef.current.Uri.parse(draft.modelUri))?.dispose();
        }
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

  const hasDirtyDocuments = documents.some(documentIsDirty);
  useEffect(() => {
    if (!hasDirtyDocuments) return undefined;
    const warnBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warnBeforeUnload);
    return () => window.removeEventListener('beforeunload', warnBeforeUnload);
  }, [hasDirtyDocuments]);

  useEffect(() => {
    const updateFullscreenState = () => {
      setIsFullscreen(document.fullscreenElement === shellRef.current);
    };
    document.addEventListener('fullscreenchange', updateFullscreenState);
    return () => document.removeEventListener('fullscreenchange', updateFullscreenState);
  }, []);

  const toggleFullscreen = useCallback(async () => {
    try {
      if (document.fullscreenElement === shellRef.current) {
        await document.exitFullscreen();
        return;
      }
      if (!shellRef.current?.requestFullscreen) {
        setStatus('Fullscreen mode is not supported by this browser.');
        return;
      }
      await shellRef.current.requestFullscreen();
    } catch {
      setStatus('The browser could not enter fullscreen mode.');
    }
  }, []);

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
        const parsed = parseStructuredFormat(text, 'json');
        loaded.push({
          id,
          name: file.name,
          size: file.size,
          lastModified: file.lastModified,
          text,
          savedText: text,
          revision: 0,
          activeFormat: 'json',
          canonicalValue: parsed.issues.length === 0 ? parsed.value : undefined,
          formatDrafts: {
            json: {
              text,
              lastValidText: parsed.issues.length === 0 ? text : '',
              modelUri: `inmemory://input-control-files/${id}/${encodeURIComponent(file.name)}.json`,
              sourceRevision: 0,
              issues: parsed.issues,
              roots: parsed.roots,
            },
          },
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

  const updateDraftText = useCallback((id: string, format: EditorFormat, value: string) => {
    setDocuments((current) => current.map((item) => {
      if (item.id !== id) return item;
      const draft = item.formatDrafts[format];
      if (!draft) return item;
      return {
        ...item,
        text: format === 'json' ? value : item.text,
        formatDrafts: {...item.formatDrafts, [format]: {...draft, text: value}},
      };
    }));
  }, []);

  const updateParsedDraft = useCallback((
    id: string,
    format: EditorFormat,
    parsedText: string,
    parsed: ParsedFormat,
  ) => {
    setDocuments((current) => current.map((item) => {
      if (item.id !== id) return item;
      const draft = item.formatDrafts[format];
      if (!draft || draft.text !== parsedText) return item;
      const parsedDraft = {...draft, issues: parsed.issues, roots: parsed.roots};
      if (parsed.issues.length > 0 || parsed.value === undefined) {
        return {
          ...item,
          canonicalValue: format === 'json' ? undefined : item.canonicalValue,
          formatDrafts: {...item.formatDrafts, [format]: parsedDraft},
        };
      }

      if (
        format !== 'json'
        && item.canonicalValue !== undefined
        && JSON.stringify(parsed.value) === JSON.stringify(item.canonicalValue)
      ) {
        return {
          ...item,
          formatDrafts: {
            ...item.formatDrafts,
            [format]: {
              ...parsedDraft,
              lastValidText: parsedText,
              sourceRevision: item.revision,
            },
          },
        };
      }

      const revision = item.revision + 1;
      if (format === 'json') {
        return {
          ...item,
          revision,
          canonicalValue: parsed.value,
          formatDrafts: {
            ...item.formatDrafts,
            json: {...parsedDraft, lastValidText: parsedText, sourceRevision: revision},
          },
        };
      }

      const jsonText = serializeStructuredFormat(parsed.value, 'json');
      const jsonParsed = parseStructuredFormat(jsonText, 'json');
      const jsonDraft: FormatDraft = {
        text: jsonText,
        lastValidText: jsonText,
        modelUri: item.formatDrafts.json?.modelUri
          ?? `inmemory://input-control-files/${item.id}/${encodeURIComponent(item.name)}.json`,
        sourceRevision: revision,
        issues: jsonParsed.issues,
        roots: jsonParsed.roots,
      };
      return {
        ...item,
        text: jsonText,
        revision,
        canonicalValue: parsed.value,
        formatDrafts: {
          ...item.formatDrafts,
          json: jsonDraft,
          [format]: {...parsedDraft, lastValidText: parsedText, sourceRevision: revision},
        },
      };
    }));
  }, []);

  const updateCanonicalDocument = useCallback((id: string, canonicalValue: unknown, source: string) => {
    setDocuments((current) => current.map((item) => {
      if (item.id !== id) return item;
      const revision = item.revision + 1;
      const jsonText = serializeStructuredFormat(canonicalValue, 'json');
      const formatDrafts: OpenDocument['formatDrafts'] = {};
      for (const [formatName, existingDraft] of Object.entries(item.formatDrafts)) {
        if (!existingDraft) continue;
        const format = formatName as EditorFormat;
        const text = serializeStructuredFormat(canonicalValue, format);
        const parsed = parseStructuredFormat(text, format);
        formatDrafts[format] = {
          ...existingDraft,
          text,
          lastValidText: text,
          sourceRevision: revision,
          issues: parsed.issues,
          roots: parsed.roots,
        };
      }
      if (!formatDrafts.json) {
        const parsed = parseStructuredFormat(jsonText, 'json');
        formatDrafts.json = {
          text: jsonText,
          lastValidText: jsonText,
          modelUri: `inmemory://input-control-files/${item.id}/${encodeURIComponent(item.name)}.json`,
          sourceRevision: revision,
          issues: parsed.issues,
          roots: parsed.roots,
        };
      }
      return {...item, text: jsonText, revision, canonicalValue, formatDrafts};
    }));
    setFocusedDocumentId(id);
    setStatus(`Applied ${source} changes to the open document. Save the file to keep them.`);
  }, []);

  const selectDocumentFormat = useCallback((id: string, format: EditorFormat) => {
    const item = documents.find((candidate) => candidate.id === id);
    if (!item || item.activeFormat === format) return;
    const currentDraft = item.formatDrafts[item.activeFormat];
    if (item.activeFormat !== 'json' && currentDraft?.text !== currentDraft?.lastValidText) {
      const parsed = currentDraft
        ? parseStructuredFormat(currentDraft.text, item.activeFormat)
        : undefined;
      setStatus(parsed?.issues.length
        ? `Fix or discard the invalid ${FORMAT_LABELS[item.activeFormat]} changes before switching formats.`
        : `Wait for ${FORMAT_LABELS[item.activeFormat]} validation to finish before switching formats.`);
      return;
    }
    if (item.canonicalValue === undefined) {
      setStatus(`Fix JSON problems in ${item.displayName} before opening another representation.`);
      return;
    }
    if (format === 'toml') {
      const issue = findTomlCompatibilityIssue(item.canonicalValue);
      if (issue) {
        setStatus(`TOML is unavailable: ${issue.message}`);
        return;
      }
    }

    setDocuments((current) => current.map((candidate) => {
      if (candidate.id !== id || candidate.canonicalValue === undefined) return candidate;
      const existing = candidate.formatDrafts[format];
      if (existing && existing.sourceRevision === candidate.revision) {
        return {...candidate, activeFormat: format};
      }
      const text = serializeStructuredFormat(candidate.canonicalValue, format);
      const parsed = parseStructuredFormat(text, format);
      const draft: FormatDraft = {
        text,
        lastValidText: text,
        modelUri: `inmemory://input-control-files/${candidate.id}/${encodeURIComponent(candidate.name)}.${format}`,
        sourceRevision: candidate.revision,
        issues: parsed.issues,
        roots: parsed.roots,
      };
      return {
        ...candidate,
        activeFormat: format,
        formatDrafts: {...candidate.formatDrafts, [format]: draft},
      };
    }));
  }, [documents]);

  const discardInvalidDraft = useCallback((id: string) => {
    setDocuments((current) => current.map((item) => {
      if (item.id !== id || item.activeFormat === 'json') return item;
      const draft = item.formatDrafts[item.activeFormat];
      if (!draft) return item;
      const parsed = parseStructuredFormat(draft.lastValidText, item.activeFormat);
      return {
        ...item,
        formatDrafts: {
          ...item.formatDrafts,
          [item.activeFormat]: {
            ...draft,
            text: draft.lastValidText,
            issues: parsed.issues,
            roots: parsed.roots,
          },
        },
      };
    }));
    setStatus('Discarded the invalid alternate-format changes.');
  }, []);

  const saveDocument = useCallback(async (id: string) => {
    const item = documents.find((candidate) => candidate.id === id);
    if (!item) return;
    const activeDraft = item.formatDrafts[item.activeFormat];
    if (item.activeFormat !== 'json' && activeDraft?.text !== activeDraft?.lastValidText) {
      const parsed = activeDraft
        ? parseStructuredFormat(activeDraft.text, item.activeFormat)
        : undefined;
      setStatus(parsed?.issues.length
        ? `Fix or discard the invalid ${FORMAT_LABELS[item.activeFormat]} changes before saving.`
        : `Wait for ${FORMAT_LABELS[item.activeFormat]} validation to finish before saving.`);
      return;
    }

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

  const closeSplit = useCallback(() => {
    setComparisonId(undefined);
    setFocusedDocumentId(primaryId);
  }, [primaryId]);

  const registerEditor = useCallback((
    id: string,
    format: EditorFormat,
    editor: monacoEditor.editor.IStandaloneCodeEditor,
  ) => {
    editorsRef.current.set(editorKey(id, format), editor);
  }, []);

  const formatActionDocument = useCallback(() => {
    if (!actionDocument) return;
    const format = actionDocument.activeFormat;
    const draft = actionDocument.formatDrafts[format];
    if (!draft || draft.issues.length > 0) return;
    try {
      updateDraftText(actionDocument.id, format, formatStructuredText(draft.text, format));
    } catch (error) {
      setStatus(error instanceof Error ? error.message : `Could not format ${FORMAT_LABELS[format]}.`);
    }
    const editor = editorsRef.current.get(editorKey(actionDocument.id, format));
    editor?.focus();
  }, [actionDocument, updateDraftText]);

  const closeDocument = useCallback((id: string) => {
    const index = documents.findIndex((item) => item.id === id);
    const item = documents[index];
    if (!item) return;
    if (documentIsDirty(item) && !window.confirm(`Close ${item.displayName} without saving?`)) {
      return;
    }

    for (const [format, draft] of Object.entries(item.formatDrafts)) {
      monacoRef.current?.editor.getModel(monacoRef.current.Uri.parse(draft.modelUri))?.dispose();
      editorsRef.current.delete(editorKey(id, format as EditorFormat));
    }
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

  return (
    <section
      ref={shellRef}
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
        <div className={styles.identity}>Input Control File Editor</div>
        <div className={styles.windowActions}>
          <button className="button button--sm button--secondary" type="button" onClick={() => void openFiles()}>
            <EditorIcon name="open" /> Open files
          </button>
          <button
            className="button button--sm button--secondary"
            type="button"
            disabled={!actionDocument || !actionDraft || actionDraft.issues.length > 0}
            title={actionDraft?.issues.length
              ? `Fix ${actionFormatLabel} problems in ${actionDocument?.displayName ?? 'the active file'} before formatting`
              : `Format ${actionDocument?.displayName ?? 'the active file'} as ${actionFormatLabel}`}
            onClick={formatActionDocument}>
            <EditorIcon name="format" /> Format
          </button>
          <button
            className="button button--sm button--secondary"
            type="button"
            disabled={!actionDocument || actionHasInvalidAlternate}
            title={actionHasInvalidAlternate
              ? `Fix or discard invalid ${actionFormatLabel} changes before saving`
              : `Save ${actionDocument?.displayName ?? 'the active file'} as JSON`}
            onClick={() => {
              if (actionDocument) void saveDocument(actionDocument.id);
            }}>
            <EditorIcon name="save" /> Save
          </button>
          {actionIsEmSolution && (
            <button
              className="button button--sm button--secondary"
              type="button"
              disabled={actionHasInvalidAlternate || actionHasMalformedMaterialProperties}
              title={actionHasInvalidAlternate
                ? `Fix or discard invalid ${actionFormatLabel} changes before editing Material Properties`
                : actionHasMalformedMaterialProperties
                  ? '16_Material_Properties or one of its material collections does not use the current object/array format'
                  : `Edit Material Properties in ${actionDocument?.displayName ?? 'the active file'}`}
              onClick={() => {
                if (actionDocument) setMaterialPropertyEditorDocumentId(actionDocument.id);
              }}>
              <EditorIcon name="material" /> Edit Material Properties
            </button>
          )}
          {actionIsEmSolution && (
            <button
              className="button button--sm button--secondary"
              type="button"
              disabled={actionHasInvalidAlternate || actionHasMalformedFieldSources}
              title={actionHasInvalidAlternate
                ? `Fix or discard invalid ${actionFormatLabel} changes before editing Field Sources`
                : actionHasMalformedFieldSources
                  ? '17_Field_Source exists but is not an editable array'
                  : `Edit Field Sources in ${actionDocument?.displayName ?? 'the active file'}`}
              onClick={() => {
                if (actionDocument) setFieldSourceEditorDocumentId(actionDocument.id);
              }}>
              <EditorIcon name="network" /> Edit Field Sources
            </button>
          )}
          {actionIsEmSolution && (
            <button
              className="button button--sm button--secondary"
              type="button"
              disabled={actionHasInvalidAlternate || actionHasMalformedTimeFunctions}
              title={actionHasInvalidAlternate
                ? `Fix or discard invalid ${actionFormatLabel} changes before editing Time Functions`
                : actionHasMalformedTimeFunctions
                  ? '18_Time_Function exists but is not an editable array'
                  : `Edit Time Functions in ${actionDocument?.displayName ?? 'the active file'}`}
              onClick={() => {
                if (actionDocument) setTimeFunctionEditorDocumentId(actionDocument.id);
              }}>
              <EditorIcon name="time" /> Edit Time Functions
            </button>
          )}
          {actionIsEmSolution && (
            <button
              className="button button--sm button--secondary"
              type="button"
              disabled={actionHasInvalidAlternate || actionHasMalformedBhCurves}
              title={actionHasInvalidAlternate
                ? `Fix or discard invalid ${actionFormatLabel} changes before editing B-H Curves`
                : actionHasMalformedBhCurves
                  ? '20_BH_Curve exists but is not an editable array'
                  : `Edit B-H Curves in ${actionDocument?.displayName ?? 'the active file'}`}
              onClick={() => {
                if (actionDocument) setBhCurveEditorDocumentId(actionDocument.id);
              }}>
              <EditorIcon name="curve" /> Edit B-H Curves
            </button>
          )}
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
            <button className="button button--sm button--secondary" type="button" onClick={closeSplit}>
              <EditorIcon name="splitClose" /> Close split
            </button>
          )}
          <button
            className="button button--sm button--secondary"
            type="button"
            aria-pressed={isFullscreen}
            title={isFullscreen ? 'Exit fullscreen mode' : 'Open the editor in fullscreen mode'}
            onClick={() => void toggleFullscreen()}>
            <EditorIcon name={isFullscreen ? 'fullscreenExit' : 'fullscreen'} />
            {isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          </button>
        </div>
      </div>

      {documents.length > 0 && (
        <div className={styles.tabs} role="tablist" aria-label="Open input control files">
          {documents.map((item) => {
            const dirty = documentIsDirty(item);
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
                  title={`Close ${item.displayName}`}
                  onClick={() => closeDocument(item.id)}><EditorIcon name="close" /></button>
              </div>
            );
          })}
        </div>
      )}

      {!primaryDocument ? (
        <div
          className={styles.dropZone}
          aria-label="JSON file drop zone">
          <div className={`${styles.dropTarget} ${isDragging ? styles.activeDropTarget : ''}`}>
            <div className={styles.dropIcon} aria-hidden="true">{isDragging ? '↓' : '{ }'}</div>
            {isDragging ? (
              <p className={styles.activeDropPrompt}>Drop JSON files to open them</p>
            ) : (
              <>
                <p>Drag and drop one or more JSON files here.</p>
                <button className="button button--primary button--lg" type="button" onClick={() => void openFiles()}>
                  <EditorIcon name="open" /> Open Input Control Files
                </button>
              </>
            )}
          </div>
        </div>
      ) : (
        <div className={`${styles.editorGrid} ${comparisonDocument ? styles.split : ''}`}>
          <EditorPane
            paneLabel="Primary editor"
            documentItem={primaryDocument}
            draft={primaryDocument.formatDrafts[primaryDocument.activeFormat]!}
            theme={colorMode === 'dark' ? 'vs-dark' : 'light'}
            isFocused={actionDocument?.id === primaryDocument.id}
            onChange={updateDraftText}
            onParsed={updateParsedDraft}
            onEditorReady={registerEditor}
            onFocus={setFocusedDocumentId}
            onSelectFormat={selectDocumentFormat}
            onDiscardInvalid={discardInvalidDraft}
            onMonacoReady={(monaco) => { monacoRef.current = monaco; }}
          />
          {comparisonDocument && (
            <EditorPane
              paneLabel="Comparison editor"
              documentItem={comparisonDocument}
              draft={comparisonDocument.formatDrafts[comparisonDocument.activeFormat]!}
              theme={colorMode === 'dark' ? 'vs-dark' : 'light'}
              isFocused={actionDocument?.id === comparisonDocument.id}
              onChange={updateDraftText}
              onParsed={updateParsedDraft}
              onEditorReady={registerEditor}
              onFocus={setFocusedDocumentId}
              onSelectFormat={selectDocumentFormat}
              onDiscardInvalid={discardInvalidDraft}
              onMonacoReady={(monaco) => { monacoRef.current = monaco; }}
            />
          )}
        </div>
      )}

      <div className={styles.globalStatus} role="status" aria-live="polite">{status}</div>
      {isDragging && primaryDocument && (
        <div className={styles.dropOverlay}>Drop JSON files to open them</div>
      )}
      {fieldSourceEditorDocument?.canonicalValue !== undefined && (
        <FieldSourceEditorModal
          documentName={fieldSourceEditorDocument.displayName}
          value={fieldSourceEditorDocument.canonicalValue}
          portalTarget={document.fullscreenElement ?? document.body}
          onClose={() => setFieldSourceEditorDocumentId(undefined)}
          onApply={(nextValue) => {
            updateCanonicalDocument(fieldSourceEditorDocument.id, nextValue, 'Field Source');
            setFieldSourceEditorDocumentId(undefined);
          }}
        />
      )}
      {materialPropertyEditorDocument?.canonicalValue !== undefined && (
        <MaterialPropertyEditorModal
          documentName={materialPropertyEditorDocument.displayName}
          value={materialPropertyEditorDocument.canonicalValue}
          portalTarget={document.fullscreenElement ?? document.body}
          onClose={() => setMaterialPropertyEditorDocumentId(undefined)}
          onApply={(nextValue) => {
            updateCanonicalDocument(materialPropertyEditorDocument.id, nextValue, 'Material Property');
            setMaterialPropertyEditorDocumentId(undefined);
          }}
        />
      )}
      {timeFunctionEditorDocument?.canonicalValue !== undefined && (
        <TimeFunctionEditorModal
          documentName={timeFunctionEditorDocument.displayName}
          value={timeFunctionEditorDocument.canonicalValue}
          portalTarget={document.fullscreenElement ?? document.body}
          onClose={() => setTimeFunctionEditorDocumentId(undefined)}
          onApply={(nextValue) => {
            updateCanonicalDocument(timeFunctionEditorDocument.id, nextValue, 'Time Function');
            setTimeFunctionEditorDocumentId(undefined);
          }}
        />
      )}
      {bhCurveEditorDocument?.canonicalValue !== undefined && (
        <BhCurveEditorModal
          documentName={bhCurveEditorDocument.displayName}
          value={bhCurveEditorDocument.canonicalValue}
          portalTarget={document.fullscreenElement ?? document.body}
          onClose={() => setBhCurveEditorDocumentId(undefined)}
          onApply={(nextValue) => {
            updateCanonicalDocument(bhCurveEditorDocument.id, nextValue, 'B-H Curve');
            setBhCurveEditorDocumentId(undefined);
          }}
        />
      )}
    </section>
  );
}

function EditorPane({
  documentItem,
  draft,
  paneLabel,
  theme,
  isFocused,
  onChange,
  onParsed,
  onEditorReady,
  onFocus,
  onMonacoReady,
  onSelectFormat,
  onDiscardInvalid,
}: EditorPaneProps): ReactNode {
  const editorRef = useRef<monacoEditor.editor.IStandaloneCodeEditor | undefined>(undefined);
  const monacoInstanceRef = useRef<Monaco | undefined>(undefined);
  const documentIdRef = useRef(documentItem.id);
  const [cursorOffset, setCursorOffset] = useState(0);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      onParsed(
        documentItem.id,
        documentItem.activeFormat,
        draft.text,
        parseStructuredFormat(draft.text, documentItem.activeFormat),
      );
    }, 220);
    return () => window.clearTimeout(timer);
  }, [documentItem.activeFormat, documentItem.id, draft.text, onParsed]);

  useEffect(() => {
    documentIdRef.current = documentItem.id;
    if (editorRef.current) onEditorReady(documentItem.id, documentItem.activeFormat, editorRef.current);
    const model = editorRef.current?.getModel();
    const position = editorRef.current?.getPosition();
    setCursorOffset(model && position ? model.getOffsetAt(position) : 0);
  }, [documentItem.activeFormat, documentItem.id, onEditorReady]);

  useEffect(() => {
    if (documentItem.activeFormat === 'json') return;
    const editor = editorRef.current;
    const monaco = monacoInstanceRef.current;
    const model = editor?.getModel();
    if (!monaco || !model) return;
    monaco.editor.setModelMarkers(model, 'input-control-format', draft.issues.map((issue) => {
      const start = model.getPositionAt(issue.offset);
      const end = model.getPositionAt(issue.offset + issue.length);
      return {
        severity: monaco.MarkerSeverity.Error,
        message: issue.message,
        startLineNumber: start.lineNumber,
        startColumn: start.column,
        endLineNumber: end.lineNumber,
        endColumn: Math.max(end.column, start.column + 1),
      };
    }));
  }, [documentItem.activeFormat, draft.issues]);

  const onMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoInstanceRef.current = monaco;
    configureTomlLanguage(monaco);
    onEditorReady(documentItem.id, documentItem.activeFormat, editor);
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

  const navigateToOffset = (offset: number) => {
    const editor = editorRef.current;
    const model = editor?.getModel();
    if (!editor || !model) return;
    const position = model.getPositionAt(offset);
    editor.setPosition(position);
    editor.revealPositionInCenter(position);
    editor.focus();
  };

  const formatLabel = FORMAT_LABELS[documentItem.activeFormat];
  const validationText = draft.issues.length === 0
    ? `Valid ${formatLabel}`
    : `${draft.issues.length} ${formatLabel} ${draft.issues.length === 1 ? 'problem' : 'problems'}`;
  const tomlIssue = documentItem.canonicalValue === undefined
    ? undefined
    : findTomlCompatibilityIssue(documentItem.canonicalValue);
  const blocksSwitching = documentItem.activeFormat !== 'json'
    && (draft.issues.length > 0 || draft.text !== draft.lastValidText);

  return (
    <section
      className={`${styles.pane} ${isFocused ? styles.focusedPane : ''}`}
      aria-label={paneLabel}
      onMouseDown={() => onFocus(documentItem.id)}>
      <div className={styles.paneNavigation}>
        <div className={styles.formatSwitcher} role="group" aria-label={`${paneLabel} format`}>
          {(['json', 'yaml', 'toml'] as const).map((format) => {
            const unavailable = format !== 'json' && documentItem.canonicalValue === undefined;
            const disabledByToml = format === 'toml' && Boolean(tomlIssue);
            const disabled = format !== documentItem.activeFormat
              && (blocksSwitching || unavailable || disabledByToml);
            const reason = blocksSwitching
              ? draft.issues.length > 0
                ? `Fix or discard invalid ${formatLabel} changes first`
                : `Wait for ${formatLabel} validation to finish`
              : unavailable
                ? 'Fix JSON problems before switching formats'
                : disabledByToml
                  ? tomlIssue?.message
                  : `Edit as ${FORMAT_LABELS[format]}`;
            return (
              <button
                key={format}
                type="button"
                className={`${styles.formatButton} ${format === documentItem.activeFormat ? styles.activeFormat : ''}`}
                aria-pressed={format === documentItem.activeFormat}
                disabled={disabled}
                title={reason}
                onClick={() => onSelectFormat(documentItem.id, format)}>
                {FORMAT_LABELS[format]}
              </button>
            );
          })}
        </div>
        <Breadcrumbs
          filename={documentItem.displayName}
          formatLabel={formatLabel}
          roots={draft.roots}
          cursorOffset={cursorOffset}
          onNavigate={navigateToOffset}
        />
      </div>

      <div className={styles.monacoHost}>
        <Editor
          path={draft.modelUri}
          language={documentItem.activeFormat}
          value={draft.text}
          theme={theme}
          keepCurrentModel
          saveViewState
          loading={<div className={styles.editorLoading}>Loading Monaco…</div>}
          onMount={onMount}
          onChange={(value) => onChange(documentItem.id, documentItem.activeFormat, value ?? '')}
          options={{
            automaticLayout: true,
            bracketPairColorization: {enabled: true},
            folding: true,
            formatOnPaste: true,
            minimap: {enabled: false},
            // Monaco 0.55.1 can surface its internal word-highlighter cancellation
            // as an unhandled rejection when this editor switches file models.
            occurrencesHighlight: 'off',
            scrollBeyondLastLine: false,
            stickyScroll: {enabled: true},
            tabSize: 2,
            wordWrap: 'on',
          }}
        />
      </div>
      <div className={`${styles.validation} ${draft.issues.length > 0 ? styles.invalid : ''}`} role="status">
        <span>
          {documentItem.activeFormat !== 'json' && draft.issues.length === 0
            ? `${validationText}. Comments are not saved to JSON.`
            : validationText}
        </span>
        {blocksSwitching && (
          <button type="button" className={styles.discardButton} onClick={() => onDiscardInvalid(documentItem.id)}>
            <EditorIcon name="cancel" /> Discard invalid changes
          </button>
        )}
      </div>
    </section>
  );
}

interface BreadcrumbsProps {
  filename: string;
  formatLabel: string;
  roots: StructuredSymbol[];
  cursorOffset: number;
  onNavigate: (offset: number) => void;
}

interface BreadcrumbEntry {
  key: string;
  name: string;
  detail?: string;
  targetOffset?: number;
  menuItems: StructuredSymbol[];
  currentId?: string;
  isChildMenu?: boolean;
}

function Breadcrumbs({filename, formatLabel, roots, cursorOffset, onNavigate}: BreadcrumbsProps): ReactNode {
  const trail = useMemo(() => findSymbolTrail(roots, cursorOffset), [cursorOffset, roots]);
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
  const fullscreenRoot = document.fullscreenElement;
  const portalTarget = fullscreenRoot instanceof HTMLElement
    && fullscreenRoot.contains(breadcrumbRef.current)
    ? fullscreenRoot
    : document.body;
  return (
    <>
      <div ref={breadcrumbRef} className={styles.breadcrumbs} aria-label={`${formatLabel} breadcrumbs`}>
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
        portalTarget,
      )}
    </>
  );
}
