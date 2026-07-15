import React, {type ReactNode, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

import EditorIcon from './EditorIcon';
import {
  collectNetworkReferences,
  componentSummary,
  createNetworkComponent,
  deepClone,
  findNetworkSections,
  isKnownNetworkType,
  isNetworkDefinition,
  isPlainRecord,
  NETWORK_COMPONENT_SCHEMAS,
  NETWORK_COMPONENT_TYPES,
  type NetworkComponent,
  type NetworkComponentType,
  type NetworkDefinition,
  type NetworkFieldDefinition,
  type NetworkSection,
  nextElementId,
  normalizeNetwork,
  replaceNetworkSections,
  validateNetwork,
} from './networkModel';
import styles from './styles.module.css';

const DOCUMENTATION_URL = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/17_9_NETWORK.html';

interface NetworkEditorModalProps {
  documentName: string;
  value: unknown;
  portalTarget?: Element;
  onApply: (value: unknown) => void;
  onClose: () => void;
}

function sectionCopies(value: unknown): Array<NetworkSection & {network: NetworkDefinition}> {
  return findNetworkSections(value).flatMap((section) => (
    isNetworkDefinition(section.network)
      ? [{...section, network: deepClone(section.network)}]
      : []
  ));
}

function dataRows(network: NetworkDefinition): unknown[] {
  return Array.isArray(network.data) ? network.data : [];
}

function componentFrom(value: unknown): NetworkComponent | undefined {
  return isPlainRecord(value) && typeof value.type === 'string' ? value as NetworkComponent : undefined;
}

function numberValue(raw: string): number | string {
  return raw.trim() === '' ? '' : Number(raw);
}

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function nextTableId(rows: unknown[]): number {
  const used = new Set<number>();
  for (const row of rows) {
    const component = componentFrom(row);
    if (component?.type !== 'TABLE' || !Array.isArray(component.data)) continue;
    for (const table of component.data) {
      if (isPlainRecord(table) && Number.isInteger(table.ID)) used.add(table.ID as number);
    }
  }
  let candidate = 1;
  while (used.has(candidate)) candidate += 1;
  return candidate;
}

function cloneForDuplicate(component: NetworkComponent, rows: unknown[]): NetworkComponent {
  const duplicate = deepClone(component);
  if (duplicate.type === 'TABLE' && Array.isArray(duplicate.data)) {
    let tableId = nextTableId(rows);
    duplicate.data = duplicate.data.map((table) => {
      const copy = deepClone(table);
      if (isPlainRecord(copy)) {
        copy.ID = tableId;
        tableId += 1;
      }
      return copy;
    });
  } else if (!['SETV', 'SETI'].includes(duplicate.type)) {
    duplicate.ID = nextElementId(rows);
  }
  return duplicate;
}

export default function NetworkEditorModal({
  documentName,
  value,
  portalTarget,
  onApply,
  onClose,
}: NetworkEditorModalProps): ReactNode {
  const initialSectionsRef = useRef(sectionCopies(value));
  const initialJsonRef = useRef(JSON.stringify(initialSectionsRef.current));
  const [sections, setSections] = useState(initialSectionsRef.current);
  const [selectedSection, setSelectedSection] = useState(0);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [addType, setAddType] = useState<NetworkComponentType>('FEM');
  const [editingIndex, setEditingIndex] = useState<number>();
  const [draft, setDraft] = useState<NetworkComponent>();
  const [rawText, setRawText] = useState('');
  const [rawError, setRawError] = useState('');
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const sectionsRef = useRef(sections);
  const restoreFocusRef = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement ? document.activeElement : null,
  );
  const references = useMemo(() => collectNetworkReferences(value), [value]);
  const section = sections[selectedSection];
  const network = section?.network;
  const rows = network ? dataRows(network) : [];

  useEffect(() => {
    sectionsRef.current = sections;
  }, [sections]);

  const updateNetwork = useCallback((update: (current: NetworkDefinition) => NetworkDefinition) => {
    setSections((current) => current.map((item, index) => (
      index === selectedSection ? {...item, network: update(item.network)} : item
    )));
  }, [selectedSection]);

  const requestClose = useCallback(() => {
    const dirty = JSON.stringify(sectionsRef.current) !== initialJsonRef.current;
    if (dirty && !window.confirm('Discard the unsaved NETWORK modal changes?')) return;
    onClose();
  }, [onClose]);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeButtonRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        requestClose();
        return;
      }
      if (event.key !== 'Tab' || !dialogRef.current) return;
      const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>(
        'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]',
      ));
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable.at(-1)!;
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', onKeyDown);
      restoreFocusRef.current?.focus();
    };
  }, [requestClose]);

  const normalizedSections = useMemo(() => sections.map((item) => ({
    ...item,
    network: normalizeNetwork(item.network),
  })), [sections]);
  const allIssues = useMemo(() => normalizedSections.flatMap((item, index) => (
    validateNetwork(item.network, value).map((issue) => ({...issue, sectionIndex: index}))
  )), [normalizedSections, value]);
  const issues = allIssues.filter((issue) => issue.sectionIndex === selectedSection);
  const errorCount = allIssues.filter((issue) => issue.severity === 'error').length;
  const warningCount = allIssues.filter((issue) => issue.severity === 'warning').length;

  const visibleRows = rows.map((row, index) => ({row, index})).filter(({row}) => {
    const component = componentFrom(row);
    const type = component?.type ?? 'INVALID';
    if (typeFilter !== 'ALL' && type !== typeFilter) return false;
    const haystack = `${type} ${component ? componentSummary(component) : JSON.stringify(row)}`.toLowerCase();
    return haystack.includes(search.trim().toLowerCase());
  });

  const openEditor = (index: number) => {
    const row = rows[index];
    const component = componentFrom(row);
    setEditingIndex(index);
    setRawError('');
    if (component && isKnownNetworkType(component.type)) {
      setDraft(deepClone(component));
      setRawText('');
    } else {
      setDraft(undefined);
      setRawText(JSON.stringify(row, null, 2));
    }
  };

  const startAdd = () => {
    setEditingIndex(rows.length);
    setDraft(createNetworkComponent(addType, rows));
    setRawText('');
    setRawError('');
  };

  const closeEditor = () => {
    setEditingIndex(undefined);
    setDraft(undefined);
    setRawText('');
    setRawError('');
  };

  const replaceRows = (nextRows: unknown[]) => updateNetwork((current) => ({...current, data: nextRows}));

  const saveEditor = () => {
    if (editingIndex === undefined) return;
    let nextRow: unknown;
    if (draft) {
      nextRow = draft;
    } else {
      try {
        nextRow = JSON.parse(rawText);
        if (!isPlainRecord(nextRow) || typeof nextRow.type !== 'string') {
          setRawError('Raw component must be a JSON object with a string type.');
          return;
        }
      } catch (error) {
        setRawError(error instanceof Error ? error.message : 'Invalid JSON component.');
        return;
      }
    }
    const nextRows = [...rows];
    if (editingIndex >= rows.length) nextRows.push(nextRow);
    else nextRows[editingIndex] = nextRow;
    replaceRows(nextRows);
    closeEditor();
  };

  const moveRow = (index: number, direction: -1 | 1) => {
    const target = index + direction;
    if (target < 0 || target >= rows.length) return;
    const nextRows = [...rows];
    [nextRows[index], nextRows[target]] = [nextRows[target], nextRows[index]];
    replaceRows(nextRows);
  };

  const duplicateRow = (index: number) => {
    const component = componentFrom(rows[index]);
    if (!component) return;
    const nextRows = [...rows];
    nextRows.splice(index + 1, 0, cloneForDuplicate(component, rows));
    replaceRows(nextRows);
  };

  const deleteRow = (index: number) => {
    if (!window.confirm(`Delete NETWORK row ${index + 1}?`)) return;
    replaceRows(rows.filter((_, rowIndex) => rowIndex !== index));
    if (editingIndex === index) closeEditor();
  };

  const apply = () => {
    if (errorCount > 0) return;
    onApply(replaceNetworkSections(value, normalizedSections));
  };

  const modal = (
    <div
      className={styles.networkModalBackdrop}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) requestClose();
      }}>
      <div
        ref={dialogRef}
        className={styles.networkModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="network-editor-title">
        <header className={styles.networkModalHeader}>
          <div>
            <h2 id="network-editor-title">NETWORK editor</h2>
            <div className={styles.networkModalSubtitle}>{documentName}</div>
          </div>
          <div className={styles.networkHeaderActions}>
            <a href={DOCUMENTATION_URL} target="_blank" rel="noreferrer">
              Official documentation <EditorIcon name="external" />
            </a>
            <button ref={closeButtonRef} type="button" className={styles.networkIconButton} aria-label="Close NETWORK editor" title="Close NETWORK editor" onClick={requestClose}>
              <EditorIcon name="close" />
            </button>
          </div>
        </header>

        <div className={styles.networkModalBody}>
          <section className={styles.networkSettings} aria-label="NETWORK settings">
            {sections.length > 1 && (
              <label>
                NETWORK occurrence
                <select value={selectedSection} onChange={(event) => {
                  setSelectedSection(Number(event.target.value));
                  closeEditor();
                }}>
                  {sections.map((item, index) => (
                    <option key={item.sourceIndex} value={index}>Entry {index + 1} (source index {item.sourceIndex})</option>
                  ))}
                </select>
              </label>
            )}
            <label title="Scale from the analyzed model region to the full physical system.">
              Region factor
              <input
                aria-label="Region factor"
                type="number"
                step="any"
                value={inputValue(network?.REGION_FACTOR)}
                onChange={(event) => updateNetwork((current) => ({...current, REGION_FACTOR: numberValue(event.target.value)}))}
              />
              <small>Full-system scale relative to the analyzed region.</small>
            </label>
            <label title="Number of electrically parallel circuit regions; the documented default is 1.">
              Parallel regions
              <input
                aria-label="Parallel regions"
                type="number"
                step="any"
                value={inputValue(network?.REGION_PARALLEL)}
                onChange={(event) => updateNetwork((current) => ({...current, REGION_PARALLEL: numberValue(event.target.value)}))}
              />
              <small>Number of parallel circuits; normally 1.</small>
            </label>
          </section>

          <div className={styles.networkToolbar}>
            <input aria-label="Search NETWORK components" type="search" placeholder="Search components…" value={search} onChange={(event) => setSearch(event.target.value)} />
            <select aria-label="Filter NETWORK component type" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
              <option value="ALL">All types</option>
              {NETWORK_COMPONENT_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
              <option value="INVALID">Unknown / invalid</option>
            </select>
            <div className={styles.networkAddGroup}>
              <select aria-label="New NETWORK component type" value={addType} onChange={(event) => setAddType(event.target.value as NetworkComponentType)}>
                {NETWORK_COMPONENT_TYPES.map((type) => (
                  <option key={type} value={type}>{type} — {NETWORK_COMPONENT_SCHEMAS[type].label}</option>
                ))}
              </select>
              <button type="button" className="button button--primary button--sm" onClick={startAdd}>
                <EditorIcon name="add" /> Add component
              </button>
            </div>
          </div>

          <div className={styles.networkWorkspace}>
            <div className={styles.networkTableWrap}>
              <table className={styles.networkTable}>
                <thead><tr><th>#</th><th>Type</th><th>ID</th><th>Connection and parameters</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  {visibleRows.map(({row, index}) => {
                    const component = componentFrom(row);
                    const type = component?.type ?? 'INVALID';
                    const rowIssues = issues.filter((issue) => issue.path.startsWith(`data[${index}]`));
                    const rowErrors = rowIssues.filter((issue) => issue.severity === 'error').length;
                    const rowWarnings = rowIssues.filter((issue) => issue.severity === 'warning').length;
                    return (
                      <tr key={index} className={editingIndex === index ? styles.networkSelectedRow : ''}>
                        <td data-label="#">{index + 1}</td>
                        <td data-label="Type"><strong>{type}</strong>{component && isKnownNetworkType(type) && <small>{NETWORK_COMPONENT_SCHEMAS[type].label}</small>}</td>
                        <td data-label="ID">{component?.ID === undefined ? '—' : String(component.ID)}</td>
                        <td data-label="Details">{component ? componentSummary(component) : 'Malformed raw value'}</td>
                        <td data-label="Status">
                          {rowErrors > 0 ? <span className={styles.networkErrorBadge}>{rowErrors} error{rowErrors === 1 ? '' : 's'}</span>
                            : rowWarnings > 0 ? <span className={styles.networkWarningBadge}>{rowWarnings} warning{rowWarnings === 1 ? '' : 's'}</span>
                              : <span className={styles.networkValidBadge}>Valid</span>}
                        </td>
                        <td data-label="Actions">
                          <div className={styles.networkRowActions}>
                            <button type="button" aria-label={`Edit NETWORK row ${index + 1}`} title="Edit component" onClick={() => openEditor(index)}><EditorIcon name="edit" /></button>
                            <button type="button" aria-label={`Duplicate NETWORK row ${index + 1}`} title="Duplicate component" disabled={!component} onClick={() => duplicateRow(index)}><EditorIcon name="copy" /></button>
                            <button type="button" aria-label={`Move NETWORK row ${index + 1} up`} title="Move up" disabled={index === 0} onClick={() => moveRow(index, -1)}><EditorIcon name="up" /></button>
                            <button type="button" aria-label={`Move NETWORK row ${index + 1} down`} title="Move down" disabled={index === rows.length - 1} onClick={() => moveRow(index, 1)}><EditorIcon name="down" /></button>
                            <button type="button" className={styles.networkDangerButton} aria-label={`Delete NETWORK row ${index + 1}`} title="Delete component" onClick={() => deleteRow(index)}><EditorIcon name="delete" /></button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {visibleRows.length === 0 && <tr><td colSpan={6} className={styles.networkEmpty}>No components match the current filters.</td></tr>}
                </tbody>
              </table>
            </div>

            {editingIndex !== undefined && (
              <ComponentEditor
                draft={draft}
                rawText={rawText}
                rawError={rawError}
                references={references}
                rows={rows}
                isNew={editingIndex >= rows.length}
                onDraft={setDraft}
                onRawText={(text) => { setRawText(text); setRawError(''); }}
                onCancel={closeEditor}
                onSave={saveEditor}
              />
            )}
          </div>

          {issues.length > 0 && (
            <section className={styles.networkIssues} aria-label="NETWORK validation issues">
              <h3>Validation</h3>
              <ul>{issues.map((issue, index) => (
                <li key={`${issue.path}:${index}`} className={issue.severity === 'error' ? styles.networkIssueError : styles.networkIssueWarning}>
                  <strong>{issue.path}</strong>: {issue.message}
                </li>
              ))}</ul>
            </section>
          )}
        </div>

        <footer className={styles.networkModalFooter}>
          <span>{rows.length} component{rows.length === 1 ? '' : 's'} · {errorCount} error{errorCount === 1 ? '' : 's'} · {warningCount} warning{warningCount === 1 ? '' : 's'}</span>
          <div>
            <button type="button" className="button button--secondary" onClick={requestClose}><EditorIcon name="cancel" /> Cancel</button>
            <button type="button" className="button button--primary" disabled={errorCount > 0} title={errorCount > 0 ? 'Fix structural errors before applying' : 'Apply NETWORK changes to the open document'} onClick={apply}><EditorIcon name="apply" /> Apply changes</button>
          </div>
        </footer>
      </div>
    </div>
  );

  return createPortal(modal, portalTarget ?? document.body);
}

interface ComponentEditorProps {
  draft?: NetworkComponent;
  rawText: string;
  rawError: string;
  references: ReturnType<typeof collectNetworkReferences>;
  rows: unknown[];
  isNew: boolean;
  onDraft: (draft: NetworkComponent) => void;
  onRawText: (text: string) => void;
  onCancel: () => void;
  onSave: () => void;
}

function ComponentEditor({
  draft,
  rawText,
  rawError,
  references,
  rows,
  isNew,
  onDraft,
  onRawText,
  onCancel,
  onSave,
}: ComponentEditorProps): ReactNode {
  if (!draft || !isKnownNetworkType(draft.type)) {
    return (
      <aside className={styles.networkComponentEditor} aria-label="Raw NETWORK component editor">
        <h3>{isNew ? 'Add raw component' : 'Edit raw component'}</h3>
        <p>Unknown component types are preserved. Edit the complete object as JSON.</p>
        <textarea aria-label="Raw NETWORK component JSON" rows={18} value={rawText} onChange={(event) => onRawText(event.target.value)} />
        {rawError && <div className={styles.networkInlineError} role="alert">{rawError}</div>}
        <EditorButtons onCancel={onCancel} onSave={onSave} />
      </aside>
    );
  }

  const schema = NETWORK_COMPONENT_SCHEMAS[draft.type];
  const inductors = rows.flatMap((row) => {
    const component = componentFrom(row);
    return component?.type === 'L' && Number.isInteger(component.ID) ? [component.ID as number] : [];
  });
  const tableIds = rows.flatMap((row) => {
    const component = componentFrom(row);
    if (component?.type !== 'TABLE' || !Array.isArray(component.data)) return [];
    return component.data.flatMap((table) => isPlainRecord(table) && Number.isInteger(table.ID) ? [table.ID as number] : []);
  });
  const targetElementIds = rows.flatMap((row) => {
    const component = componentFrom(row);
    const expectedType = draft.type === 'SETV' ? 'C' : draft.type === 'SETI' ? 'VPS' : undefined;
    return component && component.type === expectedType && Number.isInteger(component.ID) ? [component.ID as number] : [];
  });
  const change = (key: string, raw: string) => onDraft({...draft, [key]: numberValue(raw)});

  return (
    <aside className={styles.networkComponentEditor} aria-label={`${draft.type} component editor`}>
      <div className={styles.networkEditorHeading}>
        <div><h3>{isNew ? 'Add' : 'Edit'} {draft.type}</h3><strong>{schema.label}</strong></div>
        <span className={styles.networkTypeBadge}>{draft.type}</span>
      </div>
      <p>{schema.description}</p>
      {schema.fields.map((field) => (
        <FieldInput
          key={field.key}
          field={field}
          value={draft[field.key]}
          options={field.kind === 'series' ? references.seriesIds
            : field.kind === 'time' ? references.timeIds
                : field.kind === 'inductor' ? inductors
                : field.kind === 'table' ? tableIds
                  : field.kind === 'element' ? targetElementIds : []}
          onChange={(raw) => change(field.key, raw)}
        />
      ))}
      {draft.type === 'TABLE' && <TableDatasets draft={draft} rows={rows} onDraft={onDraft} />}
      {draft.type === 'SWITCH' && <SwitchTimings draft={draft} onDraft={onDraft} />}
      <EditorButtons onCancel={onCancel} onSave={onSave} />
    </aside>
  );
}

function FieldInput({field, value, options, onChange}: {
  field: NetworkFieldDefinition;
  value: unknown;
  options: number[];
  onChange: (value: string) => void;
}): ReactNode {
  const listId = options.length > 0 ? `network-options-${field.kind}-${field.key}` : undefined;
  if (field.key === 'PHASE_OP') {
    return (
      <label className={styles.networkField}>
        <span>{field.label}</span>
        <select aria-label={field.label} value={inputValue(value)} onChange={(event) => onChange(event.target.value)}>
          <option value="">Select a time mode…</option>
          <option value="0">0 — real time (seconds)</option>
          <option value="1">1 — phase angle (degrees)</option>
        </select>
        <small>{field.help}</small>
      </label>
    );
  }
  return (
    <label className={styles.networkField}>
      <span>{field.label}{field.unit && <em>{field.unit}</em>}</span>
      <input
        aria-label={field.label}
        type="number"
        step={field.kind === 'number' ? 'any' : '1'}
        list={listId}
        value={inputValue(value)}
        onChange={(event) => onChange(event.target.value)}
      />
      {listId && <datalist id={listId}>{options.map((option) => <option key={option} value={option} />)}</datalist>}
      <small>{field.help}{options.length > 0 && ' Known values are suggested; manual IDs are allowed.'}</small>
    </label>
  );
}

function TableDatasets({draft, rows, onDraft}: {draft: NetworkComponent; rows: unknown[]; onDraft: (draft: NetworkComponent) => void}): ReactNode {
  const tables = Array.isArray(draft.data) ? draft.data : [];
  const updateTables = (next: unknown[]) => onDraft({...draft, NUMBER: next.length, data: next});
  const updateTable = (index: number, update: (table: Record<string, unknown>) => Record<string, unknown>) => {
    const next = [...tables];
    const table = isPlainRecord(next[index]) ? next[index] : {};
    next[index] = update({...table});
    updateTables(next);
  };
  return (
    <section className={styles.networkNestedEditor}>
      <div className={styles.networkNestedHeading}><h4>I–V datasets ({tables.length})</h4><button type="button" onClick={() => updateTables([...tables, {ID: nextTableId(rows), NO_DATA: 0, CURRENT: [], VOLTAGE: []}])}><EditorIcon name="add" /> Add dataset</button></div>
      {tables.map((tableValue, tableIndex) => {
        const table = isPlainRecord(tableValue) ? tableValue : {};
        const current = Array.isArray(table.CURRENT) ? table.CURRENT : [];
        const voltage = Array.isArray(table.VOLTAGE) ? table.VOLTAGE : [];
        const pointCount = Math.max(current.length, voltage.length);
        return (
          <div className={styles.networkDataset} key={tableIndex}>
            <div className={styles.networkDatasetHeader}>
              <label>Table ID <input aria-label={`Table ${tableIndex + 1} ID`} type="number" step="1" value={inputValue(table.ID)} onChange={(event) => updateTable(tableIndex, (item) => ({...item, ID: numberValue(event.target.value)}))} /></label>
              <button type="button" className={styles.networkDangerButton} aria-label={`Remove table dataset ${tableIndex + 1}`} onClick={() => updateTables(tables.filter((_, index) => index !== tableIndex))}><EditorIcon name="delete" /> Remove dataset</button>
            </div>
            <div className={styles.networkPointHeader}><span>Current (A)</span><span>Voltage (V)</span><span /></div>
            {Array.from({length: pointCount}, (_, pointIndex) => (
              <div className={styles.networkPointRow} key={pointIndex}>
                <input aria-label={`Table ${tableIndex + 1} current ${pointIndex + 1}`} type="number" step="any" value={inputValue(current[pointIndex])} onChange={(event) => updateTable(tableIndex, (item) => {
                  const nextCurrent = Array.isArray(item.CURRENT) ? [...item.CURRENT] : [];
                  nextCurrent[pointIndex] = numberValue(event.target.value);
                  return {...item, CURRENT: nextCurrent, NO_DATA: Math.max(nextCurrent.length, Array.isArray(item.VOLTAGE) ? item.VOLTAGE.length : 0)};
                })} />
                <input aria-label={`Table ${tableIndex + 1} voltage ${pointIndex + 1}`} type="number" step="any" value={inputValue(voltage[pointIndex])} onChange={(event) => updateTable(tableIndex, (item) => {
                  const nextVoltage = Array.isArray(item.VOLTAGE) ? [...item.VOLTAGE] : [];
                  nextVoltage[pointIndex] = numberValue(event.target.value);
                  return {...item, VOLTAGE: nextVoltage, NO_DATA: Math.max(nextVoltage.length, Array.isArray(item.CURRENT) ? item.CURRENT.length : 0)};
                })} />
                <button type="button" aria-label={`Remove table ${tableIndex + 1} point ${pointIndex + 1}`} onClick={() => updateTable(tableIndex, (item) => {
                  const nextCurrent = Array.isArray(item.CURRENT) ? item.CURRENT.filter((_, index) => index !== pointIndex) : [];
                  const nextVoltage = Array.isArray(item.VOLTAGE) ? item.VOLTAGE.filter((_, index) => index !== pointIndex) : [];
                  return {...item, CURRENT: nextCurrent, VOLTAGE: nextVoltage, NO_DATA: nextCurrent.length};
                })}><EditorIcon name="delete" /></button>
              </div>
            ))}
            <button type="button" onClick={() => updateTable(tableIndex, (item) => {
              const nextCurrent = [...(Array.isArray(item.CURRENT) ? item.CURRENT : []), ''];
              const nextVoltage = [...(Array.isArray(item.VOLTAGE) ? item.VOLTAGE : []), ''];
              return {...item, CURRENT: nextCurrent, VOLTAGE: nextVoltage, NO_DATA: nextCurrent.length};
            })}><EditorIcon name="add" /> Add I–V point</button>
          </div>
        );
      })}
    </section>
  );
}

function SwitchTimings({draft, onDraft}: {draft: NetworkComponent; onDraft: (draft: NetworkComponent) => void}): ReactNode {
  const onTimes = Array.isArray(draft.ON_TIME) ? draft.ON_TIME : [];
  const offTimes = Array.isArray(draft.OFF_TIME) ? draft.OFF_TIME : [];
  const count = Math.max(onTimes.length, offTimes.length);
  const unit = draft.PHASE_OP === 1 ? 'deg' : 's';
  const update = (nextOn: unknown[], nextOff: unknown[]) => onDraft({...draft, ON_TIME: nextOn, OFF_TIME: nextOff});
  return (
    <section className={styles.networkNestedEditor}>
      <div className={styles.networkNestedHeading}><h4>Switch intervals ({unit})</h4><button type="button" onClick={() => update([...onTimes, ''], [...offTimes, ''])}><EditorIcon name="add" /> Add interval</button></div>
      <div className={styles.networkPointHeader}><span>On time</span><span>Off time</span><span /></div>
      {Array.from({length: count}, (_, index) => (
        <div className={styles.networkPointRow} key={index}>
          <input aria-label={`Switch on time ${index + 1}`} type="number" step="any" value={inputValue(onTimes[index])} onChange={(event) => {
            const next = [...onTimes]; next[index] = numberValue(event.target.value); update(next, offTimes);
          }} />
          <input aria-label={`Switch off time ${index + 1}`} type="number" step="any" value={inputValue(offTimes[index])} onChange={(event) => {
            const next = [...offTimes]; next[index] = numberValue(event.target.value); update(onTimes, next);
          }} />
          <button type="button" className={styles.networkDangerButton} aria-label={`Remove switch interval ${index + 1}`} title="Remove interval" onClick={() => update(onTimes.filter((_, item) => item !== index), offTimes.filter((_, item) => item !== index))}><EditorIcon name="delete" /></button>
        </div>
      ))}
    </section>
  );
}

function EditorButtons({onCancel, onSave}: {onCancel: () => void; onSave: () => void}): ReactNode {
  return (
    <div className={styles.networkEditorButtons}>
      <button type="button" className="button button--secondary button--sm" onClick={onCancel}><EditorIcon name="cancel" /> Cancel row</button>
      <button type="button" className="button button--primary button--sm" onClick={onSave}><EditorIcon name="save" /> Save row</button>
    </div>
  );
}
