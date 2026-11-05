import React, {useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode} from 'react';
import {createPortal} from 'react-dom';

import EditorIcon from './EditorIcon';
import type {TimeFunctionReferenceCatalog, TimeFunctionReferenceChoice} from './timeFunctionModel';
import styles from './styles.module.css';

interface TimeFunctionReferencePickerProps {
  catalog: TimeFunctionReferenceCatalog;
  value: unknown;
  label: string;
  fieldKey?: string;
  help?: string;
  unit?: string;
  compact?: boolean;
  onChange: (value: number | string) => void;
}

function inputValue(value: unknown): string | number {
  return typeof value === 'number' || typeof value === 'string' ? value : '';
}

function numberValue(raw: string): number | string {
  return raw.trim() === '' ? '' : Number(raw);
}

function stateMessage(state: TimeFunctionReferenceCatalog['state']): string {
  if (state === 'missing') return '18_Time_Function is missing. Manual TIME_ID entry is still available.';
  if (state === 'empty') return 'No Time Functions are defined. Manual TIME_ID entry is still available.';
  if (state === 'malformed') return '18_Time_Function is malformed. Repair it in JSON; manual TIME_ID entry remains available.';
  return 'No Time Functions match this search.';
}

function searchText(choice: TimeFunctionReferenceChoice): string {
  return [choice.timeId, choice.option, choice.optionLabel, choice.summary, choice.formattedJson].join(' ').toLocaleLowerCase();
}

export default function TimeFunctionReferencePicker({
  catalog,
  value,
  label,
  fieldKey,
  help,
  unit,
  compact = false,
  onChange,
}: TimeFunctionReferencePickerProps): ReactNode {
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

  const choose = (timeId: number) => {
    onChange(timeId);
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
    const buttons = Array.from(panelRef.current?.querySelectorAll<HTMLButtonElement>('[data-time-choice]:not(:disabled)') ?? []);
    if (buttons.length === 0) return;
    const active = document.activeElement;
    const index = buttons.findIndex((button) => button === active);
    const nextIndex = event.key === 'ArrowDown'
      ? (index + 1 + buttons.length) % buttons.length
      : (index <= 0 ? buttons.length - 1 : index - 1);
    event.preventDefault();
    buttons[nextIndex].focus();
  };

  const input = (
    <div className={styles.timeReferenceInputRow}>
      <input
        aria-label={fieldKey ? `${label} (${fieldKey})` : label}
        type="number"
        step="1"
        value={inputValue(value)}
        onChange={(event) => onChange(numberValue(event.target.value))}
      />
      <button
        ref={buttonRef}
        type="button"
        className={styles.materialReferenceButton}
        aria-label={`Choose ${label}`}
        aria-expanded={open}
        aria-controls={open ? pickerId : undefined}
        onClick={() => setOpen((currentOpen) => !currentOpen)}>
        <EditorIcon name="time" />
      </button>
    </div>
  );

  const panel = open && portalTarget ? createPortal(
    <div
      ref={panelRef}
      id={pickerId}
      role="dialog"
      aria-label="Choose a Time Function"
      className={`${styles.materialReferencePicker} ${styles.timeFunctionReferencePicker}`}
      style={position}
      onKeyDown={onPanelKeyDown}>
      <div className={styles.materialReferencePickerHeader}>
        <strong>Choose a Time Function</strong>
        <button type="button" aria-label="Close Time Function picker" onClick={() => close()}><EditorIcon name="close" /></button>
      </div>
      <input
        ref={searchRef}
        type="search"
        aria-label="Search Time Functions"
        placeholder="Search ID, option, summary, or JSON…"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />
      <div className={styles.materialReferenceChoice}>
        <div><strong>TIME_ID 0</strong><span>Circuit/network-driven or constant source</span></div>
        <button data-time-choice type="button" aria-label="Use TIME_ID 0" disabled={current === 0} onClick={() => choose(0)}>{current === 0 ? 'Selected' : 'Use'}</button>
      </div>
      <div className={styles.materialReferenceList}>
        {filtered.map((choice) => {
          const selected = choice.timeId !== null && current === choice.timeId;
          const status = choice.duplicate ? 'Duplicate ID'
            : choice.validationStatus === 'error' ? 'Has errors'
              : choice.validationStatus === 'warning' ? 'Warning' : 'Valid';
          return <div key={choice.key} className={styles.materialReferenceChoice}>
            <div>
              <strong>{choice.timeId === null ? `Entry ${choice.entryIndex + 1} · invalid TIME_ID` : `TIME_ID ${choice.timeId}`} · {choice.optionLabel}</strong>
              <span>{choice.summary}</span>
              <span className={choice.validationStatus === 'error' ? styles.timeReferenceError : choice.validationStatus === 'warning' || choice.duplicate ? styles.timeReferenceWarning : undefined}>
                {status}{choice.option !== null ? ` · OPTION ${choice.option}` : ''}
              </span>
            </div>
            <button
              data-time-choice
              type="button"
              disabled={!choice.selectable || selected}
              aria-label={choice.selectable ? `Use TIME_ID ${choice.timeId}` : `Entry ${choice.entryIndex + 1} has an invalid TIME_ID`}
              onClick={() => choice.timeId !== null && choose(choice.timeId)}>
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
