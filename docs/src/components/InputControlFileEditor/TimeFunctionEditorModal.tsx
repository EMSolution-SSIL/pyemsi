import React, {type ReactNode, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

import AddItemMenu from './AddItemMenu';
import EditorIcon from './EditorIcon';
import styles from './styles.module.css';
import {
  changeTimeFunctionOption,
  collectTimeFunctionConsumers,
  createRawTimeFunction,
  createTimeFunction,
  deepClone,
  defaultPreviewDuration,
  duplicateTimeFunction,
  findTimeFunctions,
  inspectTimeFunctionEntry,
  isPlainRecord,
  replaceTimeFunctions,
  sampleTimeFunction,
  SUPPORTED_TIME_FUNCTION_OPTIONS,
  TIME_FUNCTION_DOCUMENTATION,
  TIME_FUNCTION_EXPRESSION_DOCUMENTATION,
  TIME_FUNCTION_SCHEMAS,
  timeFunctionSummary,
  validateTimeFunctions,
  type SupportedTimeFunctionOption,
  type TimeFunctionFieldDefinition,
  type TimeFunctionValidationIssue,
} from './timeFunctionModel';

interface TimeFunctionEditorModalProps {
  documentName: string;
  value: unknown;
  portalTarget?: Element;
  onApply: (value: unknown) => void;
  onClose: () => void;
}

type AddChoice = `${SupportedTimeFunctionOption}` | 'raw';
type StatusFilter = 'ALL' | 'VALID' | 'WARNING' | 'ERROR';

const ADD_OPTIONS: Array<{value: AddChoice; label: string; description: string}> = [
  ...SUPPORTED_TIME_FUNCTION_OPTIONS.map((option) => ({
    value: String(option) as AddChoice,
    label: TIME_FUNCTION_SCHEMAS[option].label,
    description: TIME_FUNCTION_SCHEMAS[option].description,
  })),
  {value: 'raw', label: 'Raw JSON', description: 'Create an unsupported or advanced time function, including OPTION 3 motion equations.'},
];

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function numberValue(raw: string): number | string {
  return raw.trim() === '' ? '' : Number(raw);
}

export default function TimeFunctionEditorModal({
  documentName,
  value,
  portalTarget,
  onApply,
  onClose,
}: TimeFunctionEditorModalProps): ReactNode {
  const initialRootRef = useRef(replaceTimeFunctions(value, findTimeFunctions(value)));
  const initialJsonRef = useRef(JSON.stringify(initialRootRef.current));
  const [draftRoot, setDraftRoot] = useState(initialRootRef.current);
  const [selectedIndex, setSelectedIndex] = useState<number>();
  const [search, setSearch] = useState('');
  const [optionFilter, setOptionFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const draftRootRef = useRef(draftRoot);
  const restoreFocusRef = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement ? document.activeElement : null,
  );
  const entries = findTimeFunctions(draftRoot);
  const issues = useMemo(() => validateTimeFunctions(draftRoot), [draftRoot]);
  const consumers = useMemo(() => collectTimeFunctionConsumers(draftRoot), [draftRoot]);
  const errorCount = issues.filter((issue) => issue.severity === 'error').length;
  const warningCount = issues.filter((issue) => issue.severity === 'warning').length;

  useEffect(() => { draftRootRef.current = draftRoot; }, [draftRoot]);

  const requestClose = useCallback(() => {
    if (JSON.stringify(draftRootRef.current) !== initialJsonRef.current
      && !window.confirm('Discard the unsaved Time Function changes?')) return;
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

  useEffect(() => {
    if (selectedIndex === undefined) closeButtonRef.current?.focus();
    else dialogRef.current?.querySelector<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled)')?.focus();
  }, [selectedIndex]);

  const setEntries = (nextEntries: unknown[]) => setDraftRoot((current) => replaceTimeFunctions(current, nextEntries));
  const replaceEntry = (index: number, entry: unknown) => {
    const next = [...entries];
    next[index] = entry;
    setEntries(next);
  };

  const addEntry = (choice: AddChoice) => {
    const entry = choice === 'raw' ? createRawTimeFunction(entries) : createTimeFunction(Number(choice) as SupportedTimeFunctionOption, entries);
    const next = [...entries, entry];
    setEntries(next);
    setSelectedIndex(next.length - 1);
  };

  const duplicateEntry = (index: number) => {
    const next = [...entries];
    next.splice(index + 1, 0, duplicateTimeFunction(entries[index], entries));
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

  const usageFor = (entry: unknown) => {
    const id = isPlainRecord(entry) && Number.isInteger(entry.TIME_ID) ? entry.TIME_ID as number : undefined;
    return id === undefined ? [] : consumers.filter((consumer) => consumer.timeId === id);
  };

  const deleteEntry = (index: number) => {
    const usage = usageFor(entries[index]);
    const warning = usage.length > 0 ? ` It is referenced ${usage.length} time${usage.length === 1 ? '' : 's'} elsewhere in this document.` : '';
    if (!window.confirm(`Delete Time Function entry ${index + 1}?${warning}`)) return;
    setEntries(entries.filter((_, itemIndex) => itemIndex !== index));
    if (selectedIndex === index) setSelectedIndex(undefined);
  };

  const confirmIdChange = (entry: unknown, nextEntry: unknown): boolean => {
    if (!isPlainRecord(entry) || !isPlainRecord(nextEntry) || entry.TIME_ID === nextEntry.TIME_ID) return true;
    const usage = usageFor(entry);
    return usage.length === 0 || window.confirm(`TIME_ID ${String(entry.TIME_ID)} is referenced ${usage.length} time${usage.length === 1 ? '' : 's'}. Change it without updating those references?`);
  };

  const visibleEntries = entries.map((entry, index) => {
    const inspected = inspectTimeFunctionEntry(entry);
    const entryIssues = issues.filter((issue) => issue.entryIndex === index);
    const status: Exclude<StatusFilter, 'ALL'> = entryIssues.some((issue) => issue.severity === 'error') ? 'ERROR'
      : entryIssues.some((issue) => issue.severity === 'warning') ? 'WARNING' : 'VALID';
    const option = inspected.kind === 'guided' ? String(inspected.option)
      : inspected.reason === 'unsupported' ? String(inspected.option) : 'RAW';
    return {entry, index, inspected, entryIssues, status, option};
  }).filter(({entry, inspected, option, status}) => {
    if (optionFilter === 'RAW' && inspected.kind !== 'raw') return false;
    if (optionFilter !== 'ALL' && optionFilter !== 'RAW' && option !== optionFilter) return false;
    if (statusFilter !== 'ALL' && statusFilter !== status) return false;
    return `${option} ${timeFunctionSummary(entry)} ${JSON.stringify(entry)}`.toLowerCase().includes(search.trim().toLowerCase());
  });

  const detail = selectedIndex === undefined ? undefined : (
    <TimeFunctionDetail
      key={selectedIndex}
      entry={entries[selectedIndex]}
      index={selectedIndex}
      issues={issues.filter((issue) => issue.entryIndex === selectedIndex)}
      usageCount={usageFor(entries[selectedIndex]).length}
      onBack={() => setSelectedIndex(undefined)}
      onChange={(entry) => { if (confirmIdChange(entries[selectedIndex], entry)) replaceEntry(selectedIndex, entry); }}
      onChangeOption={(option) => {
        const entry = entries[selectedIndex];
        if (!isPlainRecord(entry) || entry.OPTION === option) return;
        if (!window.confirm(`Change entry ${selectedIndex + 1} to OPTION ${option}? Known fields from the current guided mode will be replaced.`)) return;
        replaceEntry(selectedIndex, changeTimeFunctionOption(entry, option));
      }}
    />
  );

  const modal = (
    <div className={styles.networkModalBackdrop} onMouseDown={(event) => { if (event.target === event.currentTarget) requestClose(); }}>
      <div ref={dialogRef} className={`${styles.networkModal} ${styles.fieldSourceModal}`} role="dialog" aria-modal="true" aria-labelledby="time-function-editor-title">
        <header className={styles.networkModalHeader}>
          <div><h2 id="time-function-editor-title">Time Function editor</h2><div className={styles.networkModalSubtitle}>{documentName}</div></div>
          <div className={styles.networkHeaderActions}>
            <a href={TIME_FUNCTION_DOCUMENTATION} target="_blank" rel="noreferrer">Time Function documentation <EditorIcon name="external" /></a>
            <button ref={closeButtonRef} type="button" className={styles.networkIconButton} aria-label="Close Time Function editor" title="Close Time Function editor" onClick={requestClose}><EditorIcon name="close" /></button>
          </div>
        </header>
        <div className={`${styles.networkModalBody} ${styles.fieldSourceModalBody}`}>
          {detail ?? <>
            <div className={styles.networkToolbar}>
              <input aria-label="Search Time Functions" type="search" placeholder="Search time functions…" value={search} onChange={(event) => setSearch(event.target.value)} />
              <select aria-label="Filter Time Function option" value={optionFilter} onChange={(event) => setOptionFilter(event.target.value)}>
                <option value="ALL">All options</option>
                {SUPPORTED_TIME_FUNCTION_OPTIONS.map((option) => <option key={option} value={option}>OPTION {option} — {TIME_FUNCTION_SCHEMAS[option].label}</option>)}
                <option value="RAW">Raw / unsupported</option>
              </select>
              <select aria-label="Filter Time Function status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}>
                <option value="ALL">All statuses</option><option value="VALID">Valid</option><option value="WARNING">Warnings</option><option value="ERROR">Errors</option>
              </select>
              <div className={styles.networkAddGroup}><AddItemMenu label="Add time function" itemName="Time Function" options={ADD_OPTIONS} onSelect={addEntry} /></div>
            </div>
            <div className={styles.networkTableWrap}><table className={styles.networkTable}>
              <thead><tr><th>#</th><th>TIME_ID</th><th>Option</th><th>Summary</th><th>Uses</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>{visibleEntries.map(({entry, index, inspected, entryIssues}) => {
                const errors = entryIssues.filter((issue) => issue.severity === 'error').length;
                const warnings = entryIssues.filter((issue) => issue.severity === 'warning').length;
                const option = isPlainRecord(entry) ? entry.OPTION : undefined;
                const label = inspected.kind === 'guided' ? TIME_FUNCTION_SCHEMAS[inspected.option].label : 'Raw JSON';
                return <tr key={index}>
                  <td data-label="#">{index + 1}</td><td data-label="TIME_ID">{isPlainRecord(entry) && entry.TIME_ID !== undefined ? String(entry.TIME_ID) : '—'}</td>
                  <td data-label="Option"><strong>{option === undefined ? '—' : String(option)}</strong><small>{label}</small></td>
                  <td data-label="Summary">{timeFunctionSummary(entry)}</td><td data-label="Uses">{usageFor(entry).length}</td>
                  <td data-label="Status">{errors > 0 ? <span className={styles.networkErrorBadge}>{errors} error{errors === 1 ? '' : 's'}</span>
                    : warnings > 0 ? <span className={styles.networkWarningBadge}>{warnings} warning{warnings === 1 ? '' : 's'}</span>
                      : <span className={styles.networkValidBadge}>Valid</span>}</td>
                  <td data-label="Actions"><div className={styles.networkRowActions}>
                    <button type="button" aria-label={`Edit Time Function row ${index + 1}`} title="Edit time function" onClick={() => setSelectedIndex(index)}><EditorIcon name="edit" /></button>
                    <button type="button" aria-label={`Duplicate Time Function row ${index + 1}`} title="Duplicate time function" onClick={() => duplicateEntry(index)}><EditorIcon name="copy" /></button>
                    <button type="button" aria-label={`Move Time Function row ${index + 1} up`} title="Move up" disabled={index === 0} onClick={() => moveEntry(index, -1)}><EditorIcon name="up" /></button>
                    <button type="button" aria-label={`Move Time Function row ${index + 1} down`} title="Move down" disabled={index === entries.length - 1} onClick={() => moveEntry(index, 1)}><EditorIcon name="down" /></button>
                    <button type="button" className={styles.networkDangerButton} aria-label={`Delete Time Function row ${index + 1}`} title="Delete time function" onClick={() => deleteEntry(index)}><EditorIcon name="delete" /></button>
                  </div></td>
                </tr>;
              })}{visibleEntries.length === 0 && <tr><td colSpan={7} className={styles.networkEmpty}>No Time Functions match the current filters.</td></tr>}</tbody>
            </table></div>
            <ValidationIssues issues={issues.filter((issue) => issue.entryIndex === undefined)} />
          </>}
        </div>
        <footer className={styles.networkModalFooter}>
          <span>{entries.length} function{entries.length === 1 ? '' : 's'} · {errorCount} error{errorCount === 1 ? '' : 's'} · {warningCount} warning{warningCount === 1 ? '' : 's'}</span>
          <div><button type="button" className="button button--secondary" onClick={requestClose}><EditorIcon name="cancel" /> Cancel</button>
            <button type="button" className="button button--primary" disabled={errorCount > 0} title={errorCount > 0 ? 'Fix structural errors before applying' : 'Apply all Time Function changes to the open document'} onClick={() => { if (errorCount === 0) onApply(draftRoot); }}><EditorIcon name="apply" /> Apply changes</button></div>
        </footer>
      </div>
    </div>
  );
  return createPortal(modal, portalTarget ?? document.body);
}

function TimeFunctionDetail({entry, index, issues, usageCount, onBack, onChange, onChangeOption}: {
  entry: unknown;
  index: number;
  issues: TimeFunctionValidationIssue[];
  usageCount: number;
  onBack: () => void;
  onChange: (entry: unknown) => void;
  onChangeOption: (option: SupportedTimeFunctionOption) => void;
}): ReactNode {
  const inspected = inspectTimeFunctionEntry(entry);
  if (inspected.kind !== 'guided') return <div className={styles.fieldSourceDetail}>
    <DetailHeading index={index} title="Raw JSON" onBack={onBack} />
    <div className={styles.fieldSourceDescription}><div><strong>Unsupported Time Function</strong><p>This entire entry is preserved and edited as raw JSON. Guided controls and previews are intentionally unavailable.</p></div></div>
    <RawJsonEditor label="Raw Time Function entry JSON" value={entry} onSave={onChange} />
    <ValidationIssues issues={issues} />
  </div>;

  const schema = TIME_FUNCTION_SCHEMAS[inspected.option];
  const updateField = (key: string, nextValue: unknown) => onChange({...deepClone(inspected.value), [key]: nextValue});
  return <div className={styles.fieldSourceDetail}>
    <DetailHeading index={index} title={`OPTION ${inspected.option}`} onBack={onBack}>
      <label>Change option<select aria-label="Time Function option" value={inspected.option} onChange={(event) => onChangeOption(Number(event.target.value) as SupportedTimeFunctionOption)}>
        {SUPPORTED_TIME_FUNCTION_OPTIONS.map((option) => <option key={option} value={option}>{option} — {TIME_FUNCTION_SCHEMAS[option].label}</option>)}
      </select></label>
    </DetailHeading>
    <div className={styles.fieldSourceDescription}><div><strong>{schema.label}</strong><p>{schema.description}{usageCount > 0 ? ` This TIME_ID is used ${usageCount} time${usageCount === 1 ? '' : 's'} elsewhere.` : ''}</p></div>
      <a href={TIME_FUNCTION_DOCUMENTATION} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a></div>
    <div className={styles.fieldSourceFieldGrid}>
      <TimeFunctionField field={{key: 'TIME_ID', label: 'Time function ID', kind: 'integer', help: 'Identifier referenced by sources and circuits.'}} value={inspected.value.TIME_ID} onChange={(next) => updateField('TIME_ID', next)} />
      {schema.fields.map((field) => <TimeFunctionField key={field.key} field={field} value={inspected.value[field.key]} onChange={(next) => updateField(field.key, next)} />)}
    </div>
    {inspected.option === 1 && <TimeTableEditor entry={inspected.value} onChange={onChange} />}
    {inspected.option === 11 && <div className={styles.timeFunctionNotice}>Expressions are stored but never evaluated in the browser. See the <a href={TIME_FUNCTION_EXPRESSION_DOCUMENTATION} target="_blank" rel="noreferrer">mathematical-expression reference</a>.</div>}
    {[0, 1, 2].includes(inspected.option) && <TimeFunctionPreviewCard entry={inspected.value} option={inspected.option as 0 | 1 | 2} />}
    <ValidationIssues issues={issues} />
  </div>;
}

function DetailHeading({index, title, onBack, children}: {index: number; title: string; onBack: () => void; children?: ReactNode}): ReactNode {
  return <div className={styles.fieldSourceDetailHeading}><button type="button" className="button button--secondary button--sm" onClick={onBack}><EditorIcon name="up" /> Back to time functions</button><h3>Entry {index + 1} · {title}</h3>{children ?? <span />}</div>;
}

function TimeFunctionField({field, value, onChange}: {field: TimeFunctionFieldDefinition; value: unknown; onChange: (value: unknown) => void}): ReactNode {
  const label = `${field.label} (${field.key})`;
  if (field.multiline) return <label className={`${styles.networkField} ${styles.timeFunctionWideField}`}><span>{field.label}<em>{field.key}</em></span>
    <textarea aria-label={label} rows={5} value={typeof value === 'string' ? value : ''} onChange={(event) => onChange(event.target.value)} /><small>{field.help}</small></label>;
  return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span>
    <input aria-label={label} type={field.kind === 'string' ? 'text' : 'number'} step={field.kind === 'integer' ? '1' : 'any'} value={inputValue(value)} onChange={(event) => onChange(field.kind === 'string' ? event.target.value : numberValue(event.target.value))} />
    <small>{field.help}</small></label>;
}

function TimeTableEditor({entry, onChange}: {entry: Record<string, unknown>; onChange: (entry: unknown) => void}): ReactNode {
  const times = Array.isArray(entry.TIME) ? entry.TIME : [];
  const values = Array.isArray(entry.VALUE) ? entry.VALUE : [];
  const count = Math.max(times.length, values.length);
  const updateRows = (nextTimes: unknown[], nextValues: unknown[]) => onChange({...deepClone(entry), TIME: nextTimes, VALUE: nextValues});
  const move = (index: number, direction: -1 | 1) => {
    const target = index + direction;
    if (target < 0 || target >= count) return;
    const nextTimes = Array.from({length: count}, (_, itemIndex) => times[itemIndex] ?? '');
    const nextValues = Array.from({length: count}, (_, itemIndex) => values[itemIndex] ?? '');
    [nextTimes[index], nextTimes[target]] = [nextTimes[target], nextTimes[index]];
    [nextValues[index], nextValues[target]] = [nextValues[target], nextValues[index]];
    updateRows(nextTimes, nextValues);
  };
  return <section className={styles.fieldSourceRows}><div className={styles.fieldSourceRowsHeading}><div><h4>Time/value points</h4><p>Times must be non-decreasing. Equal consecutive times create a vertical step.</p></div>
    <button type="button" className="button button--secondary button--sm" onClick={() => updateRows([...times, times.at(-1) ?? 0], [...values, values.at(-1) ?? 0])}><EditorIcon name="add" /> Add point</button></div>
    <div className={styles.networkTableWrap}><table className={styles.networkTable}><thead><tr><th>#</th><th>Time (s)</th><th>Value</th><th>Actions</th></tr></thead><tbody>
      {Array.from({length: count}, (_, index) => <tr key={index}><td data-label="#">{index + 1}</td>
        <td data-label="Time (s)"><input className={styles.timeFunctionTableInput} aria-label={`Time point ${index + 1}`} type="number" step="any" value={inputValue(times[index])} onChange={(event) => { const next = [...times]; next[index] = numberValue(event.target.value); updateRows(next, Array.from({length: count}, (_, i) => values[i] ?? '')); }} /></td>
        <td data-label="Value"><input className={styles.timeFunctionTableInput} aria-label={`Value point ${index + 1}`} type="number" step="any" value={inputValue(values[index])} onChange={(event) => { const next = [...values]; next[index] = numberValue(event.target.value); updateRows(Array.from({length: count}, (_, i) => times[i] ?? ''), next); }} /></td>
        <td data-label="Actions"><div className={styles.networkRowActions}>
          <button type="button" aria-label={`Duplicate time point ${index + 1}`} onClick={() => { const nextTimes = [...times]; const nextValues = [...values]; nextTimes.splice(index + 1, 0, times[index]); nextValues.splice(index + 1, 0, values[index]); updateRows(nextTimes, nextValues); }}><EditorIcon name="copy" /></button>
          <button type="button" aria-label={`Move time point ${index + 1} up`} disabled={index === 0} onClick={() => move(index, -1)}><EditorIcon name="up" /></button>
          <button type="button" aria-label={`Move time point ${index + 1} down`} disabled={index === count - 1} onClick={() => move(index, 1)}><EditorIcon name="down" /></button>
          <button type="button" className={styles.networkDangerButton} aria-label={`Delete time point ${index + 1}`} onClick={() => updateRows(times.filter((_, i) => i !== index), values.filter((_, i) => i !== index))}><EditorIcon name="delete" /></button>
        </div></td></tr>)}
      {count === 0 && <tr><td colSpan={4} className={styles.networkEmpty}>No time/value points are defined.</td></tr>}
    </tbody></table></div>
  </section>;
}

function TimeFunctionPreviewCard({entry, option}: {entry: Record<string, unknown>; option: 0 | 1 | 2}): ReactNode {
  const initialDuration = defaultPreviewDuration(entry);
  const [duration, setDuration] = useState(initialDuration);
  useEffect(() => { setDuration(defaultPreviewDuration(entry)); }, [entry.OPTION]);
  const preview = useMemo(() => sampleTimeFunction(entry, option === 0 ? duration : undefined), [duration, entry, option]);
  return <section className={styles.timeFunctionPreview}><div className={styles.timeFunctionPreviewHeader}><div><h4>Preview</h4><p>Browser preview based on the documented equation; it is not an EMSolution simulation.</p></div>
    {option === 0 && <label>Preview end time (s)<input aria-label="Preview end time" type="number" min="0" step="any" value={inputValue(duration)} onChange={(event) => setDuration(Number(event.target.value))} /></label>}</div>
    {option === 0 && <AnalyticEquation />}{option === 2 && <AcEquation />}
    {preview.error ? <div className={styles.timeFunctionPreviewEmpty}>{preview.error}</div> : <TimeFunctionChart points={preview.points} duration={preview.duration} />}
  </section>;
}

function AnalyticEquation(): ReactNode {
  return <div className={styles.timeFunctionEquation} role="img" aria-label="f of t equals C0 plus C1 t plus exponential and sinusoidal terms C2 through C6">
    <i>f</i>(<i>t</i>) = C<sub>0</sub> + C<sub>1</sub><i>t</i> + C<sub>2</sub>e<sup>−t/TEXP</sup> + C<sub>3</sub>sin(2πt/TCYCLE) + C<sub>4</sub>cos(2πt/TCYCLE + PHASE4·π/180) + C<sub>5</sub>e<sup>−t/TEXP</sup>sin(2πt/TCYCLE) + C<sub>6</sub>e<sup>−t/TEXP</sup>cos(2πt/TCYCLE)
  </div>;
}

function AcEquation(): ReactNode {
  return <div className={styles.timeFunctionEquation} role="img" aria-label="f of t equals amplitude times cosine of two pi t over T cycle plus phase times pi over 180">
    <i>f</i>(<i>t</i>) = AMPLITUDE · cos(2π<i>t</i>/TCYCLE + PHASE·π/180)
  </div>;
}

function TimeFunctionChart({points, duration}: {points: Array<{time: number; value: number}>; duration: number}): ReactNode {
  const width = 720; const height = 240; const left = 58; const right = 18; const top = 16; const bottom = 38;
  const xMin = Math.min(0, ...points.map((point) => point.time));
  const xMaxCandidate = Math.max(duration, ...points.map((point) => point.time));
  const xMax = xMaxCandidate === xMin ? xMin + 1 : xMaxCandidate;
  const rawMin = Math.min(...points.map((point) => point.value)); const rawMax = Math.max(...points.map((point) => point.value));
  const yPad = rawMax === rawMin ? Math.max(Math.abs(rawMax) * 0.1, 1) : (rawMax - rawMin) * 0.08;
  const yMin = rawMin - yPad; const yMax = rawMax + yPad;
  const x = (value: number) => left + (value - xMin) / (xMax - xMin) * (width - left - right);
  const y = (value: number) => top + (yMax - value) / (yMax - yMin) * (height - top - bottom);
  const path = points.map((point, index) => `${index === 0 ? 'M' : 'L'}${x(point.time).toFixed(2)},${y(point.value).toFixed(2)}`).join(' ');
  const label = `Time-function preview from ${xMin.toPrecision(3)} to ${xMax.toPrecision(3)} seconds, values ${rawMin.toPrecision(3)} to ${rawMax.toPrecision(3)}.`;
  return <figure className={styles.timeFunctionChart}><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
    <line className={styles.timeFunctionGrid} x1={left} y1={top} x2={left} y2={height - bottom} /><line className={styles.timeFunctionGrid} x1={left} y1={height - bottom} x2={width - right} y2={height - bottom} />
    {yMin <= 0 && yMax >= 0 && <line className={styles.timeFunctionZero} x1={left} y1={y(0)} x2={width - right} y2={y(0)} />}
    <path className={styles.timeFunctionLine} d={path} />
    <text x={left} y={height - 14}>{xMin.toPrecision(3)} s</text><text textAnchor="end" x={width - right} y={height - 14}>{xMax.toPrecision(3)} s</text>
    <text x={8} y={top + 5}>{rawMax.toPrecision(3)}</text><text x={8} y={height - bottom}>{rawMin.toPrecision(3)}</text>
  </svg><figcaption>{label}</figcaption></figure>;
}

function RawJsonEditor({label, value, onSave}: {label: string; value: unknown; onSave: (value: unknown) => void}): ReactNode {
  const [text, setText] = useState(JSON.stringify(value, null, 2));
  const [error, setError] = useState('');
  return <div className={styles.fieldSourceRawEditor}><textarea aria-label={label} rows={18} value={text} onChange={(event) => { setText(event.target.value); setError(''); }} />
    {error && <div className={styles.networkInlineError}>{error}</div>}<div className={styles.networkEditorButtons}><button type="button" className="button button--primary button--sm" onClick={() => {
      try { const parsed = JSON.parse(text); if (!isPlainRecord(parsed)) { setError('Value must be a JSON object.'); return; } onSave(parsed); }
      catch (caught) { setError(caught instanceof Error ? caught.message : 'Invalid JSON.'); }
    }}><EditorIcon name="save" /> Save raw JSON</button></div></div>;
}

function ValidationIssues({issues}: {issues: TimeFunctionValidationIssue[]}): ReactNode {
  if (issues.length === 0) return null;
  return <section className={styles.networkIssues} aria-label="Time Function validation issues"><h3>Validation</h3><ul>{issues.map((issue, index) => <li key={`${issue.path}:${index}`} className={issue.severity === 'error' ? styles.networkIssueError : styles.networkIssueWarning}><strong>{issue.path}</strong>: {issue.message}</li>)}</ul></section>;
}
