import React, {type ReactNode, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

import AddItemMenu from './AddItemMenu';
import {
  BH_CURVE_DOCUMENTATION,
  bhCurvePreviewPoints,
  bhCurveSummary,
  collectBhCurveConsumers,
  createBhCurve,
  createEncryptedBhCurve,
  deepClone,
  duplicateBhCurve,
  findBhCurves,
  inspectBhCurveEntry,
  isPlainRecord,
  replaceBhCurves,
  validateBhCurves,
  type BhCurveValidationIssue,
} from './bhCurveModel';
import EditorIcon from './EditorIcon';
import styles from './styles.module.css';

interface BhCurveEditorModalProps {
  documentName: string;
  value: unknown;
  portalTarget?: Element;
  onApply: (value: unknown) => void;
  onClose: () => void;
}

type AddChoice = 'table' | 'encrypted';
type StatusFilter = 'ALL' | 'VALID' | 'WARNING' | 'ERROR';
type TypeFilter = 'ALL' | 'TABLE' | 'RAW';

const ADD_OPTIONS: Array<{value: AddChoice; label: string; description: string}> = [
  {value: 'table', label: 'B-H table', description: 'Create paired magnetic field strength H and flux density B arrays.'},
  {value: 'encrypted', label: 'Encrypted / raw JSON', description: 'Create an encrypted_data entry and edit the complete object as JSON.'},
];

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function numberValue(raw: string): number | string {
  return raw.trim() === '' ? '' : Number(raw);
}

export default function BhCurveEditorModal({
  documentName,
  value,
  portalTarget,
  onApply,
  onClose,
}: BhCurveEditorModalProps): ReactNode {
  const initialRootRef = useRef(replaceBhCurves(value, findBhCurves(value)));
  const initialJsonRef = useRef(JSON.stringify(initialRootRef.current));
  const [draftRoot, setDraftRoot] = useState(initialRootRef.current);
  const [selectedIndex, setSelectedIndex] = useState<number>();
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('ALL');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const draftRootRef = useRef(draftRoot);
  const restoreFocusRef = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement ? document.activeElement : null,
  );
  const entries = findBhCurves(draftRoot);
  const issues = useMemo(() => validateBhCurves(draftRoot), [draftRoot]);
  const consumers = useMemo(() => collectBhCurveConsumers(draftRoot), [draftRoot]);
  const errorCount = issues.filter((issue) => issue.severity === 'error').length;
  const warningCount = issues.filter((issue) => issue.severity === 'warning').length;

  useEffect(() => { draftRootRef.current = draftRoot; }, [draftRoot]);

  const requestClose = useCallback(() => {
    if (JSON.stringify(draftRootRef.current) !== initialJsonRef.current
      && !window.confirm('Discard the unsaved B-H Curve changes?')) return;
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
    else dialogRef.current?.querySelector<HTMLElement>('button:not(:disabled), input:not(:disabled), textarea:not(:disabled)')?.focus();
  }, [selectedIndex]);

  const setEntries = (nextEntries: unknown[]) => setDraftRoot((current) => replaceBhCurves(current, nextEntries));
  const replaceEntry = (index: number, entry: unknown) => {
    const next = [...entries];
    next[index] = entry;
    setEntries(next);
  };
  const usageFor = (entry: unknown) => {
    const id = isPlainRecord(entry) && Number.isInteger(entry.BH_CURVE_ID) ? entry.BH_CURVE_ID as number : undefined;
    return id === undefined ? [] : consumers.filter((consumer) => consumer.curveId === id);
  };
  const confirmIdChange = (entry: unknown, nextEntry: unknown): boolean => {
    if (!isPlainRecord(entry) || !isPlainRecord(nextEntry) || entry.BH_CURVE_ID === nextEntry.BH_CURVE_ID) return true;
    const usage = usageFor(entry);
    return usage.length === 0 || window.confirm(`BH_CURVE_ID ${String(entry.BH_CURVE_ID)} is referenced ${usage.length} time${usage.length === 1 ? '' : 's'}. Change it without updating those references?`);
  };
  const addEntry = (choice: AddChoice) => {
    const entry = choice === 'encrypted' ? createEncryptedBhCurve(entries) : createBhCurve(entries);
    const next = [...entries, entry];
    setEntries(next);
    setSelectedIndex(next.length - 1);
  };
  const duplicateEntry = (index: number) => {
    const next = [...entries];
    next.splice(index + 1, 0, duplicateBhCurve(entries[index], entries));
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
    const usage = usageFor(entries[index]);
    const warning = usage.length > 0 ? ` It is referenced ${usage.length} time${usage.length === 1 ? '' : 's'} elsewhere in this document.` : '';
    if (!window.confirm(`Delete B-H Curve entry ${index + 1}?${warning}`)) return;
    setEntries(entries.filter((_, itemIndex) => itemIndex !== index));
    if (selectedIndex === index) setSelectedIndex(undefined);
  };

  const visibleEntries = entries.map((entry, index) => {
    const inspected = inspectBhCurveEntry(entry);
    const entryIssues = issues.filter((issue) => issue.entryIndex === index);
    const status: Exclude<StatusFilter, 'ALL'> = entryIssues.some((issue) => issue.severity === 'error') ? 'ERROR'
      : entryIssues.some((issue) => issue.severity === 'warning') ? 'WARNING' : 'VALID';
    const kind: Exclude<TypeFilter, 'ALL'> = inspected.kind === 'guided' ? 'TABLE' : 'RAW';
    return {entry, index, inspected, entryIssues, status, kind};
  }).filter(({entry, status, kind}) => {
    if (typeFilter !== 'ALL' && typeFilter !== kind) return false;
    if (statusFilter !== 'ALL' && statusFilter !== status) return false;
    return `${kind} ${bhCurveSummary(entry)} ${JSON.stringify(entry)}`.toLowerCase().includes(search.trim().toLowerCase());
  });

  const detail = selectedIndex === undefined ? undefined : (
    <BhCurveDetail
      key={selectedIndex}
      entry={entries[selectedIndex]}
      index={selectedIndex}
      issues={issues.filter((issue) => issue.entryIndex === selectedIndex)}
      usageCount={usageFor(entries[selectedIndex]).length}
      onBack={() => setSelectedIndex(undefined)}
      onChange={(entry) => { if (confirmIdChange(entries[selectedIndex], entry)) replaceEntry(selectedIndex, entry); }}
    />
  );

  const modal = (
    <div className={styles.networkModalBackdrop} onMouseDown={(event) => { if (event.target === event.currentTarget) requestClose(); }}>
      <div ref={dialogRef} className={`${styles.networkModal} ${styles.fieldSourceModal}`} role="dialog" aria-modal="true" aria-labelledby="bh-curve-editor-title">
        <header className={styles.networkModalHeader}>
          <div><h2 id="bh-curve-editor-title">B-H Curve editor</h2><div className={styles.networkModalSubtitle}>{documentName}</div></div>
          <div className={styles.networkHeaderActions}>
            <a href={BH_CURVE_DOCUMENTATION} target="_blank" rel="noreferrer">B-H Curve documentation <EditorIcon name="external" /></a>
            <button ref={closeButtonRef} type="button" className={styles.networkIconButton} aria-label="Close B-H Curve editor" title="Close B-H Curve editor" onClick={requestClose}><EditorIcon name="close" /></button>
          </div>
        </header>
        <div className={`${styles.networkModalBody} ${styles.fieldSourceModalBody}`}>
          {detail ?? <>
            <div className={styles.networkToolbar}>
              <input aria-label="Search B-H Curves" type="search" placeholder="Search B-H curves…" value={search} onChange={(event) => setSearch(event.target.value)} />
              <select aria-label="Filter B-H Curve type" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value as TypeFilter)}>
                <option value="ALL">All types</option><option value="TABLE">Table</option><option value="RAW">Encrypted / raw</option>
              </select>
              <select aria-label="Filter B-H Curve status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}>
                <option value="ALL">All statuses</option><option value="VALID">Valid</option><option value="WARNING">Warnings</option><option value="ERROR">Errors</option>
              </select>
              <div className={styles.networkAddGroup}><AddItemMenu label="Add B-H curve" itemName="B-H Curve" options={ADD_OPTIONS} onSelect={addEntry} /></div>
            </div>
            <div className={styles.networkTableWrap}><table className={styles.networkTable}>
              <thead><tr><th>#</th><th>BH_CURVE_ID</th><th>Type</th><th>Summary</th><th>Uses</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>{visibleEntries.map(({entry, index, inspected, entryIssues}) => {
                const errors = entryIssues.filter((issue) => issue.severity === 'error').length;
                const warnings = entryIssues.filter((issue) => issue.severity === 'warning').length;
                const label = inspected.kind === 'guided' ? 'H/B table'
                  : inspected.reason === 'encrypted' ? 'Encrypted / raw JSON' : 'Raw JSON';
                return <tr key={index}>
                  <td data-label="#">{index + 1}</td>
                  <td data-label="BH_CURVE_ID">{isPlainRecord(entry) && entry.BH_CURVE_ID !== undefined ? String(entry.BH_CURVE_ID) : '—'}</td>
                  <td data-label="Type"><strong>{label}</strong></td>
                  <td data-label="Summary">{bhCurveSummary(entry)}</td><td data-label="Uses">{usageFor(entry).length}</td>
                  <td data-label="Status">{errors > 0 ? <span className={styles.networkErrorBadge}>{errors} error{errors === 1 ? '' : 's'}</span>
                    : warnings > 0 ? <span className={styles.networkWarningBadge}>{warnings} warning{warnings === 1 ? '' : 's'}</span>
                      : <span className={styles.networkValidBadge}>Valid</span>}</td>
                  <td data-label="Actions"><div className={styles.networkRowActions}>
                    <button type="button" aria-label={`Edit B-H Curve row ${index + 1}`} title="Edit B-H curve" onClick={() => setSelectedIndex(index)}><EditorIcon name="edit" /></button>
                    <button type="button" aria-label={`Duplicate B-H Curve row ${index + 1}`} title="Duplicate B-H curve" onClick={() => duplicateEntry(index)}><EditorIcon name="copy" /></button>
                    <button type="button" aria-label={`Move B-H Curve row ${index + 1} up`} title="Move up" disabled={index === 0} onClick={() => moveEntry(index, -1)}><EditorIcon name="up" /></button>
                    <button type="button" aria-label={`Move B-H Curve row ${index + 1} down`} title="Move down" disabled={index === entries.length - 1} onClick={() => moveEntry(index, 1)}><EditorIcon name="down" /></button>
                    <button type="button" className={styles.networkDangerButton} aria-label={`Delete B-H Curve row ${index + 1}`} title="Delete B-H curve" onClick={() => deleteEntry(index)}><EditorIcon name="delete" /></button>
                  </div></td>
                </tr>;
              })}{visibleEntries.length === 0 && <tr><td colSpan={7} className={styles.networkEmpty}>No B-H Curves match the current filters.</td></tr>}</tbody>
            </table></div>
            <ValidationIssues issues={issues.filter((issue) => issue.entryIndex === undefined)} />
          </>}
        </div>
        <footer className={styles.networkModalFooter}>
          <span>{entries.length} curve{entries.length === 1 ? '' : 's'} · {errorCount} error{errorCount === 1 ? '' : 's'} · {warningCount} warning{warningCount === 1 ? '' : 's'}</span>
          <div><button type="button" className="button button--secondary" onClick={requestClose}><EditorIcon name="cancel" /> Cancel</button>
            <button type="button" className="button button--primary" disabled={errorCount > 0} title={errorCount > 0 ? 'Fix structural errors before applying' : 'Apply all B-H Curve changes to the open document'} onClick={() => { if (errorCount === 0) onApply(draftRoot); }}><EditorIcon name="apply" /> Apply changes</button></div>
        </footer>
      </div>
    </div>
  );
  return createPortal(modal, portalTarget ?? document.body);
}

function BhCurveDetail({entry, index, issues, usageCount, onBack, onChange}: {
  entry: unknown;
  index: number;
  issues: BhCurveValidationIssue[];
  usageCount: number;
  onBack: () => void;
  onChange: (entry: unknown) => void;
}): ReactNode {
  const inspected = inspectBhCurveEntry(entry);
  if (inspected.kind !== 'guided') return <div className={styles.fieldSourceDetail}>
    <DetailHeading index={index} title="Encrypted / raw JSON" onBack={onBack} />
    <div className={styles.fieldSourceDescription}><div><strong>Whole-entry JSON editor</strong><p>Encrypted and unsupported B-H curves are preserved without partial normalization. Repair malformed entries here or update encrypted_data directly.</p></div>
      <a href={BH_CURVE_DOCUMENTATION} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a></div>
    <RawJsonEditor label="Raw B-H Curve entry JSON" value={entry} onSave={onChange} />
    <ValidationIssues issues={issues} />
  </div>;

  const value = inspected.value;
  const data = value.data as Record<string, unknown>;
  const hValues = data.H as unknown[];
  const bValues = data.B as unknown[];
  const updateRows = (nextH: unknown[], nextB: unknown[]) => onChange({
    ...deepClone(value),
    data: {...deepClone(data), H: nextH, B: nextB},
  });
  const count = Math.max(hValues.length, bValues.length);
  const move = (rowIndex: number, direction: -1 | 1) => {
    const target = rowIndex + direction;
    if (target < 0 || target >= count) return;
    const nextH = Array.from({length: count}, (_, itemIndex) => hValues[itemIndex] ?? '');
    const nextB = Array.from({length: count}, (_, itemIndex) => bValues[itemIndex] ?? '');
    [nextH[rowIndex], nextH[target]] = [nextH[target], nextH[rowIndex]];
    [nextB[rowIndex], nextB[target]] = [nextB[target], nextB[rowIndex]];
    updateRows(nextH, nextB);
  };
  return <div className={styles.fieldSourceDetail}>
    <DetailHeading index={index} title="H/B table" onBack={onBack} />
    <div className={styles.fieldSourceDescription}><div><strong>Isotropic B-H curve</strong><p>Edit magnetic field strength and flux density as paired points.{usageCount > 0 ? ` This curve ID is used ${usageCount} time${usageCount === 1 ? '' : 's'} elsewhere.` : ''}</p></div>
      <a href={BH_CURVE_DOCUMENTATION} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a></div>
    <div className={styles.fieldSourceFieldGrid}>
      <label className={styles.networkField}><span>B-H curve ID<em>BH_CURVE_ID</em></span>
        <input aria-label="B-H curve ID (BH_CURVE_ID)" type="number" step="1" value={inputValue(value.BH_CURVE_ID)} onChange={(event) => onChange({...deepClone(value), BH_CURVE_ID: numberValue(event.target.value)})} />
        <small>Positive identifier referenced by magnetic material properties.</small></label>
    </div>
    <section className={styles.fieldSourceRows}><div className={styles.fieldSourceRowsHeading}><div><h4>H/B points</h4><p>Start at H=0, B=0. EMSolution linearly interpolates and extrapolates the table; the documented high-field slope should approach vacuum permeability.</p></div>
      <button type="button" className="button button--secondary button--sm" onClick={() => updateRows([...hValues, hValues.at(-1) ?? 0], [...bValues, bValues.at(-1) ?? 0])}><EditorIcon name="add" /> Add point</button></div>
      <div className={styles.networkTableWrap}><table className={styles.networkTable}><thead><tr><th>#</th><th>H (A/m)</th><th>B (T)</th><th>Actions</th></tr></thead><tbody>
        {Array.from({length: count}, (_, rowIndex) => <tr key={rowIndex}><td data-label="#">{rowIndex + 1}</td>
          <td data-label="H (A/m)"><input className={styles.timeFunctionTableInput} aria-label={`H point ${rowIndex + 1}`} type="number" step="any" value={inputValue(hValues[rowIndex])} onChange={(event) => { const next = [...hValues]; next[rowIndex] = numberValue(event.target.value); updateRows(next, Array.from({length: count}, (_, i) => bValues[i] ?? '')); }} /></td>
          <td data-label="B (T)"><input className={styles.timeFunctionTableInput} aria-label={`B point ${rowIndex + 1}`} type="number" step="any" value={inputValue(bValues[rowIndex])} onChange={(event) => { const next = [...bValues]; next[rowIndex] = numberValue(event.target.value); updateRows(Array.from({length: count}, (_, i) => hValues[i] ?? ''), next); }} /></td>
          <td data-label="Actions"><div className={styles.networkRowActions}>
            <button type="button" aria-label={`Duplicate B-H point ${rowIndex + 1}`} onClick={() => { const nextH = [...hValues]; const nextB = [...bValues]; nextH.splice(rowIndex + 1, 0, hValues[rowIndex]); nextB.splice(rowIndex + 1, 0, bValues[rowIndex]); updateRows(nextH, nextB); }}><EditorIcon name="copy" /></button>
            <button type="button" aria-label={`Move B-H point ${rowIndex + 1} up`} disabled={rowIndex === 0} onClick={() => move(rowIndex, -1)}><EditorIcon name="up" /></button>
            <button type="button" aria-label={`Move B-H point ${rowIndex + 1} down`} disabled={rowIndex === count - 1} onClick={() => move(rowIndex, 1)}><EditorIcon name="down" /></button>
            <button type="button" className={styles.networkDangerButton} aria-label={`Delete B-H point ${rowIndex + 1}`} onClick={() => updateRows(hValues.filter((_, i) => i !== rowIndex), bValues.filter((_, i) => i !== rowIndex))}><EditorIcon name="delete" /></button>
          </div></td></tr>)}
        {count === 0 && <tr><td colSpan={4} className={styles.networkEmpty}>No H/B points are defined.</td></tr>}
      </tbody></table></div>
    </section>
    <BhCurvePreview entry={value} />
    <ValidationIssues issues={issues} />
  </div>;
}

function DetailHeading({index, title, onBack}: {index: number; title: string; onBack: () => void}): ReactNode {
  return <div className={styles.fieldSourceDetailHeading}><button type="button" className="button button--secondary button--sm" onClick={onBack}><EditorIcon name="up" /> Back to B-H curves</button><h3>Entry {index + 1} · {title}</h3><span /></div>;
}

function BhCurvePreview({entry}: {entry: unknown}): ReactNode {
  const points = bhCurvePreviewPoints(entry);
  return <section className={styles.timeFunctionPreview}>
    <div className={styles.timeFunctionPreviewHeader}><div><h4>B-H curve preview</h4><p>Browser visualization of the entered points; it is not an EMSolution simulation.</p></div></div>
    {points.length < 2 ? <div className={styles.timeFunctionPreviewEmpty}>A complete table with at least two finite H/B pairs is required for the preview.</div> : <BhCurveChart points={points} />}
  </section>;
}

function BhCurveChart({points}: {points: Array<{h: number; b: number}>}): ReactNode {
  const width = 720; const height = 260; const left = 72; const right = 20; const top = 18; const bottom = 48;
  const rawHMin = Math.min(...points.map((point) => point.h)); const rawHMax = Math.max(...points.map((point) => point.h));
  const rawBMin = Math.min(...points.map((point) => point.b)); const rawBMax = Math.max(...points.map((point) => point.b));
  const hPad = rawHMax === rawHMin ? Math.max(Math.abs(rawHMax) * 0.1, 1) : 0;
  const bPad = rawBMax === rawBMin ? Math.max(Math.abs(rawBMax) * 0.1, 1) : (rawBMax - rawBMin) * 0.05;
  const hMin = rawHMin - hPad; const hMax = rawHMax + hPad;
  const bMin = rawBMin - bPad; const bMax = rawBMax + bPad;
  const x = (value: number) => left + (value - hMin) / (hMax - hMin) * (width - left - right);
  const y = (value: number) => top + (bMax - value) / (bMax - bMin) * (height - top - bottom);
  const path = points.map((point, index) => `${index === 0 ? 'M' : 'L'}${x(point.h).toFixed(2)},${y(point.b).toFixed(2)}`).join(' ');
  const label = `B-H curve preview with ${points.length} points, H ${rawHMin.toPrecision(3)} to ${rawHMax.toPrecision(3)} amperes per metre and B ${rawBMin.toPrecision(3)} to ${rawBMax.toPrecision(3)} tesla.`;
  return <figure className={styles.timeFunctionChart}><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
    <line className={styles.timeFunctionGrid} x1={left} y1={top} x2={left} y2={height - bottom} /><line className={styles.timeFunctionGrid} x1={left} y1={height - bottom} x2={width - right} y2={height - bottom} />
    {bMin <= 0 && bMax >= 0 && <line className={styles.timeFunctionZero} x1={left} y1={y(0)} x2={width - right} y2={y(0)} />}
    <path className={styles.timeFunctionLine} d={path} />
    {points.map((point, index) => <circle key={index} className={styles.bhCurvePoint} cx={x(point.h)} cy={y(point.b)} r="3" />)}
    <text x={left} y={height - 23}>{rawHMin.toPrecision(3)}</text><text textAnchor="end" x={width - right} y={height - 23}>{rawHMax.toPrecision(3)}</text>
    <text textAnchor="middle" x={(left + width - right) / 2} y={height - 7}>H (A/m)</text>
    <text x={8} y={top + 5}>{rawBMax.toPrecision(3)}</text><text x={8} y={height - bottom}>{rawBMin.toPrecision(3)}</text>
    <text transform={`translate(17 ${(top + height - bottom) / 2}) rotate(-90)`} textAnchor="middle">B (T)</text>
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

function ValidationIssues({issues}: {issues: BhCurveValidationIssue[]}): ReactNode {
  if (issues.length === 0) return null;
  return <section className={styles.networkIssues} aria-label="B-H Curve validation issues"><h3>Validation</h3><ul>{issues.map((issue, index) => <li key={`${issue.path}:${index}`} className={issue.severity === 'error' ? styles.networkIssueError : styles.networkIssueWarning}><strong>{issue.path}</strong>: {issue.message}</li>)}</ul></section>;
}
