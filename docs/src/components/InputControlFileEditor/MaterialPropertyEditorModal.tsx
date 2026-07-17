import React, {type ReactNode, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createPortal} from 'react-dom';

import AddItemMenu from './AddItemMenu';
import EditorIcon from './EditorIcon';
import {
  createMaterialProperties,
  createSurfaceMaterial,
  createVolumeMaterial,
  deepClone,
  getMaterialField,
  inspectSurfaceMaterial,
  isPlainRecord,
  MATERIAL_DOCUMENTATION,
  MATERIAL_FIELD_GROUPS,
  nonlinearParametersKey,
  NONLINEAR_IMPEDANCE_FIELDS,
  removeMaterialField,
  replaceMaterialProperties,
  replaceSurfaceMaterials,
  replaceVolumeMaterials,
  setMaterialField,
  SURFACE_MATERIAL_SCHEMAS,
  SURFACE_MATERIAL_TYPES,
  surfaceMaterials,
  surfaceMaterialSummary,
  validateMaterialProperties,
  VOLUME_BASE_FIELDS,
  VOLUME_FLAG_FIELDS,
  volumeMaterials,
  volumeMaterialSummary,
  type MaterialFieldDefinition,
  type MaterialFieldGroupDefinition,
  type MaterialPropertyValidationIssue,
  type MaterialSection,
  type SurfaceMaterialType,
} from './materialPropertyModel';
import styles from './styles.module.css';

interface MaterialPropertyEditorModalProps {
  documentName: string;
  value: unknown;
  portalTarget?: Element;
  onApply: (value: unknown) => void;
  onClose: () => void;
}

type StatusFilter = 'ALL' | 'VALID' | 'WARNING' | 'ERROR';

const GROUP_DEFAULTS: Record<string, Record<string, unknown>> = {
  conductivity: {SIGMA: 0},
  sigmaXyz: {COORD_ID: 0, FACTOR_XYZ: [1, 1, 1]},
  permittivity: {EPS: 1},
  epsXyz: {COORD_ID: 0, FACTOR_XYZ: [1, 1, 1]},
  magnetic: {MU: 1},
  muXyz: {COORD_ID: 0, FACTOR_XYZ: [1, 1, 1]},
  packing: {PACKING_FACTOR: 0.95, COORD_ID: 0, PACKING_DIRECTION: [0, 0, 1]},
  bhCurveXyz: {COORD_ID: 0, BH_XYZ_ID: [0, 0, 0], MU_XYZ: [1, 1, 1]},
  anisotropy2d: {COORD_ID: 0, BH_XY: 1, MU_Z: 1},
  hysteresis: {COORD_ID: 0, MU_Z: 1, DB_CAL: 0.001},
  jaModel: {MS: [1_670_000, 1_670_000], K: [82, 82], C: [0.1, 0.1], A: [50, 50], ALPHA: [0.00004907, 0.00004907]},
  playModel: {PLAY_ID: 1, DB_FACTOR: 0, B_MIN_LOSS_CORRECTION: 0},
  muComplex: {MU_Re: 1, MU_Im: 0},
  ironLoss: {COORD_ID: 0, MASS_DENSITY: 7850, KE: 0, KH: 0},
};

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

function matchesStatus(issues: MaterialPropertyValidationIssue[], filter: StatusFilter): boolean {
  if (filter === 'ALL') return true;
  if (filter === 'ERROR') return issues.some((issue) => issue.severity === 'error');
  if (filter === 'WARNING') return !issues.some((issue) => issue.severity === 'error') && issues.some((issue) => issue.severity === 'warning');
  return issues.length === 0;
}

export default function MaterialPropertyEditorModal({
  documentName,
  value,
  portalTarget,
  onApply,
  onClose,
}: MaterialPropertyEditorModalProps): ReactNode {
  const initialPropertiesRef = useRef(createMaterialProperties(value));
  const initialJsonRef = useRef(JSON.stringify(initialPropertiesRef.current));
  const [draftProperties, setDraftProperties] = useState(initialPropertiesRef.current);
  const [section, setSection] = useState<MaterialSection>('general');
  const [selectedIndex, setSelectedIndex] = useState<number>();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const [surfaceTypeFilter, setSurfaceTypeFilter] = useState('ALL');
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const draftRef = useRef(draftProperties);
  const restoreFocusRef = useRef<HTMLElement | null>(document.activeElement instanceof HTMLElement ? document.activeElement : null);

  useEffect(() => { draftRef.current = draftProperties; }, [draftProperties]);

  const requestClose = useCallback(() => {
    if (JSON.stringify(draftRef.current) !== initialJsonRef.current
      && !window.confirm('Discard the unsaved Material Property changes?')) return;
    onClose();
  }, [onClose]);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeButtonRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); requestClose(); return; }
      if (event.key !== 'Tab' || !dialogRef.current) return;
      const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>(
        'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]',
      ));
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable.at(-1)!;
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', onKeyDown);
      restoreFocusRef.current?.focus();
    };
  }, [requestClose]);

  const stagedRoot = useMemo(() => replaceMaterialProperties(value, draftProperties), [draftProperties, value]);
  const issues = useMemo(() => validateMaterialProperties(stagedRoot), [stagedRoot]);
  const errorCount = issues.filter((issue) => issue.severity === 'error').length;
  const warningCount = issues.filter((issue) => issue.severity === 'warning').length;
  const volumes = volumeMaterials(draftProperties);
  const surfaces = surfaceMaterials(draftProperties);

  const selectSection = (next: MaterialSection) => {
    setSection(next);
    setSelectedIndex(undefined);
    setSearch('');
    setStatusFilter('ALL');
  };

  const modal = (
    <div className={styles.networkModalBackdrop} onMouseDown={(event) => { if (event.target === event.currentTarget) requestClose(); }}>
      <div ref={dialogRef} className={`${styles.networkModal} ${styles.fieldSourceModal}`} role="dialog" aria-modal="true" aria-labelledby="material-property-editor-title">
        <header className={styles.networkModalHeader}>
          <div><h2 id="material-property-editor-title">Material Properties editor</h2><div className={styles.networkModalSubtitle}>{documentName}</div></div>
          <div className={styles.networkHeaderActions}>
            <a href={MATERIAL_DOCUMENTATION.overview} target="_blank" rel="noreferrer">Material documentation <EditorIcon name="external" /></a>
            <button ref={closeButtonRef} type="button" className={styles.networkIconButton} aria-label="Close Material Properties editor" title="Close Material Properties editor" onClick={requestClose}><EditorIcon name="close" /></button>
          </div>
        </header>

        <nav className={styles.materialTabs} aria-label="Material Property sections">
          {([['general', 'General'], ['volume', `Volume (${volumes.length})`], ['surface', `Surface (${surfaces.length})`]] as const).map(([key, label]) => (
            <button key={key} type="button" aria-current={section === key ? 'page' : undefined} className={section === key ? styles.materialTabActive : undefined} onClick={() => selectSection(key)}>{label}</button>
          ))}
        </nav>

        <div className={`${styles.networkModalBody} ${styles.fieldSourceModalBody}`}>
          {section === 'general' ? (
            <GeneralEditor properties={draftProperties} issues={issues.filter((issue) => issue.section === 'general')} onChange={setDraftProperties} />
          ) : section === 'volume' ? (
            selectedIndex === undefined ? (
              <VolumeMaster entries={volumes} issues={issues} search={search} statusFilter={statusFilter}
                onSearch={setSearch} onStatusFilter={setStatusFilter} onEdit={setSelectedIndex}
                onEntries={(entries) => setDraftProperties((current) => replaceVolumeMaterials(current, entries))}
                onAdd={() => {
                  const next = [...volumes, createVolumeMaterial(value)];
                  setDraftProperties((current) => replaceVolumeMaterials(current, next));
                  setSelectedIndex(next.length - 1);
                }} />
            ) : (
              <VolumeDetail entry={volumes[selectedIndex]} index={selectedIndex} issues={issues.filter((issue) => issue.section === 'volume' && issue.entryIndex === selectedIndex)}
                onBack={() => setSelectedIndex(undefined)} onChange={(entry) => {
                  const next = [...volumes]; next[selectedIndex] = entry;
                  setDraftProperties((current) => replaceVolumeMaterials(current, next));
                }} />
            )
          ) : selectedIndex === undefined ? (
            <SurfaceMaster entries={surfaces} issues={issues} search={search} statusFilter={statusFilter} typeFilter={surfaceTypeFilter}
              onSearch={setSearch} onStatusFilter={setStatusFilter} onTypeFilter={setSurfaceTypeFilter} onEdit={setSelectedIndex}
              onEntries={(entries) => setDraftProperties((current) => replaceSurfaceMaterials(current, entries))}
              onAdd={(type) => {
                const next = [...surfaces, createSurfaceMaterial(type)];
                setDraftProperties((current) => replaceSurfaceMaterials(current, next));
                setSelectedIndex(next.length - 1);
              }} />
          ) : (
            <SurfaceDetail entry={surfaces[selectedIndex]} index={selectedIndex} issues={issues.filter((issue) => issue.section === 'surface' && issue.entryIndex === selectedIndex)}
              onBack={() => setSelectedIndex(undefined)} onChange={(entry) => {
                const next = [...surfaces]; next[selectedIndex] = entry;
                setDraftProperties((current) => replaceSurfaceMaterials(current, next));
              }} />
          )}
        </div>

        <footer className={styles.networkModalFooter}>
          <span>{volumes.length} volume · {surfaces.length} surface · {errorCount} error{errorCount === 1 ? '' : 's'} · {warningCount} warning{warningCount === 1 ? '' : 's'}</span>
          <div>
            <button type="button" className="button button--secondary" onClick={requestClose}><EditorIcon name="cancel" /> Cancel</button>
            <button type="button" className="button button--primary" disabled={errorCount > 0} title={errorCount > 0 ? 'Fix structural errors before applying' : 'Apply all Material Property changes to the open document'} onClick={() => onApply(stagedRoot)}><EditorIcon name="apply" /> Apply changes</button>
          </div>
        </footer>
      </div>
    </div>
  );
  return createPortal(modal, portalTarget ?? document.body);
}

function GeneralEditor({properties, issues, onChange}: {
  properties: Record<string, unknown>;
  issues: MaterialPropertyValidationIssue[];
  onChange: (value: Record<string, unknown>) => void;
}): ReactNode {
  const update = (key: string, value: unknown) => onChange({...properties, [key]: value});
  const remove = (key: string) => { const next = {...properties}; delete next[key]; onChange(next); };
  return <div className={styles.fieldSourceDetail}>
    <div className={styles.fieldSourceDescription}>
      <div><strong>General material settings</strong><p>Settings shared by volume and surface material definitions.</p></div>
      <a href={MATERIAL_DOCUMENTATION.overview} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a>
    </div>
    <div className={styles.fieldSourceFieldGrid}>
      <label className={styles.networkField}><span>Extend total-potential region<em>EXTEND_TOTAL_for_COIL</em></span>
        <select aria-label="Extend total-potential region (EXTEND_TOTAL_for_COIL)" value={inputValue(properties.EXTEND_TOTAL_for_COIL)} onChange={(event) => update('EXTEND_TOTAL_for_COIL', Number(event.target.value))}>
          <option value={0}>0 — Disabled</option><option value={1}>1 — Enabled</option>
        </select><small>Extend the total-potential region by one layer for COIL calculations.</small></label>
      <label className={styles.networkField}><span>Thin-element criterion<em>THIN_CRITERION</em></span>
        <input aria-label="Thin-element criterion (THIN_CRITERION)" type="number" step="any" value={inputValue(properties.THIN_CRITERION)} placeholder="Not set" onChange={(event) => event.target.value === '' ? remove('THIN_CRITERION') : update('THIN_CRITERION', numberValue(event.target.value))} />
        <small>Optional aspect-ratio threshold for materials marked as thin elements.</small></label>
    </div>
    <ValidationIssues label="Material Property validation issues" issues={issues} />
  </div>;
}

function VolumeMaster({entries, issues, search, statusFilter, onSearch, onStatusFilter, onEdit, onEntries, onAdd}: {
  entries: unknown[];
  issues: MaterialPropertyValidationIssue[];
  search: string;
  statusFilter: StatusFilter;
  onSearch: (value: string) => void;
  onStatusFilter: (value: StatusFilter) => void;
  onEdit: (index: number) => void;
  onEntries: (entries: unknown[]) => void;
  onAdd: () => void;
}): ReactNode {
  const visible = entries.map((entry, index) => ({entry, index})).filter(({entry, index}) => {
    const entryIssues = issues.filter((issue) => issue.section === 'volume' && issue.entryIndex === index);
    return matchesStatus(entryIssues, statusFilter) && `${volumeMaterialSummary(entry)} ${JSON.stringify(entry)}`.toLowerCase().includes(search.toLowerCase());
  });
  return <>
    <div className={styles.networkToolbar}>
      <input aria-label="Search volume materials" type="search" placeholder="Search volume materials…" value={search} onChange={(event) => onSearch(event.target.value)} />
      <StatusSelect label="Filter volume material status" value={statusFilter} onChange={onStatusFilter} />
      <button type="button" className="button button--primary button--sm" onClick={onAdd}><EditorIcon name="add" /> Add volume material</button>
    </div>
    <div className={styles.networkTableWrap}><table className={styles.networkTable}>
      <thead><tr><th>#</th><th>MAT_ID</th><th>Name</th><th>Summary</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>{visible.map(({entry, index}) => {
        const entryIssues = issues.filter((issue) => issue.section === 'volume' && issue.entryIndex === index);
        const record = isPlainRecord(entry) ? entry : undefined;
        return <tr key={index}><td data-label="#">{index + 1}</td><td data-label="MAT_ID">{String(record?.MAT_ID ?? '—')}</td><td data-label="Name">{String(record?.MAT_NAME ?? '—')}</td>
          <td data-label="Summary">{volumeMaterialSummary(entry)}</td><td data-label="Status"><StatusBadge issues={entryIssues} /></td>
          <td data-label="Actions"><RowActions label="volume material" index={index} count={entries.length} onEdit={() => onEdit(index)} onDuplicate={() => {
            const next = [...entries]; next.splice(index + 1, 0, deepClone(entry)); onEntries(next);
          }} onMove={(direction) => moveEntry(entries, index, direction, onEntries)} onDelete={() => {
            if (window.confirm(`Delete volume material ${index + 1}?`)) onEntries(entries.filter((_, itemIndex) => itemIndex !== index));
          }} /></td></tr>;
      })}{visible.length === 0 && <tr><td colSpan={6} className={styles.networkEmpty}>No volume materials match the current filters.</td></tr>}</tbody>
    </table></div>
  </>;
}

function SurfaceMaster({entries, issues, search, statusFilter, typeFilter, onSearch, onStatusFilter, onTypeFilter, onEdit, onEntries, onAdd}: {
  entries: unknown[];
  issues: MaterialPropertyValidationIssue[];
  search: string;
  statusFilter: StatusFilter;
  typeFilter: string;
  onSearch: (value: string) => void;
  onStatusFilter: (value: StatusFilter) => void;
  onTypeFilter: (value: string) => void;
  onEdit: (index: number) => void;
  onEntries: (entries: unknown[]) => void;
  onAdd: (type: SurfaceMaterialType) => void;
}): ReactNode {
  const visible = entries.map((entry, index) => ({entry, index, inspected: inspectSurfaceMaterial(entry)})).filter(({entry, index, inspected}) => {
    const type = inspected.kind === 'known' ? inspected.type : inspected.reason.toUpperCase();
    const entryIssues = issues.filter((issue) => issue.section === 'surface' && issue.entryIndex === index);
    return (typeFilter === 'ALL' || type === typeFilter) && matchesStatus(entryIssues, statusFilter)
      && `${type} ${surfaceMaterialSummary(entry)} ${JSON.stringify(entry)}`.toLowerCase().includes(search.toLowerCase());
  });
  return <>
    <div className={`${styles.networkToolbar} ${styles.materialToolbar}`}>
      <input aria-label="Search surface materials" type="search" placeholder="Search surface materials…" value={search} onChange={(event) => onSearch(event.target.value)} />
      <select aria-label="Filter surface material type" value={typeFilter} onChange={(event) => onTypeFilter(event.target.value)}><option value="ALL">All types</option>{SURFACE_MATERIAL_TYPES.map((type) => <option key={type}>{type}</option>)}<option value="UNKNOWN">Unknown</option><option value="MALFORMED">Malformed</option><option value="MULTIPLE">Multiple</option></select>
      <StatusSelect label="Filter surface material status" value={statusFilter} onChange={onStatusFilter} />
      <div className={styles.networkAddGroup}>
        <AddItemMenu
          label="Add surface material"
          itemName="surface material"
          options={SURFACE_MATERIAL_TYPES.map((type) => ({
            value: type,
            label: SURFACE_MATERIAL_SCHEMAS[type].label,
            description: SURFACE_MATERIAL_SCHEMAS[type].description,
          }))}
          onSelect={onAdd} />
      </div>
    </div>
    <div className={styles.networkTableWrap}><table className={styles.networkTable}>
      <thead><tr><th>#</th><th>Type</th><th>SMAT_ID</th><th>Summary</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>{visible.map(({entry, index, inspected}) => {
        const entryIssues = issues.filter((issue) => issue.section === 'surface' && issue.entryIndex === index);
        const record = isPlainRecord(entry) ? entry : undefined;
        const type = inspected.kind === 'known' ? inspected.type : inspected.reason.toUpperCase();
        return <tr key={index}><td data-label="#">{index + 1}</td><td data-label="Type"><strong>{type}</strong></td><td data-label="SMAT_ID">{String(record?.SMAT_ID ?? '—')}</td>
          <td data-label="Summary">{surfaceMaterialSummary(entry)}</td><td data-label="Status"><StatusBadge issues={entryIssues} /></td>
          <td data-label="Actions"><RowActions label="surface material" index={index} count={entries.length} onEdit={() => onEdit(index)} onDuplicate={() => {
            const next = [...entries]; next.splice(index + 1, 0, deepClone(entry)); onEntries(next);
          }} onMove={(direction) => moveEntry(entries, index, direction, onEntries)} onDelete={() => {
            if (window.confirm(`Delete surface material ${index + 1}?`)) onEntries(entries.filter((_, itemIndex) => itemIndex !== index));
          }} /></td></tr>;
      })}{visible.length === 0 && <tr><td colSpan={6} className={styles.networkEmpty}>No surface materials match the current filters.</td></tr>}</tbody>
    </table></div>
  </>;
}

function VolumeDetail({entry, index, issues, onBack, onChange}: {
  entry: unknown;
  index: number;
  issues: MaterialPropertyValidationIssue[];
  onBack: () => void;
  onChange: (entry: unknown) => void;
}): ReactNode {
  if (!isPlainRecord(entry)) return <RawDetail title={`Volume entry ${index + 1} · Raw JSON`} label="Raw volume material JSON" value={entry} issues={issues} onBack={onBack} onSave={onChange} />;
  const updateField = (path: string, value: unknown) => { const next = deepClone(entry); value === undefined ? removeMaterialField(next, path) : setMaterialField(next, path, value); onChange(next); };
  const addGroup = (key: string) => updateField(MATERIAL_FIELD_GROUPS[key].key, deepClone(GROUP_DEFAULTS[key]));
  const removeGroup = (key: string) => {
    const group = MATERIAL_FIELD_GROUPS[key];
    if (window.confirm(`Remove ${group.label} and all of its values?`)) updateField(group.key, undefined);
  };
  const magnetic = getMaterialField(entry, 'MagneticProperty');
  const hysteresis = getMaterialField(entry, 'MagneticProperty.HYSTERESIS');
  return <div className={styles.fieldSourceDetail}>
    <DetailHeading title={`Volume entry ${index + 1}`} onBack={onBack} />
    <div className={styles.fieldSourceDescription}><div><strong>Volume material</strong><p>Current analysis defaults are applied only to new rows; every documented subsection remains available.</p></div><a href={MATERIAL_DOCUMENTATION.volume} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a></div>
    <div className={styles.fieldSourceFieldGrid}>{VOLUME_BASE_FIELDS.map((field) => <MaterialInput key={field.key} field={field} value={entry[field.key]} onChange={(value) => updateField(field.key, value)} />)}</div>
    <div className={styles.materialGroupGrid}>
      <OptionalGroup groupKey="conductivity" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField}>
        <OptionalGroup groupKey="sigmaXyz" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField} compact />
      </OptionalGroup>
      <OptionalGroup groupKey="permittivity" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField}>
        <OptionalGroup groupKey="epsXyz" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField} compact />
      </OptionalGroup>
      <OptionalGroup groupKey="magnetic" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField}>
        {isPlainRecord(magnetic) && <div className={styles.materialInlineOptional}>
          <label className={styles.networkField}><span>Temperature-dependent B-H curve<em>TEMP_DEPEND_BH_CURVE_ID</em></span><input aria-label="Temperature-dependent B-H curve (TEMP_DEPEND_BH_CURVE_ID)" type="number" step="1" placeholder="Not set" value={inputValue(magnetic.TEMP_DEPEND_BH_CURVE_ID)} onChange={(event) => updateField('MagneticProperty.TEMP_DEPEND_BH_CURVE_ID', event.target.value === '' ? undefined : numberValue(event.target.value))} /><small>Optional temperature-dependent magnetic-curve identifier.</small></label>
        </div>}
      </OptionalGroup>
      {isPlainRecord(magnetic) && ['muXyz', 'packing', 'bhCurveXyz', 'anisotropy2d', 'hysteresis', 'muComplex', 'ironLoss'].map((key) => (
        <OptionalGroup key={key} groupKey={key} entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField}>
          {key === 'hysteresis' && isPlainRecord(hysteresis) && <div className={styles.materialNestedGroups}>
            <OptionalGroup groupKey="jaModel" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField} compact />
            <OptionalGroup groupKey="playModel" entry={entry} onAdd={addGroup} onRemove={removeGroup} onField={updateField} compact />
          </div>}
        </OptionalGroup>
      ))}
    </div>
    <section className={styles.fieldSourceRows}><div className={styles.fieldSourceRowsHeading}><div><h4>Optional material flags</h4><p>Choose Not set to remove an optional flag without changing other properties.</p></div></div>
      <div className={styles.fieldSourceFieldGrid}>{VOLUME_FLAG_FIELDS.map((field) => <MaterialInput key={field.key} field={field} value={entry[field.key]} onChange={(value) => updateField(field.key, value)} />)}</div>
    </section>
    <ValidationIssues label="Volume material validation issues" issues={issues} />
  </div>;
}

function SurfaceDetail({entry, index, issues, onBack, onChange}: {
  entry: unknown;
  index: number;
  issues: MaterialPropertyValidationIssue[];
  onBack: () => void;
  onChange: (entry: unknown) => void;
}): ReactNode {
  const inspected = inspectSurfaceMaterial(entry);
  if (inspected.kind !== 'known' || !isPlainRecord(inspected.definition)) return <RawDetail title={`Surface entry ${index + 1} · Raw JSON`} label="Raw surface material JSON" value={entry} issues={issues} onBack={onBack} onSave={onChange} />;
  const wrapper = inspected.wrapper;
  const definition = inspected.definition;
  const updateWrapper = (path: string, value: unknown) => { const next = deepClone(wrapper); value === undefined ? removeMaterialField(next, path) : setMaterialField(next, path, value); onChange(next); };
  const changeType = (type: SurfaceMaterialType) => {
    if (type === inspected.type) return;
    if (!window.confirm(`Replace surface material ${index + 1} with a new ${type} definition? Existing type-specific values will be discarded.`)) return;
    const replacement = createSurfaceMaterial(type);
    replacement.SMAT_ID = wrapper.SMAT_ID;
    for (const [key, value] of Object.entries(wrapper)) if (key !== inspected.type && key !== 'SMAT_ID') replacement[key] = deepClone(value);
    onChange(replacement);
  };
  const nonlinearKey = nonlinearParametersKey(definition);
  const nonlinear = definition[nonlinearKey];
  return <div className={styles.fieldSourceDetail}>
    <DetailHeading title={`Surface entry ${index + 1} · ${inspected.type}`} onBack={onBack}>
      <label>Change type<select aria-label="Surface material type" value={inspected.type} onChange={(event) => changeType(event.target.value as SurfaceMaterialType)}>{SURFACE_MATERIAL_TYPES.map((type) => <option key={type}>{type}</option>)}</select></label>
    </DetailHeading>
    <div className={styles.fieldSourceDescription}><div><strong>{SURFACE_MATERIAL_SCHEMAS[inspected.type].label}</strong><p>{SURFACE_MATERIAL_SCHEMAS[inspected.type].description}</p></div><a href={MATERIAL_DOCUMENTATION.surface} target="_blank" rel="noreferrer">Official documentation <EditorIcon name="external" /></a></div>
    <div className={styles.fieldSourceFieldGrid}>
      <MaterialInput field={{key: 'SMAT_ID', label: 'Surface material ID', kind: 'integer', help: 'Surface-element material identifier.', required: true}} value={wrapper.SMAT_ID} onChange={(value) => updateWrapper('SMAT_ID', value)} />
      {SURFACE_MATERIAL_SCHEMAS[inspected.type].fields.map((field) => <MaterialInput key={field.key} field={field} value={definition[field.key]} onChange={(value) => updateWrapper(`${inspected.type}.${field.key}`, value)} />)}
    </div>
    {inspected.type === 'SURFACE_IMPEDANCE' && <section className={styles.fieldSourceRows}>
      <div className={styles.fieldSourceRowsHeading}><div><h4>Nonlinear impedance</h4><p>Required for IMP_TYPE 1 through 4. The original supported spelling is retained.</p></div>
        {nonlinear === undefined ? <button type="button" className="button button--secondary button--sm" onClick={() => updateWrapper(`${inspected.type}.${nonlinearKey}`, {BH_CURVE_ID: 1, AGRWALL: 0.75, K: 5, HK: 2000})}><EditorIcon name="add" /> Add parameters</button>
          : <button type="button" className="button button--secondary button--sm" onClick={() => { if (window.confirm('Remove nonlinear impedance parameters and all of their values?')) updateWrapper(`${inspected.type}.${nonlinearKey}`, undefined); }}><EditorIcon name="delete" /> Remove parameters</button>}</div>
      {isPlainRecord(nonlinear) && <div className={styles.fieldSourceFieldGrid}>{NONLINEAR_IMPEDANCE_FIELDS.map((field) => <MaterialInput key={field.key} field={field} value={nonlinear[field.key]} onChange={(value) => updateWrapper(`${inspected.type}.${nonlinearKey}.${field.key}`, value)} />)}</div>}
    </section>}
    {inspected.type === 'THIN_CONDUCTOR' && <SurfaceAnisotropy definition={definition} onChange={(path, value) => updateWrapper(`${inspected.type}.${path}`, value)} />}
    <ValidationIssues label="Surface material validation issues" issues={issues} />
  </div>;
}

function SurfaceAnisotropy({definition, onChange}: {definition: Record<string, unknown>; onChange: (path: string, value: unknown) => void}): ReactNode {
  const group = MATERIAL_FIELD_GROUPS.sigmaXyz;
  const value = definition.SIGMA_XYZ;
  return <section className={styles.fieldSourceRows}><div className={styles.fieldSourceRowsHeading}><div><h4>Anisotropic conductivity</h4><p>Optional local-coordinate conductivity factors.</p></div>
    {value === undefined ? <button type="button" className="button button--secondary button--sm" onClick={() => onChange('SIGMA_XYZ', deepClone(GROUP_DEFAULTS.sigmaXyz))}><EditorIcon name="add" /> Add anisotropy</button>
      : <button type="button" className="button button--secondary button--sm" onClick={() => { if (window.confirm('Remove anisotropic conductivity and all of its values?')) onChange('SIGMA_XYZ', undefined); }}><EditorIcon name="delete" /> Remove anisotropy</button>}</div>
    {isPlainRecord(value) && <div className={styles.fieldSourceFieldGrid}>{group.fields.map((field) => <MaterialInput key={field.key} field={field} value={value[field.key]} onChange={(next) => onChange(`SIGMA_XYZ.${field.key}`, next)} />)}</div>}
  </section>;
}

function OptionalGroup({groupKey, entry, onAdd, onRemove, onField, compact, children}: {
  groupKey: string;
  entry: Record<string, unknown>;
  onAdd: (key: string) => void;
  onRemove: (key: string) => void;
  onField: (path: string, value: unknown) => void;
  compact?: boolean;
  children?: ReactNode;
}): ReactNode {
  const group = MATERIAL_FIELD_GROUPS[groupKey];
  const value = getMaterialField(entry, group.key);
  return <section className={`${styles.materialGroupCard} ${compact ? styles.materialGroupCompact : ''}`}>
    <div className={styles.materialGroupHeader}><div><h4>{group.label}</h4><p>{group.description}</p></div>
      {value === undefined ? <button type="button" className="button button--secondary button--sm" aria-label={`Add ${group.label}`} onClick={() => onAdd(groupKey)}><EditorIcon name="add" /> Add</button>
        : <button type="button" className="button button--secondary button--sm" aria-label={`Remove ${group.label}`} onClick={() => onRemove(groupKey)}><EditorIcon name="delete" /> Remove</button>}</div>
    {isPlainRecord(value) && <><div className={styles.fieldSourceFieldGrid}>{group.fields.map((field) => <MaterialInput key={field.key} field={field} value={value[field.key]} onChange={(next) => onField(`${group.key}.${field.key}`, next)} />)}</div>{children}</>}
  </section>;
}

function MaterialInput({field, value, onChange}: {field: MaterialFieldDefinition; value: unknown; onChange: (value: unknown) => void}): ReactNode {
  const label = `${field.label} (${field.key})`;
  if (field.kind === 'vector3') {
    const values = Array.isArray(value) ? value : ['', '', ''];
    return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span><div className={styles.fieldSourceVector}>{['X', 'Y', 'Z'].map((axis, index) => <input key={axis} aria-label={`${label} ${axis}`} type="number" step="any" value={inputValue(values[index])} onChange={(event) => { const next = [...values]; next[index] = numberValue(event.target.value); onChange(next); }} />)}</div><small>{field.help}</small></label>;
  }
  if (field.kind === 'integer-array' || field.kind === 'number-array') return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span><input aria-label={label} type="text" value={arrayText(value)} placeholder="Comma-separated values" onChange={(event) => onChange(arrayValue(event.target.value))} /><small>{field.help}</small></label>;
  if (field.kind === 'enum') return <label className={styles.networkField}><span>{field.label}<em>{field.key}</em></span><select aria-label={label} value={inputValue(value)} onChange={(event) => onChange(event.target.value === '' ? undefined : Number(event.target.value))}>{!field.required && <option value="">Not set</option>}{field.options?.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select><small>{field.help}</small></label>;
  return <label className={styles.networkField}><span>{field.label}<em>{field.key}{field.unit ? ` · ${field.unit}` : ''}</em></span><input aria-label={label} type={field.kind === 'string' ? 'text' : 'number'} step={field.kind === 'integer' ? '1' : 'any'} value={inputValue(value)} placeholder={!field.required ? 'Not set' : undefined} onChange={(event) => {
    if (!field.required && event.target.value === '') onChange(undefined);
    else onChange(field.kind === 'string' ? event.target.value : numberValue(event.target.value));
  }} /><small>{field.help}</small></label>;
}

function DetailHeading({title, onBack, children}: {title: string; onBack: () => void; children?: ReactNode}): ReactNode {
  return <div className={styles.fieldSourceDetailHeading}><button type="button" className="button button--secondary button--sm" onClick={onBack}><EditorIcon name="up" /> Back to materials</button><h3>{title}</h3>{children ?? <span />}</div>;
}

function RawDetail({title, label, value, issues, onBack, onSave}: {title: string; label: string; value: unknown; issues: MaterialPropertyValidationIssue[]; onBack: () => void; onSave: (value: unknown) => void}): ReactNode {
  return <div className={styles.fieldSourceDetail}><DetailHeading title={title} onBack={onBack} /><RawJsonEditor label={label} value={value} onSave={onSave} /><ValidationIssues label="Material validation issues" issues={issues} /></div>;
}

function RawJsonEditor({label, value, onSave}: {label: string; value: unknown; onSave: (value: unknown) => void}): ReactNode {
  const [text, setText] = useState(JSON.stringify(value, null, 2));
  const [error, setError] = useState('');
  return <div className={styles.fieldSourceRawEditor}><textarea aria-label={label} rows={16} value={text} onChange={(event) => { setText(event.target.value); setError(''); }} />{error && <div className={styles.networkInlineError}>{error}</div>}
    <div className={styles.networkEditorButtons}><button type="button" className="button button--primary button--sm" onClick={() => { try { const parsed = JSON.parse(text); if (!isPlainRecord(parsed)) { setError('Value must be a JSON object.'); return; } onSave(parsed); } catch (caught) { setError(caught instanceof Error ? caught.message : 'Invalid JSON.'); } }}><EditorIcon name="save" /> Save raw JSON</button></div>
  </div>;
}

function StatusSelect({label, value, onChange}: {label: string; value: StatusFilter; onChange: (value: StatusFilter) => void}): ReactNode {
  return <select aria-label={label} value={value} onChange={(event) => onChange(event.target.value as StatusFilter)}><option value="ALL">All statuses</option><option value="VALID">Valid</option><option value="WARNING">Warnings</option><option value="ERROR">Errors</option></select>;
}

function StatusBadge({issues}: {issues: MaterialPropertyValidationIssue[]}): ReactNode {
  const errors = issues.filter((issue) => issue.severity === 'error').length;
  const warnings = issues.filter((issue) => issue.severity === 'warning').length;
  return errors > 0 ? <span className={styles.networkErrorBadge}>{errors} error{errors === 1 ? '' : 's'}</span>
    : warnings > 0 ? <span className={styles.networkWarningBadge}>{warnings} warning{warnings === 1 ? '' : 's'}</span>
      : <span className={styles.networkValidBadge}>Valid</span>;
}

function RowActions({label, index, count, onEdit, onDuplicate, onMove, onDelete}: {label: string; index: number; count: number; onEdit: () => void; onDuplicate: () => void; onMove: (direction: -1 | 1) => void; onDelete: () => void}): ReactNode {
  return <div className={styles.networkRowActions}><button type="button" aria-label={`Edit ${label} row ${index + 1}`} onClick={onEdit}><EditorIcon name="edit" /></button><button type="button" aria-label={`Duplicate ${label} row ${index + 1}`} onClick={onDuplicate}><EditorIcon name="copy" /></button><button type="button" aria-label={`Move ${label} row ${index + 1} up`} disabled={index === 0} onClick={() => onMove(-1)}><EditorIcon name="up" /></button><button type="button" aria-label={`Move ${label} row ${index + 1} down`} disabled={index === count - 1} onClick={() => onMove(1)}><EditorIcon name="down" /></button><button type="button" className={styles.networkDangerButton} aria-label={`Delete ${label} row ${index + 1}`} onClick={onDelete}><EditorIcon name="delete" /></button></div>;
}

function moveEntry(entries: unknown[], index: number, direction: -1 | 1, onEntries: (entries: unknown[]) => void): void {
  const target = index + direction;
  if (target < 0 || target >= entries.length) return;
  const next = [...entries]; [next[index], next[target]] = [next[target], next[index]]; onEntries(next);
}

function ValidationIssues({label, issues}: {label: string; issues: MaterialPropertyValidationIssue[]}): ReactNode {
  if (issues.length === 0) return null;
  return <section className={styles.networkIssues} aria-label={label}><h3>Validation</h3><ul>{issues.map((issue, index) => <li key={`${issue.path}:${index}`} className={issue.severity === 'error' ? styles.networkIssueError : styles.networkIssueWarning}><strong>{issue.path}</strong>: {issue.message}</li>)}</ul></section>;
}
