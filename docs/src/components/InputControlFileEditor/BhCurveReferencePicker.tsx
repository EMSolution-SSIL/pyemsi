import React, {useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode} from 'react';
import {createPortal} from 'react-dom';

import type {BhCurveReferenceCatalog, BhCurveReferenceChoice} from './bhCurveModel';
import EditorIcon from './EditorIcon';
import styles from './styles.module.css';

interface BhCurveReferencePickerProps {
  catalog: BhCurveReferenceCatalog;
  value: unknown;
  label: string;
  fieldKey?: string;
  help?: string;
  unit?: string;
  compact?: boolean;
  allowZero?: boolean;
  required?: boolean;
  onChange: (value: number | string | undefined) => void;
}

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function numberValue(raw: string, required: boolean): number | string | undefined {
  if (raw.trim() === '') return required ? '' : undefined;
  return Number(raw);
}

function stateMessage(state: BhCurveReferenceCatalog['state']): string {
  if (state === 'missing') return '20_BH_Curve is missing. Manual curve ID entry is still available.';
  if (state === 'empty') return 'No B-H Curves are defined. Manual curve ID entry is still available.';
  if (state === 'malformed') return '20_BH_Curve is malformed. Repair it in JSON; manual curve ID entry remains available.';
  return 'No B-H Curves match this search.';
}

function searchText(choice: BhCurveReferenceChoice): string {
  return [choice.curveId, choice.typeLabel, choice.summary, choice.formattedJson].join(' ').toLocaleLowerCase();
}

export default function BhCurveReferencePicker({
  catalog,
  value,
  label,
  fieldKey,
  help,
  unit,
  compact = false,
  allowZero = false,
  required = true,
  onChange,
}: BhCurveReferencePickerProps): ReactNode {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [position, setPosition] = useState<CSSProperties>({left: 8, top: 8});
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const pickerId = React.useId();
  const portalTarget = open ? buttonRef.current?.closest('[role="dialog"]') ?? document.body : null;
  const current = typeof value === 'number' ? value : Number.NaN;
  const filtered = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    return query ? catalog.choices.filter((choice) => searchText(choice).includes(query)) : catalog.choices;
  }, [catalog, search]);

  const close = useCallback((restoreFocus = true) => {
    setOpen(false);
    setSearch('');
    if (restoreFocus) requestAnimationFrame(() => buttonRef.current?.focus());
  }, []);

  const place = useCallback(() => {
    const button = buttonRef.current;
    const panel = panelRef.current;
    if (!button || !panel) return;
    const margin = 8;
    const gap = 5;
    const trigger = button.getBoundingClientRect();
    const panelRect = panel.getBoundingClientRect();
    const measuredWidth = panelRect.width || Math.min(432, window.innerWidth - margin * 2);
    const width = Math.min(measuredWidth, window.innerWidth - margin * 2);
    const left = Math.min(Math.max(margin, trigger.right - width), window.innerWidth - width - margin);
    const below = trigger.bottom + gap;
    const top = below + panelRect.height <= window.innerHeight - margin
      ? below : Math.max(margin, trigger.top - panelRect.height - gap);
    setPosition({left, top, width});
  }, []);

  useEffect(() => {
    if (!open) return;
    const frame = requestAnimationFrame(() => {
      place();
      searchRef.current?.focus();
    });
    const onViewportChange = () => place();
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target as Node;
      if (panelRef.current?.contains(target) || buttonRef.current?.contains(target)) return;
      close();
    };
    window.addEventListener('resize', onViewportChange);
    window.addEventListener('scroll', onViewportChange, true);
    document.addEventListener('mousedown', onPointerDown, true);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', onViewportChange);
      window.removeEventListener('scroll', onViewportChange, true);
      document.removeEventListener('mousedown', onPointerDown, true);
    };
  }, [close, open, place]);

  const choose = (curveId: number) => {
    onChange(curveId);
    close();
  };

  const onPanelKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      event.nativeEvent.stopImmediatePropagation();
      close();
      return;
    }
    if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;
    const buttons = Array.from(panelRef.current?.querySelectorAll<HTMLButtonElement>('[data-bh-curve-choice]:not(:disabled)') ?? []);
    if (buttons.length === 0) return;
    const active = document.activeElement;
    const index = buttons.findIndex((button) => button === active);
    const nextIndex = event.key === 'ArrowDown'
      ? (index + 1 + buttons.length) % buttons.length
      : (index <= 0 ? buttons.length - 1 : index - 1);
    event.preventDefault();
    buttons[nextIndex].focus();
  };

  const inputLabel = fieldKey ? `${label} (${fieldKey})` : label;
  const input = <div className={styles.timeReferenceInputRow}>
    <input aria-label={inputLabel} type="number" step="1" value={inputValue(value)}
      placeholder={!required ? 'Not set' : undefined}
      onChange={(event) => onChange(numberValue(event.target.value, required))} />
    <button ref={buttonRef} type="button" className={styles.materialReferenceButton}
      aria-label={`Choose ${label}`} aria-expanded={open} aria-controls={open ? pickerId : undefined}
      onClick={() => setOpen((currentOpen) => !currentOpen)}><EditorIcon name="curve" /></button>
  </div>;

  const panel = open && portalTarget ? createPortal(
    <div ref={panelRef} id={pickerId} role="dialog" aria-label={`Choose ${label}`}
      className={`${styles.materialReferencePicker} ${styles.timeFunctionReferencePicker}`}
      style={position} onKeyDown={onPanelKeyDown}>
      <div className={styles.materialReferencePickerHeader}>
        <strong>Choose a B-H Curve</strong>
        <button type="button" aria-label={`Close ${label} picker`} onClick={() => close()}><EditorIcon name="close" /></button>
      </div>
      <input ref={searchRef} type="search" aria-label={`Search B-H Curves for ${label}`}
        placeholder="Search ID, type, summary, or JSON…" value={search} onChange={(event) => setSearch(event.target.value)} />
      {allowZero && <div className={styles.materialReferenceChoice}>
        <div><strong>BH_CURVE_ID 0</strong><span>Linear permeability; no nonlinear B-H table is referenced.</span></div>
        <button data-bh-curve-choice type="button" aria-label={`Use BH_CURVE_ID 0 for ${label}`} disabled={current === 0} onClick={() => choose(0)}>{current === 0 ? 'Selected' : 'Use'}</button>
      </div>}
      <div className={styles.materialReferenceList}>
        {filtered.map((choice) => {
          const selected = choice.curveId !== null && current === choice.curveId;
          const status = choice.duplicate ? 'Duplicate ID'
            : choice.validationStatus === 'error' ? 'Has errors'
              : choice.validationStatus === 'warning' ? 'Warning' : 'Valid';
          return <div key={choice.key} className={styles.materialReferenceChoice}>
            <div>
              <strong>{choice.curveId === null ? `Entry ${choice.entryIndex + 1} · invalid BH_CURVE_ID` : `BH_CURVE_ID ${choice.curveId}`} · {choice.typeLabel}</strong>
              <span>{choice.summary}</span>
              <span className={choice.validationStatus === 'error' ? styles.timeReferenceError : choice.validationStatus === 'warning' || choice.duplicate ? styles.timeReferenceWarning : undefined}>{status}</span>
            </div>
            <button data-bh-curve-choice type="button" disabled={!choice.selectable || selected}
              aria-label={choice.selectable ? `Use BH_CURVE_ID ${choice.curveId} for ${label}` : `Entry ${choice.entryIndex + 1} has an invalid BH_CURVE_ID`}
              onClick={() => choice.curveId !== null && choose(choice.curveId)}>
              {!choice.selectable ? 'Invalid ID' : selected ? 'Selected' : 'Use'}
            </button>
            <details><summary>Raw JSON</summary><pre>{choice.formattedJson}</pre></details>
          </div>;
        })}
        {filtered.length === 0 && <p className={styles.materialReferenceEmpty}>{stateMessage(catalog.state)}</p>}
      </div>
    </div>,
    portalTarget,
  ) : null;

  if (compact) return <div className={styles.timeReferenceCompact}>{input}{panel}</div>;
  return <div className={`${styles.networkField} ${styles.materialReferenceField}`}>
    <span>{label}{(fieldKey || unit) && <em>{fieldKey}{unit ? `${fieldKey ? ' · ' : ''}${unit}` : ''}</em>}</span>
    {input}
    {help && <small>{help}</small>}
    {panel}
  </div>;
}
