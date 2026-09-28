import React, {type KeyboardEvent, type ReactNode, useEffect, useRef, useState} from 'react';

import EditorIcon from './EditorIcon';
import styles from './styles.module.css';

export interface AddItemMenuOption<T extends string> {
  value: T;
  label: string;
  description: string;
}

interface AddItemMenuProps<T extends string> {
  label: string;
  itemName: string;
  options: AddItemMenuOption<T>[];
  onSelect: (value: T) => void;
}

export default function AddItemMenu<T extends string>({
  label,
  itemName,
  options,
  onSelect,
}: AddItemMenuProps<T>): ReactNode {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return undefined;
    containerRef.current?.querySelector<HTMLButtonElement>('[role="menuitem"]')?.focus();
    const dismiss = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', dismiss);
    return () => document.removeEventListener('mousedown', dismiss);
  }, [open]);

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!open) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      setOpen(false);
      triggerRef.current?.focus();
      return;
    }
    const items = Array.from(containerRef.current?.querySelectorAll<HTMLButtonElement>('[role="menuitem"]') ?? []);
    const currentIndex = items.indexOf(document.activeElement as HTMLButtonElement);
    let nextIndex: number | undefined;
    if (event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % items.length;
    else if (event.key === 'ArrowUp') nextIndex = (currentIndex - 1 + items.length) % items.length;
    else if (event.key === 'Home') nextIndex = 0;
    else if (event.key === 'End') nextIndex = items.length - 1;
    else if (event.key === 'Tab') setOpen(false);
    if (nextIndex !== undefined) {
      event.preventDefault();
      items[nextIndex]?.focus();
    }
  };

  return (
    <div ref={containerRef} className={styles.addItemMenu} onKeyDown={handleKeyDown}>
      <button
        ref={triggerRef}
        type="button"
        className={`button button--primary button--sm ${styles.addItemMenuTrigger}`}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}>
        <EditorIcon name="add" /> {label} <span className={styles.addItemMenuCaret} aria-hidden="true">▾</span>
      </button>
      {open && (
        <div className={styles.addItemMenuPanel} role="menu" aria-label={`Choose ${itemName} type`}>
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              role="menuitem"
              aria-label={`Add ${option.label} (${option.value})`}
              className={styles.addItemMenuOption}
              onClick={() => {
                setOpen(false);
                onSelect(option.value);
              }}>
              <span className={styles.addItemMenuOptionHeading}>
                <strong>{option.label}</strong>
                <code>{option.value}</code>
              </span>
              <small>{option.description}</small>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
