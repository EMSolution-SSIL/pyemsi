import React, {type ReactNode, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

import {
  type CircuitDefinition,
  type CircuitPowerSupply,
  type CircuitSection,
  findCircuitSections,
  isCircuitDefinition,
  nextPowerSupplyId,
  normalizeCircuit,
  readConnectionMatrix,
  readSymmetricMatrix,
  remapCircuitPowerSupplies,
  remapCircuitSeries,
  replaceCircuitSections,
  setCircuitMatrixMode,
  updateConnectionMatrixCell,
  updateSymmetricMatrixCell,
  validateCircuit,
} from './circuitModel';
import EditorIcon from './EditorIcon';
import {collectEmSolutionReferences, deepClone, isPlainRecord} from './emSolutionModel';
import TimeFunctionReferencePicker from './TimeFunctionReferencePicker';
import {createTimeFunctionReferenceCatalog} from './timeFunctionModel';
import styles from './styles.module.css';

const DOCUMENTATION_URL = 'https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/17_8_CIRCUIT.html';

interface CircuitEditorModalProps {
  documentName: string;
  value: unknown;
  portalTarget?: Element;
  embedded?: boolean;
  initialSection?: number;
  onApply: (value: unknown) => void;
  onClose: () => void;
}

function sectionCopies(value: unknown): Array<CircuitSection & {circuit: CircuitDefinition}> {
  return findCircuitSections(value).flatMap((section) => (
    isCircuitDefinition(section.circuit)
      ? [{...section, circuit: deepClone(section.circuit)}]
      : []
  ));
}

function numberValue(raw: string): number | string {
  return raw.trim() === '' ? '' : Number(raw);
}

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function indexed(count: number): number[] {
  return Array.from({length: count}, (_, index) => index);
}

function moveIndex(count: number, index: number, direction: -1 | 1): number[] {
  const indices = indexed(count);
  const target = index + direction;
  if (target >= 0 && target < count) [indices[index], indices[target]] = [indices[target], indices[index]];
  return indices;
}

function matrixRecord(value: unknown): Record<string, unknown> {
  return isPlainRecord(value) ? value : {};
}

function supplyRecord(value: unknown): CircuitPowerSupply {
  return isPlainRecord(value) ? value : {};
}

export default function CircuitEditorModal({
  documentName,
  value,
  portalTarget,
  embedded = false,
  initialSection = 0,
  onApply,
  onClose,
}: CircuitEditorModalProps): ReactNode {
  const initialSectionsRef = useRef(sectionCopies(value));
  const initialJsonRef = useRef(JSON.stringify(initialSectionsRef.current));
  const [sections, setSections] = useState(initialSectionsRef.current);
  const [selectedSection, setSelectedSection] = useState(() => Math.max(0, Math.min(initialSection, initialSectionsRef.current.length - 1)));
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const sectionsRef = useRef(sections);
  const restoreFocusRef = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement ? document.activeElement : null,
  );
  const references = useMemo(() => collectEmSolutionReferences(value), [value]);
  const timeFunctionCatalog = useMemo(() => createTimeFunctionReferenceCatalog(value), [value]);
  const section = sections[selectedSection];
  const circuit = section?.circuit;
  const series = circuit && Array.isArray(circuit.SERIES_IDS) ? circuit.SERIES_IDS : [];
  const supplies = circuit && Array.isArray(circuit.POWER_SUPPLIES) ? circuit.POWER_SUPPLIES : [];

  useEffect(() => {
    sectionsRef.current = sections;
  }, [sections]);

  const updateCircuit = useCallback((update: (current: CircuitDefinition) => CircuitDefinition) => {
    setSections((current) => current.map((item, index) => (
      index === selectedSection ? {...item, circuit: update(item.circuit)} : item
    )));
  }, [selectedSection]);

  const requestClose = useCallback(() => {
    const dirty = JSON.stringify(sectionsRef.current) !== initialJsonRef.current;
    if (dirty && !window.confirm('Discard the unsaved CIRCUIT modal changes?')) return;
    onClose();
  }, [onClose]);

  useEffect(() => {
    if (embedded) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeButtonRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (dialogRef.current?.querySelector(`.${styles.timeFunctionReferencePicker}`)) return;
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
  }, [embedded, requestClose]);

  useEffect(() => {
    if (!embedded) return undefined;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      if (dialogRef.current?.querySelector(`.${styles.timeFunctionReferencePicker}`)) return;
      event.preventDefault();
      requestClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [embedded, requestClose]);

  const allIssues = useMemo(() => sections.flatMap((item, index) => (
    validateCircuit(item.circuit, value).map((issue) => ({...issue, sectionIndex: index}))
  )), [sections, value]);
  const issues = allIssues.filter((issue) => issue.sectionIndex === selectedSection);
  const errorCount = allIssues.filter((issue) => issue.severity === 'error').length;
  const warningCount = allIssues.filter((issue) => issue.severity === 'warning').length;

  const updateSeriesValue = (index: number, raw: string) => {
    updateCircuit((current) => ({
      ...current,
      SERIES_IDS: series.map((entry, itemIndex) => itemIndex === index ? numberValue(raw) : entry),
    }));
  };

  const addSeries = () => updateCircuit((current) => remapCircuitSeries(
    current,
    [...series, ''],
    [...indexed(series.length), undefined],
  ));

  const duplicateSeries = (index: number) => updateCircuit((current) => {
    const nextIds = [...series];
    nextIds.splice(index + 1, 0, deepClone(series[index]));
    const indices: Array<number | undefined> = indexed(series.length);
    indices.splice(index + 1, 0, index);
    return remapCircuitSeries(current, nextIds, indices);
  });

  const deleteSeries = (index: number) => {
    if (!window.confirm(`Delete series row ${index + 1} and its matrix values?`)) return;
    updateCircuit((current) => remapCircuitSeries(
      current,
      series.filter((_, itemIndex) => itemIndex !== index),
      indexed(series.length).filter((itemIndex) => itemIndex !== index),
    ));
  };

  const moveSeries = (index: number, direction: -1 | 1) => updateCircuit((current) => {
    const indices = moveIndex(series.length, index, direction);
    return remapCircuitSeries(current, indices.map((source) => series[source]), indices);
  });

  const updateSupply = (index: number, key: keyof CircuitPowerSupply, raw: string | number) => {
    updateCircuit((current) => ({
      ...current,
      POWER_SUPPLIES: supplies.map((entry, itemIndex) => (
        itemIndex === index ? {...supplyRecord(entry), [key]: typeof raw === 'number' ? raw : numberValue(raw)} : entry
      )),
    }));
  };

  const addSupply = () => updateCircuit((current) => remapCircuitPowerSupplies(
    current,
    [...supplies, {PS_ID: nextPowerSupplyId(supplies), TYPE: '', TIME_ID: '', INITIAL_CURRENT: ''}],
    [...indexed(supplies.length), undefined],
  ));

  const duplicateSupply = (index: number) => updateCircuit((current) => {
    const duplicate = {...deepClone(supplyRecord(supplies[index])), PS_ID: nextPowerSupplyId(supplies)};
    const nextSupplies = [...supplies];
    nextSupplies.splice(index + 1, 0, duplicate);
    const indices: Array<number | undefined> = indexed(supplies.length);
    indices.splice(index + 1, 0, index);
    return remapCircuitPowerSupplies(current, nextSupplies, indices);
  });

  const deleteSupply = (index: number) => {
    if (!window.confirm(`Delete power supply row ${index + 1} and its connection values?`)) return;
    updateCircuit((current) => remapCircuitPowerSupplies(
      current,
      supplies.filter((_, itemIndex) => itemIndex !== index),
      indexed(supplies.length).filter((itemIndex) => itemIndex !== index),
    ));
  };

  const moveSupply = (index: number, direction: -1 | 1) => updateCircuit((current) => {
    const indices = moveIndex(supplies.length, index, direction);
    return remapCircuitPowerSupplies(current, indices.map((source) => supplies[source]), indices);
  });

  const apply = () => {
    if (errorCount > 0) return;
    const normalized = sections.map((item) => ({...item, circuit: normalizeCircuit(item.circuit)}));
    onApply(replaceCircuitSections(value, normalized));
  };

  const editor = (
      <div
        ref={dialogRef}
        className={embedded ? styles.fieldSourceEmbeddedSpecial : styles.networkModal}
        role={embedded ? 'region' : 'dialog'}
        aria-modal={embedded ? undefined : true}
        aria-label={embedded ? 'CIRCUIT editor' : undefined}
        aria-labelledby={embedded ? undefined : 'circuit-editor-title'}>
        <header className={styles.networkModalHeader}>
          <div>
            <h2 id="circuit-editor-title">CIRCUIT editor</h2>
            <div className={styles.networkModalSubtitle}>{documentName}</div>
          </div>
          <div className={styles.networkHeaderActions}>
            <a href={DOCUMENTATION_URL} target="_blank" rel="noreferrer">
              Official documentation <EditorIcon name="external" />
            </a>
            <button ref={closeButtonRef} type="button" className={styles.networkIconButton} aria-label="Close CIRCUIT editor" title="Close CIRCUIT editor" onClick={requestClose}>
              <EditorIcon name="close" />
            </button>
          </div>
        </header>

        <div className={styles.networkModalBody}>
          <section className={styles.networkSettings} aria-label="CIRCUIT settings">
            {sections.length > 1 && (
              <label>
                CIRCUIT occurrence
                <select value={selectedSection} onChange={(event) => setSelectedSection(Number(event.target.value))}>
                  {sections.map((item, index) => (
                    <option key={item.sourceIndex} value={index}>Entry {index + 1} (source index {item.sourceIndex})</option>
                  ))}
                </select>
              </label>
            )}
            <label title="Scale from the analyzed model region to the full physical system.">
              Region factor
              <input aria-label="CIRCUIT region factor" type="number" step="any" value={inputValue(circuit?.REGION_FACTOR)} onChange={(event) => updateCircuit((current) => ({...current, REGION_FACTOR: numberValue(event.target.value)}))} />
              <small>Full-system scale relative to the analyzed region.</small>
            </label>
            <label title="Number of electrically parallel circuit regions; the documented default is 1.">
              Parallel regions
              <input aria-label="CIRCUIT parallel regions" type="number" step="any" value={inputValue(circuit?.REGION_PARALLEL)} onChange={(event) => updateCircuit((current) => ({...current, REGION_PARALLEL: numberValue(event.target.value)}))} />
              <small>Number of parallel circuits; normally 1.</small>
            </label>
          </section>

          <div className={styles.circuitLists}>
            <section className={styles.circuitCard} aria-labelledby="circuit-series-title">
              <div className={styles.circuitCardHeader}>
                <div><h3 id="circuit-series-title">Source series</h3><p>Ordered SERIES_ID references connected to the external circuit.</p></div>
                <button type="button" onClick={addSeries}><EditorIcon name="add" /> Add series</button>
              </div>
              <datalist id="circuit-series-options">{references.seriesIds.map((id) => <option key={id} value={id} />)}</datalist>
              <div className={styles.networkTableWrap}>
                <table className={styles.networkTable}>
                  <thead><tr><th>#</th><th>Series ID</th><th>Reference</th><th>Actions</th></tr></thead>
                  <tbody>
                    {series.map((id, index) => (
                      <tr key={index}>
                        <td data-label="#">{index + 1}</td>
                        <td data-label="Series ID"><input className={styles.circuitTableInput} aria-label={`Series ID ${index + 1}`} type="number" step="1" list="circuit-series-options" value={inputValue(id)} onChange={(event) => updateSeriesValue(index, event.target.value)} /></td>
                        <td data-label="Reference">{Number.isInteger(id) && references.seriesIds.includes(id as number) ? <span className={styles.networkValidBadge}>Found</span> : <span className={styles.networkWarningBadge}>Manual / unresolved</span>}</td>
                        <td data-label="Actions"><RowActions label={`series row ${index + 1}`} index={index} count={series.length} onDuplicate={() => duplicateSeries(index)} onMove={moveSeries} onDelete={() => deleteSeries(index)} /></td>
                      </tr>
                    ))}
                    {series.length === 0 && <tr><td colSpan={4} className={styles.networkEmpty}>No source series are defined.</td></tr>}
                  </tbody>
                </table>
              </div>
            </section>

            <section className={styles.circuitCard} aria-labelledby="circuit-supplies-title">
              <div className={styles.circuitCardHeader}>
                <div><h3 id="circuit-supplies-title">Power supplies</h3><p>Independent current or voltage sources connected through the connection matrix.</p></div>
                <button type="button" onClick={addSupply}><EditorIcon name="add" /> Add power supply</button>
              </div>
              <div className={styles.networkTableWrap}>
                <table className={styles.networkTable}>
                  <thead><tr><th>#</th><th>PS ID</th><th>Type</th><th>Time ID</th><th>Initial current (A)</th><th>Actions</th></tr></thead>
                  <tbody>
                    {supplies.map((entry, index) => {
                      const supply = supplyRecord(entry);
                      return (
                        <tr key={index}>
                          <td data-label="#">{index + 1}</td>
                          <td data-label="PS ID"><input className={styles.circuitTableInput} aria-label={`Power supply ${index + 1} ID`} type="number" step="1" value={inputValue(supply.PS_ID)} onChange={(event) => updateSupply(index, 'PS_ID', event.target.value)} /></td>
                          <td data-label="Type"><select className={styles.circuitTableSelect} aria-label={`Power supply ${index + 1} type`} value={inputValue(supply.TYPE)} onChange={(event) => updateSupply(index, 'TYPE', event.target.value)}><option value="">Select…</option><option value="0">0 — current</option><option value="1">1 — voltage</option></select></td>
                          <td data-label="Time ID"><TimeFunctionReferencePicker compact catalog={timeFunctionCatalog} value={supply.TIME_ID} label={`Power supply ${index + 1} time ID`} onChange={(nextValue) => updateSupply(index, 'TIME_ID', nextValue)} /></td>
                          <td data-label="Initial current"><input className={styles.circuitTableInput} aria-label={`Power supply ${index + 1} initial current`} type="number" step="any" value={inputValue(supply.INITIAL_CURRENT)} onChange={(event) => updateSupply(index, 'INITIAL_CURRENT', event.target.value)} /></td>
                          <td data-label="Actions"><RowActions label={`power supply row ${index + 1}`} index={index} count={supplies.length} onDuplicate={() => duplicateSupply(index)} onMove={moveSupply} onDelete={() => deleteSupply(index)} /></td>
                        </tr>
                      );
                    })}
                    {supplies.length === 0 && <tr><td colSpan={6} className={styles.networkEmpty}>No power supplies are defined.</td></tr>}
                  </tbody>
                </table>
              </div>
              <small className={styles.circuitHelp}>TIME_ID 0 means a constant source. INITIAL_CURRENT applies to transient constant-voltage supplies.</small>
            </section>
          </div>

          {circuit && (
            <div className={styles.circuitMatrices}>
              <SymmetricMatrixEditor title="External inductance" description="Self and mutual inductance outside the finite-element region." unit="H" matrixKey="INDUCTANCE_MATRIX" modeKey="IN_IND" circuit={circuit} series={series} onCircuit={updateCircuit} />
              <SymmetricMatrixEditor title="External resistance" description="Self and mutual resistance outside the finite-element region." unit="Ω" matrixKey="RESISTANCE_MATRIX" modeKey="IN_RES" circuit={circuit} series={series} onCircuit={updateCircuit} />
              <ConnectionMatrixEditor circuit={circuit} series={series} supplies={supplies} onCircuit={updateCircuit} />
            </div>
          )}

          {issues.length > 0 && (
            <section className={styles.networkIssues} aria-label="CIRCUIT validation issues">
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
          <span>{series.length} series · {supplies.length} power suppl{supplies.length === 1 ? 'y' : 'ies'} · {errorCount} error{errorCount === 1 ? '' : 's'} · {warningCount} warning{warningCount === 1 ? '' : 's'}</span>
          <div>
            <button type="button" className="button button--secondary" onClick={requestClose}><EditorIcon name="cancel" /> Cancel</button>
            <button type="button" className="button button--primary" disabled={errorCount > 0} title={errorCount > 0 ? 'Fix structural errors before applying' : 'Apply CIRCUIT changes to the open document'} onClick={apply}><EditorIcon name="apply" /> Apply changes</button>
          </div>
        </footer>
      </div>
  );

  if (embedded) return editor;
  const modal = (
    <div
      className={styles.networkModalBackdrop}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) requestClose();
      }}>
      {editor}
    </div>
  );
  return createPortal(modal, portalTarget ?? document.body);
}

function RowActions({label, index, count, onDuplicate, onMove, onDelete}: {
  label: string;
  index: number;
  count: number;
  onDuplicate: () => void;
  onMove: (index: number, direction: -1 | 1) => void;
  onDelete: () => void;
}): ReactNode {
  return (
    <div className={styles.networkRowActions}>
      <button type="button" aria-label={`Duplicate ${label}`} title="Duplicate" onClick={onDuplicate}><EditorIcon name="copy" /></button>
      <button type="button" aria-label={`Move ${label} up`} title="Move up" disabled={index === 0} onClick={() => onMove(index, -1)}><EditorIcon name="up" /></button>
      <button type="button" aria-label={`Move ${label} down`} title="Move down" disabled={index === count - 1} onClick={() => onMove(index, 1)}><EditorIcon name="down" /></button>
      <button type="button" className={styles.networkDangerButton} aria-label={`Delete ${label}`} title="Delete" onClick={onDelete}><EditorIcon name="delete" /></button>
    </div>
  );
}

function SymmetricMatrixEditor({title, description, unit, matrixKey, modeKey, circuit, series, onCircuit}: {
  title: string;
  description: string;
  unit: string;
  matrixKey: 'INDUCTANCE_MATRIX' | 'RESISTANCE_MATRIX';
  modeKey: 'IN_IND' | 'IN_RES';
  circuit: CircuitDefinition;
  series: unknown[];
  onCircuit: (update: (current: CircuitDefinition) => CircuitDefinition) => void;
}): ReactNode {
  const matrix = matrixRecord(circuit[matrixKey]);
  const mode = matrix[modeKey];
  const grid = readSymmetricMatrix(matrix.MATRIX, series.length, mode);
  return (
    <section className={styles.circuitCard} aria-label={`${title} matrix`}>
      <div className={styles.circuitMatrixHeading}>
        <div><h3>{title} matrix <span>{unit}</span></h3><p>{description}</p></div>
        <label>Input mode <select aria-label={`${title} input mode`} value={inputValue(mode)} onChange={(event) => onCircuit((current) => setCircuitMatrixMode(current, matrixKey, numberValue(event.target.value)))}><option value="">Select…</option><option value="0">0 — lower triangle</option><option value="1">1 — diagonal only</option><option value="2">2 — none</option></select></label>
      </div>
      {mode === 2 ? <div className={styles.circuitImplicit}>No external {title.toLowerCase()} values are stored in mode 2.</div>
        : series.length === 0 ? <div className={styles.circuitImplicit}>Add a source series to edit this matrix.</div>
          : <MatrixGrid rowLabels={series} columnLabels={series} ariaLabel={title} values={grid} cell={(row, column) => {
            const editable = mode === 0 ? row >= column : mode === 1 && row === column;
            const value = mode === 1 && row !== column ? 0 : grid[row][column];
            return editable
              ? <input aria-label={`${title} row ${row + 1} column ${column + 1}`} type="number" step="any" value={inputValue(value)} onChange={(event) => onCircuit((current) => updateSymmetricMatrixCell(current, matrixKey, row, column, numberValue(event.target.value)))} />
              : <span className={styles.circuitMirroredCell} title={mode === 0 ? 'Mirrored from the lower triangle' : 'Zero in diagonal mode'}>{String(value ?? '')}</span>;
          }} />}
      <small className={styles.circuitHelp}>Mode 0 stores the lower triangle; mirrored cells are read-only. Mode 1 stores only the diagonal.</small>
    </section>
  );
}

function ConnectionMatrixEditor({circuit, series, supplies, onCircuit}: {
  circuit: CircuitDefinition;
  series: unknown[];
  supplies: unknown[];
  onCircuit: (update: (current: CircuitDefinition) => CircuitDefinition) => void;
}): ReactNode {
  const matrix = matrixRecord(circuit.CONNECTION_MATRIX);
  const mode = matrix.IN_CON;
  const grid = readConnectionMatrix(matrix.MATRIX, series.length, supplies.length);
  const supplyLabels = supplies.map((entry) => supplyRecord(entry).PS_ID);
  return (
    <section className={`${styles.circuitCard} ${styles.circuitConnectionCard}`} aria-label="Connection matrix">
      <div className={styles.circuitMatrixHeading}>
        <div><h3>Connection matrix</h3><p>Maps source-series currents and voltages to independent power supplies.</p></div>
        <label>Input mode <select aria-label="Connection input mode" value={inputValue(mode)} onChange={(event) => onCircuit((current) => setCircuitMatrixMode(current, 'CONNECTION_MATRIX', numberValue(event.target.value)))}><option value="">Select…</option><option value="0">0 — explicit matrix</option><option value="1">1 — identity</option></select></label>
      </div>
      {series.length === 0 || supplies.length === 0 ? <div className={styles.circuitImplicit}>Add source series and power supplies to edit this matrix.</div>
        : <MatrixGrid rowLabels={series} columnLabels={supplyLabels} ariaLabel="Connection" values={grid} cell={(row, column) => {
          const value = mode === 1 ? (row === column ? 1 : 0) : grid[row][column];
          return mode === 0
            ? <input aria-label={`Connection row ${row + 1} column ${column + 1}`} type="number" step="any" value={inputValue(value)} onChange={(event) => onCircuit((current) => updateConnectionMatrixCell(current, row, column, numberValue(event.target.value)))} />
            : <span className={styles.circuitMirroredCell} title="Implicit identity value">{String(value ?? '')}</span>;
        }} />}
      <small className={styles.circuitHelp}>Mode 1 is an implicit identity matrix and requires the same number of series and power supplies.</small>
    </section>
  );
}

function MatrixGrid({rowLabels, columnLabels, ariaLabel, values, cell}: {
  rowLabels: unknown[];
  columnLabels: unknown[];
  ariaLabel: string;
  values: unknown[][];
  cell: (row: number, column: number) => ReactNode;
}): ReactNode {
  return (
    <div className={styles.circuitMatrixWrap}>
      <table className={styles.circuitMatrix} aria-label={`${ariaLabel} matrix values`}>
        <thead><tr><th scope="col">Series \ {ariaLabel === 'Connection' ? 'supply' : 'series'}</th>{columnLabels.map((label, index) => <th scope="col" key={index}>{String(label || `#${index + 1}`)}</th>)}</tr></thead>
        <tbody>{values.map((_, row) => <tr key={row}><th scope="row">{String(rowLabels[row] || `#${row + 1}`)}</th>{columnLabels.map((__, column) => <td key={column}>{cell(row, column)}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}
