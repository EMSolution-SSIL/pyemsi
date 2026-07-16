import React, {type ReactNode, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

import CircuitEditorModal from './CircuitEditorModal';
import EditorIcon from './EditorIcon';
import {
  createFieldSourceEntry,
  createFieldSourceRow,
  deepClone,
  FIELD_SOURCE_SCHEMAS,
  FIELD_SOURCE_TYPES,
  fieldSourceRows,
  fieldSourceSummary,
  findFieldSourceEntries,
  getFieldValue,
  inspectFieldSourceEntry,
  isPlainRecord,
  normalizeFieldSources,
  replaceFieldSourceEntries,
  rowSchemaForSource,
  setFieldValue,
  sourceRowTypes,
  validateFieldSources,
  visibleFieldSourceFields,
  type FieldSourceFieldDefinition,
  type FieldSourceRowSchema,
  type FieldSourceType,
} from './fieldSourceModel';
import NetworkEditorModal from './NetworkEditorModal';
import styles from './styles.module.css';

const OVERVIEW_URL = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/17_Field_Source.html';

interface FieldSourceEditorModalProps {
  documentName: string;
  value: unknown;
  portalTarget?: Element;
  onApply: (value: unknown) => void;
  onClose: () => void;
}

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function numberValue(raw: string): number | string {
  return raw.trim() === '' ? '' : Number(raw);
}

function arrayText(value: unknown): string {
  return Array.isArray(value) ? value.join(', ') : '';
}

function arrayValue(raw: string): Array<number | string> {
  if (raw.trim() === '') return [];
  return raw.split(/[\s,]+/).filter(Boolean).map((part) => {
    const parsed = Number(part);
    return Number.isFinite(parsed) ? parsed : part;
  });
}

export default function FieldSourceEditorModal({
  documentName,
  value,
  portalTarget,
  onApply,
  onClose,
}: FieldSourceEditorModalProps): ReactNode {
  const initialRootRef = useRef(replaceFieldSourceEntries(value, findFieldSourceEntries(value)));
  const initialJsonRef = useRef(JSON.stringify(initialRootRef.current));
  const [draftRoot, setDraftRoot] = useState(initialRootRef.current);
  const [selectedIndex, setSelectedIndex] = useState<number>();
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [addType, setAddType] = useState<FieldSourceType>('COIL');
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const draftRootRef = useRef(draftRoot);
  const restoreFocusRef = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement ? document.activeElement : null,
  );
  const entries = findFieldSourceEntries(draftRoot);
  const selected = selectedIndex === undefined ? undefined : inspectFieldSourceEntry(entries[selectedIndex]);
  const specialOpen = selected?.kind === 'known' && isPlainRecord(selected.definition) && ['NETWORK', 'CIRCUIT'].includes(selected.type);
  const specialOpenRef = useRef(specialOpen);
  specialOpenRef.current = specialOpen;

  useEffect(() => { draftRootRef.current = draftRoot; }, [draftRoot]);

  const requestClose = useCallback(() => {
    const dirty = JSON.stringify(draftRootRef.current) !== initialJsonRef.current;
    if (dirty && !window.confirm('Discard the unsaved Field Source changes?')) return;
    onClose();
  }, [onClose]);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeButtonRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (specialOpenRef.current) return;
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

  useEffect(() => {
    if (selectedIndex === undefined) {
      closeButtonRef.current?.focus();
      return;
    }
    dialogRef.current?.querySelector<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled)')?.focus();
  }, [selectedIndex]);

  const issues = useMemo(() => validateFieldSources(draftRoot), [draftRoot]);
  const errorCount = issues.filter((issue) => issue.severity === 'error').length;
  const warningCount = issues.filter((issue) => issue.severity === 'warning').length;

  const setEntries = (nextEntries: unknown[]) => setDraftRoot((current) => replaceFieldSourceEntries(current, nextEntries));

  const addEntry = () => {
    const next = [...entries, createFieldSourceEntry(addType)];
    setEntries(next);
    setSelectedIndex(next.length - 1);
  };

  const duplicateEntry = (index: number) => {
    const next = [...entries];
    next.splice(index + 1, 0, deepClone(entries[index]));
    setEntries(next);
  };

  const moveEntry = (index: number, direction: -1 | 1) => {
    const target = index + direction;
    if (target < 0 || target >= entries.length) return;
    const next = [...entries];
    [next[index], next[target]] = [next[target], next[index]];
    setEntries(next);
    if (selectedIndex === index) setSelectedIndex(target);
  };

  const deleteEntry = (index: number) => {
    if (!window.confirm(`Delete Field Source entry ${index + 1}?`)) return;
    setEntries(entries.filter((_, itemIndex) => itemIndex !== index));
    if (selectedIndex === index) setSelectedIndex(undefined);
  };

  const replaceEntry = (index: number, entry: unknown) => {
    const next = [...entries];
    next[index] = entry;
    setEntries(next);
  };

  const changeEntryType = (index: number, type: FieldSourceType) => {
    const inspected = inspectFieldSourceEntry(entries[index]);
    if (inspected.kind === 'known' && inspected.type === type && inspected.key !== 'EPOTNODE') return;
    if (!window.confirm(`Replace Field Source entry ${index + 1} with a new ${type} definition? Existing values in this entry will be discarded.`)) return;
    replaceEntry(index, createFieldSourceEntry(type));
  };

  const visibleEntries = entries.map((entry, index) => ({entry, index, inspected: inspectFieldSourceEntry(entry)})).filter(({entry, inspected}) => {
    const type = inspected.kind === 'known' ? inspected.type : inspected.reason.toUpperCase();
    if (typeFilter !== 'ALL' && type !== typeFilter) return false;
    return `${type} ${fieldSourceSummary(entry)} ${JSON.stringify(entry)}`.toLowerCase().includes(search.trim().toLowerCase());
  });

  const apply = () => {
    if (errorCount > 0) return;
    onApply(normalizeFieldSources(draftRoot));
  };

  const detail = selectedIndex === undefined ? undefined : (
    selected?.kind === 'known' && isPlainRecord(selected.definition) && selected.type === 'NETWORK' ? (
      <NetworkEditorModal
        embedded
        initialSection={entries.slice(0, selectedIndex).filter((entry) => {
          const inspected = inspectFieldSourceEntry(entry);
          return inspected.kind === 'known' && inspected.type === 'NETWORK';
        }).length}
        documentName={documentName}
        value={draftRoot}
        onClose={() => setSelectedIndex(undefined)}
        onApply={(nextRoot) => { setDraftRoot(nextRoot); setSelectedIndex(undefined); }}
      />
    ) : selected?.kind === 'known' && isPlainRecord(selected.definition) && selected.type === 'CIRCUIT' ? (
      <CircuitEditorModal
        embedded
        initialSection={entries.slice(0, selectedIndex).filter((entry) => {
          const inspected = inspectFieldSourceEntry(entry);
          return inspected.kind === 'known' && inspected.type === 'CIRCUIT';
        }).length}
        documentName={documentName}
        value={draftRoot}
        onClose={() => setSelectedIndex(undefined)}
        onApply={(nextRoot) => { setDraftRoot(nextRoot); setSelectedIndex(undefined); }}
      />
    ) : (
      <SourceDetailEditor
        entry={entries[selectedIndex]}
        index={selectedIndex}
        issues={issues.filter((issue) => issue.sourceIndex === selectedIndex)}
        onBack={() => setSelectedIndex(undefined)}
        onChange={(entry) => replaceEntry(selectedIndex, entry)}
        onChangeType={(type) => changeEntryType(selectedIndex, type)}
      />
    )
  );

  const modal = (
    <div className={styles.networkModalBackdrop} onMouseDown={(event) => {
      if (event.target === event.currentTarget && !specialOpen) requestClose();
    }}>
      <div ref={dialogRef} className={`${styles.networkModal} ${styles.fieldSourceModal}`} role="dialog" aria-modal="true" aria-labelledby="field-source-editor-title">
        <header className={styles.networkModalHeader}>
          <div>
            <h2 id="field-source-editor-title">Field Source editor</h2>
            <div className={styles.networkModalSubtitle}>{documentName}</div>
          </div>
          <div className={styles.networkHeaderActions}>
            <a href={OVERVIEW_URL} target="_blank" rel="noreferrer">Field Source documentation <EditorIcon name="external" /></a>
            {!specialOpen && <button ref={closeButtonRef} type="button" className={styles.networkIconButton} aria-label="Close Field Source editor" title="Close Field Source editor" onClick={requestClose}><EditorIcon name="close" /></button>}
          </div>
        </header>

        <div className={`${styles.networkModalBody} ${styles.fieldSourceModalBody}`}>
          {detail ?? (
            <>
              <div className={styles.networkToolbar}>
                <input aria-label="Search Field Sources" type="search" placeholder="Search sources…" value={search} onChange={(event) => setSearch(event.target.value)} />
                <select aria-label="Filter Field Source type" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
                  <option value="ALL">All types</option>
                  {FIELD_SOURCE_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
                  <option value="UNKNOWN">Unknown</option>
                  <option value="MALFORMED">Malformed</option>
                  <option value="MULTIPLE">Multiple definitions</option>
                </select>
                <div className={styles.networkAddGroup}>
                  <select aria-label="New Field Source type" value={addType} onChange={(event) => setAddType(event.target.value as FieldSourceType)}>
                    {FIELD_SOURCE_TYPES.map((type) => <option key={type} value={type}>{type} — {FIELD_SOURCE_SCHEMAS[type].label}</option>)}
                  </select>
                  <button type="button" className="button button--primary button--sm" onClick={addEntry}><EditorIcon name="add" /> Add source</button>
                </div>
              </div>

              <div className={styles.networkTableWrap}>
                <table className={styles.networkTable}>
                  <thead><tr><th>#</th><th>Type</th><th>Series</th><th>Summary</th><th>Status</th><th>Actions</th></tr></thead>
                  <tbody>
                    {visibleEntries.map(({entry, index, inspected}) => {
                      const entryIssues = issues.filter((issue) => issue.sourceIndex === index);
                      const errors = entryIssues.filter((issue) => issue.severity === 'error').length;
                      const warnings = entryIssues.filter((issue) => issue.severity === 'warning').length;
                      const definition = inspected.kind === 'known' && isPlainRecord(inspected.definition) ? inspected.definition : undefined;
                      const type = inspected.kind === 'known' ? inspected.type : inspected.reason.toUpperCase();
                      return (
                        <tr key={index}>
                          <td data-label="#">{index + 1}</td>
                          <td data-label="Type"><strong>{type}</strong>{inspected.kind === 'known' && <small>{FIELD_SOURCE_SCHEMAS[inspected.type].label}{inspected.key === 'EPOTNODE' ? ' · legacy key' : ''}</small>}</td>
                          <td data-label="Series">{definition?.SERIES_ID === undefined ? '—' : String(definition.SERIES_ID)}</td>
                          <td data-label="Summary">{fieldSourceSummary(entry)}</td>
                          <td data-label="Status">{errors > 0 ? <span className={styles.networkErrorBadge}>{errors} error{errors === 1 ? '' : 's'}</span>
                            : warnings > 0 ? <span className={styles.networkWarningBadge}>{warnings} warning{warnings === 1 ? '' : 's'}</span>
                              : <span className={styles.networkValidBadge}>Valid</span>}</td>
                          <td data-label="Actions"><div className={styles.networkRowActions}>
                            <button type="button" aria-label={`Edit Field Source row ${index + 1}`} title="Edit source" onClick={() => setSelectedIndex(index)}><EditorIcon name="edit" /></button>
                            <button type="button" aria-label={`Duplicate Field Source row ${index + 1}`} title="Duplicate source" onClick={() => duplicateEntry(index)}><EditorIcon name="copy" /></button>
                            <button type="button" aria-label={`Move Field Source row ${index + 1} up`} title="Move up" disabled={index === 0} onClick={() => moveEntry(index, -1)}><EditorIcon name="up" /></button>
                            <button type="button" aria-label={`Move Field Source row ${index + 1} down`} title="Move down" disabled={index === entries.length - 1} onClick={() => moveEntry(index, 1)}><EditorIcon name="down" /></button>
                            <button type="button" className={styles.networkDangerButton} aria-label={`Delete Field Source row ${index + 1}`} title="Delete source" onClick={() => deleteEntry(index)}><EditorIcon name="delete" /></button>
                          </div></td>
                        </tr>
                      );
                    })}
                    {visibleEntries.length === 0 && <tr><td colSpan={6} className={styles.networkEmpty}>No Field Sources match the current filters.</td></tr>}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>

        {!specialOpen && <footer className={styles.networkModalFooter}>
          <span>{entries.length} source{entries.length === 1 ? '' : 's'} · {errorCount} error{errorCount === 1 ? '' : 's'} · {warningCount} warning{warningCount === 1 ? '' : 's'}</span>
          <div>
            <button type="button" className="button button--secondary" onClick={requestClose}><EditorIcon name="cancel" /> Cancel</button>
            <button type="button" className="button button--primary" disabled={errorCount > 0} title={errorCount > 0 ? 'Fix structural errors before applying' : 'Apply all Field Source changes to the open document'} onClick={apply}><EditorIcon name="apply" /> Apply changes</button>
          </div>
        </footer>}
      </div>
    </div>
  );
  return createPortal(modal, portalTarget ?? document.body);
}

function SourceDetailEditor({entry, index, issues, onBack, onChange, onChangeType}: {
  entry: unknown;
  index: number;
  issues: ReturnType<typeof validateFieldSources>;
  onBack: () => void;
  onChange: (entry: unknown) => void;
  onChangeType: (type: FieldSourceType) => void;
}): ReactNode {
  const inspected = inspectFieldSourceEntry(entry);
  if (inspected.kind !== 'known' || !isPlainRecord(inspected.definition)) {
    return (
      <div className={styles.fieldSourceDetail}>
        <DetailHeading index={index} type={inspected.kind === 'known' ? inspected.type : undefined} onBack={onBack} onChangeType={onChangeType} />
        <RawJsonEditor label="Raw Field Source entry JSON" value={entry} requireObject onSave={onChange} />
        <ValidationIssues issues={issues} />
      </div>
    );
  }
  const schema = FIELD_SOURCE_SCHEMAS[inspected.type];
  const definition = inspected.definition;
  const updateDefinition = (next: Record<string, unknown>) => onChange({...inspected.wrapper, [inspected.key]: next});
  return (
    <div className={styles.fieldSourceDetail}>
      <DetailHeading index={index} type={inspected.type} onBack={onBack} onChangeType={onChangeType} />
      <div className={styles.fieldSourceDescription}>
        <div><strong>{schema.label}</strong><p>{schema.description}</p></div>
        <a href={schema.documentationUrl} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a>
      </div>
      <div className={styles.fieldSourceFieldGrid}>
        {visibleFieldSourceFields(schema.fields, definition).map((field) => (
          <FieldInput key={field.key} field={field} value={getFieldValue(definition, field.key)} onChange={(nextValue) => {
            const next = deepClone(definition);
            setFieldValue(next, field.key, nextValue);
            updateDefinition(next);
          }} />
        ))}
      </div>
      {schema.rowLabel && (
        <NestedRowsEditor type={inspected.type} definition={definition} onDefinition={updateDefinition} />
      )}
      <ValidationIssues issues={issues} />
    </div>
  );
}

function DetailHeading({index, type, onBack, onChangeType}: {
  index: number;
  type?: FieldSourceType;
  onBack: () => void;
  onChangeType: (type: FieldSourceType) => void;
}): ReactNode {
  return (
    <div className={styles.fieldSourceDetailHeading}>
      <button type="button" className="button button--secondary button--sm" onClick={onBack}><EditorIcon name="up" /> Back to sources</button>
      <h3>Entry {index + 1}{type ? ` · ${type}` : ' · Raw JSON'}</h3>
      <label>Change type<select aria-label="Field Source type" value={type ?? ''} onChange={(event) => onChangeType(event.target.value as FieldSourceType)}>
        {!type && <option value="">Select replacement…</option>}
        {FIELD_SOURCE_TYPES.map((item) => <option key={item} value={item}>{item} — {FIELD_SOURCE_SCHEMAS[item].label}</option>)}
      </select></label>
    </div>
  );
}

function FieldInput({field, value, onChange}: {
  field: FieldSourceFieldDefinition;
  value: unknown;
  onChange: (value: unknown) => void;
}): ReactNode {
  const label = `${field.label} (${field.key})`;
  if (field.kind === 'vector3') {
    const values = Array.isArray(value) ? value : ['', '', ''];
    return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span><div className={styles.fieldSourceVector}>
      {['X', 'Y', 'Z'].map((axis, index) => <input key={axis} aria-label={`${label} ${axis}`} type="number" step="any" value={inputValue(values[index])} onChange={(event) => {
        const next = [...values];
        next[index] = numberValue(event.target.value);
        onChange(next);
      }} />)}
      </div><small>{field.help}</small></label>;
  }
  if (field.kind === 'integer-array' || field.kind === 'number-array') {
    return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span>
      <input aria-label={label} type="text" value={arrayText(value)} placeholder="Comma-separated values" onChange={(event) => onChange(arrayValue(event.target.value))} />
      <small>{field.help}</small></label>;
  }
  if (field.kind === 'enum') {
    return <label className={styles.networkField}><span>{field.label}<em>{field.key}</em></span><select aria-label={label} value={inputValue(value)} onChange={(event) => onChange(numberValue(event.target.value))}>
      {!field.required && <option value="">Not set</option>}
      {field.options?.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select><small>{field.help}</small></label>;
  }
  return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span>
    <input aria-label={label} type={field.kind === 'string' ? 'text' : 'number'} step={field.kind === 'integer' ? '1' : 'any'} value={inputValue(value)} onChange={(event) => onChange(field.kind === 'string' ? event.target.value : numberValue(event.target.value))} />
    <small>{field.help}</small></label>;
}

function NestedRowsEditor({type, definition, onDefinition}: {
  type: FieldSourceType;
  definition: Record<string, unknown>;
  onDefinition: (definition: Record<string, unknown>) => void;
}): ReactNode {
  const rows = fieldSourceRows(definition);
  const rowTypes = sourceRowTypes(type);
  const [addRowType, setAddRowType] = useState(rowTypes[0] ?? '');
  const replaceRows = (nextRows: unknown[]) => onDefinition({...definition, data: nextRows});
  const addRow = () => replaceRows([...rows, createFieldSourceRow(type, definition, addRowType)]);
  const updateRow = (index: number, row: unknown) => {
    const next = [...rows]; next[index] = row; replaceRows(next);
  };
  const moveRow = (index: number, direction: -1 | 1) => {
    const target = index + direction;
    if (target < 0 || target >= rows.length) return;
    const next = [...rows]; [next[index], next[target]] = [next[target], next[index]]; replaceRows(next);
  };
  const deleteRow = (index: number) => {
    if (window.confirm(`Delete ${FIELD_SOURCE_SCHEMAS[type].rowLabel} ${index + 1}?`)) replaceRows(rows.filter((_, rowIndex) => rowIndex !== index));
  };
  return (
    <section className={styles.fieldSourceRows}>
      <div className={styles.fieldSourceRowsHeading}>
        <div><h4>{FIELD_SOURCE_SCHEMAS[type].rowLabel}s</h4><p>Add, reorder, duplicate, or remove nested definitions. Extra JSON properties are retained.</p></div>
        <div className={styles.networkAddGroup}>{rowTypes.length > 0 && <select aria-label={`New ${type} row type`} value={addRowType} onChange={(event) => setAddRowType(event.target.value)}>
          {rowTypes.map((rowType) => <option key={rowType} value={rowType}>{rowType} — {FIELD_SOURCE_SCHEMAS.COIL.rowSchemas?.[rowType].label}</option>)}
        </select>}<button type="button" className="button button--primary button--sm" onClick={addRow}><EditorIcon name="add" /> Add row</button></div>
      </div>
      {rows.map((row, index) => <NestedRowCard key={index} type={type} definition={definition} row={row} index={index} count={rows.length}
        onChange={(next) => updateRow(index, next)} onDuplicate={() => {
          const next = [...rows]; next.splice(index + 1, 0, deepClone(row)); replaceRows(next);
        }} onMove={(direction) => moveRow(index, direction)} onDelete={() => deleteRow(index)} />)}
      {rows.length === 0 && <div className={styles.networkEmpty}>No nested rows are defined.</div>}
    </section>
  );
}

function NestedRowCard({type, definition, row, index, count, onChange, onDuplicate, onMove, onDelete}: {
  type: FieldSourceType;
  definition: Record<string, unknown>;
  row: unknown;
  index: number;
  count: number;
  onChange: (row: unknown) => void;
  onDuplicate: () => void;
  onMove: (direction: -1 | 1) => void;
  onDelete: () => void;
}): ReactNode {
  const rowSchema = rowSchemaForSource(type, definition, row);
  if (!isPlainRecord(row) || !rowSchema) {
    return <div className={styles.fieldSourceRowCard}><RowCardHeader index={index} count={count} title="Raw nested row" onDuplicate={onDuplicate} onMove={onMove} onDelete={onDelete} />
      <RawJsonEditor label={`${type} raw row ${index + 1}`} value={row} requireObject onSave={onChange} /></div>;
  }
  const changeCoilType = (nextType: string) => {
    if (nextType === row.type) return;
    if (window.confirm(`Replace COIL row ${index + 1} with a new ${nextType} row?`)) onChange(createFieldSourceRow(type, definition, nextType));
  };
  return <div className={styles.fieldSourceRowCard}>
    <RowCardHeader index={index} count={count} title={rowSchema.type ? `${rowSchema.type} — ${rowSchema.label}` : rowSchema.label} onDuplicate={onDuplicate} onMove={onMove} onDelete={onDelete} />
    <p>{rowSchema.description}</p>
    {type === 'COIL' && <label className={styles.networkField}><span>Element type<em>type</em></span><select aria-label={`COIL row ${index + 1} type`} value={String(row.type)} onChange={(event) => changeCoilType(event.target.value)}>
      {sourceRowTypes(type).map((item) => <option key={item} value={item}>{item} — {FIELD_SOURCE_SCHEMAS.COIL.rowSchemas?.[item].label}</option>)}
    </select></label>}
    <div className={styles.fieldSourceFieldGrid}>{rowSchema.fields.map((field) => <FieldInput key={field.key} field={field} value={getFieldValue(row, field.key)} onChange={(nextValue) => {
      const next = deepClone(row); setFieldValue(next, field.key, nextValue); onChange(next);
    }} />)}</div>
  </div>;
}

function RowCardHeader({index, count, title, onDuplicate, onMove, onDelete}: {
  index: number;
  count: number;
  title: string;
  onDuplicate: () => void;
  onMove: (direction: -1 | 1) => void;
  onDelete: () => void;
}): ReactNode {
  return <div className={styles.fieldSourceRowCardHeader}><h5>{index + 1}. {title}</h5><div className={styles.networkRowActions}>
    <button type="button" aria-label={`Duplicate nested row ${index + 1}`} onClick={onDuplicate}><EditorIcon name="copy" /></button>
    <button type="button" aria-label={`Move nested row ${index + 1} up`} disabled={index === 0} onClick={() => onMove(-1)}><EditorIcon name="up" /></button>
    <button type="button" aria-label={`Move nested row ${index + 1} down`} disabled={index === count - 1} onClick={() => onMove(1)}><EditorIcon name="down" /></button>
    <button type="button" className={styles.networkDangerButton} aria-label={`Delete nested row ${index + 1}`} onClick={onDelete}><EditorIcon name="delete" /></button>
  </div></div>;
}

function RawJsonEditor({label, value, requireObject, onSave}: {
  label: string;
  value: unknown;
  requireObject?: boolean;
  onSave: (value: unknown) => void;
}): ReactNode {
  const [text, setText] = useState(JSON.stringify(value, null, 2));
  const [error, setError] = useState('');
  return <div className={styles.fieldSourceRawEditor}><textarea aria-label={label} rows={16} value={text} onChange={(event) => { setText(event.target.value); setError(''); }} />
    {error && <div className={styles.networkInlineError}>{error}</div>}
    <div className={styles.networkEditorButtons}><button type="button" className="button button--primary button--sm" onClick={() => {
      try {
        const parsed = JSON.parse(text);
        if (requireObject && !isPlainRecord(parsed)) { setError('Value must be a JSON object.'); return; }
        onSave(parsed);
      } catch (caught) { setError(caught instanceof Error ? caught.message : 'Invalid JSON.'); }
    }}><EditorIcon name="save" /> Save raw JSON</button></div>
  </div>;
}

function ValidationIssues({issues}: {issues: ReturnType<typeof validateFieldSources>}): ReactNode {
  if (issues.length === 0) return null;
  return <section className={styles.networkIssues} aria-label="Field Source validation issues"><h3>Validation</h3><ul>{issues.map((issue, index) => (
    <li key={`${issue.path}:${index}`} className={issue.severity === 'error' ? styles.networkIssueError : styles.networkIssueWarning}><strong>{issue.path}</strong>: {issue.message}</li>
  ))}</ul></section>;
}
