import React, {useEffect} from 'react';
import {fireEvent, render, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

import InputControlFileEditorClient from './InputControlFileEditorClient';

vi.mock('@docusaurus/theme-common', () => ({
  useColorMode: () => ({colorMode: 'light'}),
}));

const disposedModels = new Set<string>();
let fullscreenElement: Element | null = null;

vi.mock('monaco-editor', () => ({}));

vi.mock('@monaco-editor/react', () => ({
  loader: {config: vi.fn()},
  default: (props: Record<string, any>) => {
    useEffect(() => {
      const model = {
        getOffsetAt: () => 0,
        getPositionAt: () => ({lineNumber: 1, column: 1}),
      };
      const editor = {
        getModel: () => model,
        getPosition: () => ({lineNumber: 1, column: 1}),
        getAction: () => ({run: vi.fn()}),
        onDidChangeCursorPosition: vi.fn(),
        onDidChangeModel: vi.fn(),
        onDidFocusEditorText: vi.fn(),
        setPosition: vi.fn(),
        revealPositionInCenter: vi.fn(),
        focus: vi.fn(),
      };
      const monaco = {
        Uri: {parse: (value: string) => value},
        editor: {
          getModel: (value: string) => ({dispose: () => disposedModels.add(value)}),
          setModelMarkers: vi.fn(),
        },
        MarkerSeverity: {Error: 8},
        languages: {
          getLanguages: vi.fn(() => [{id: 'json'}, {id: 'yaml'}]),
          register: vi.fn(),
          setLanguageConfiguration: vi.fn(),
          setMonarchTokensProvider: vi.fn(),
          json: {jsonDefaults: {setDiagnosticsOptions: vi.fn()}},
        },
      };
      props.onMount?.(editor, monaco);
    }, []);

    return React.createElement('textarea', {
      'aria-label': `Monaco ${props.path}`,
      'data-occurrences-highlight': props.options?.occurrencesHighlight,
      value: props.value,
      onFocus: () => undefined,
      onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        props.onChange?.(event.target.value);
        try {
          JSON.parse(event.target.value);
          props.onValidate?.([]);
        } catch {
          props.onValidate?.([{}]);
        }
      },
    });
  },
}));

function jsonFile(name: string, content: string, lastModified = 1): File {
  const file = new File([content], name, {type: 'application/json', lastModified});
  Object.defineProperty(file, 'text', {value: async () => content});
  return file;
}

function emsolutionInput(networkData: unknown[] = [
  {type: 'FEM', ID: 1, START: 1, END: 2, SERIES_ID: 1},
  {type: 'CPS', ID: 2, START: 2, END: 9999, TIME_ID: 1},
  {type: 'R', ID: 3, START: 9999, END: 1, RESISTANCE: 1_000_000},
]): string {
  return JSON.stringify({
    metaData: {type: 'EMSolution_Input', version: '1.0'},
    '0_Release_Number': {RLS_NO: 'r6.6'},
    '1_Execution_Control': {},
    '2_Analysis_Type': {STATIC: 0, AC: 0, TRANSIENT: 1},
    '17_Field_Source': [
      {PHICOIL: {SERIES_ID: 1, IN_ROTOR: 0, data: []}},
      {NETWORK: {REGION_FACTOR: 8, REGION_PARALLEL: 1, data: networkData}},
    ],
    '18_Time_Function': [{TIME_ID: 1, OPTION: 2}],
  });
}

function emsolutionCircuitInput(circuit: Record<string, unknown> = {
  REGION_FACTOR: 8,
  REGION_PARALLEL: 1,
  SERIES_IDS: [1],
  INDUCTANCE_MATRIX: {comment: 'keep', IN_IND: 0, MATRIX: [[0]]},
  RESISTANCE_MATRIX: {format: 'keep', IN_RES: 0, MATRIX: [[5]]},
  CONNECTION_MATRIX: {IN_CON: 0, MATRIX: [[1]]},
  POWER_SUPPLIES: [{PS_ID: 1, TYPE: 1, TIME_ID: 1, INITIAL_CURRENT: 0, vendor: 'keep'}],
}): string {
  return JSON.stringify({
    metaData: {type: 'EMSolution_Input', version: '1.0'},
    '0_Release_Number': {RLS_NO: 'r6.6'},
    '1_Execution_Control': {},
    '2_Analysis_Type': {STATIC: 0, AC: 0, TRANSIENT: 1},
    '17_Field_Source': [
      {ELMCUR: {SERIES_ID: 1, OPTION: 1, IN_ROTOR: 0, data: []}},
      {CIRCUIT: circuit},
    ],
    '18_Time_Function': [{TIME_ID: 1, OPTION: 2}],
  });
}

async function chooseFiles(container: HTMLElement, files: File[]): Promise<void> {
  const input = container.querySelector<HTMLInputElement>('input[type="file"]');
  if (!input) throw new Error('File input was not rendered');
  fireEvent.change(input, {target: {files}});
  await waitFor(() => expect(screen.getAllByRole('tab')).toHaveLength(files.length));
}

async function openFieldSourceEditor(): Promise<HTMLElement> {
  await userEvent.click(screen.getByRole('button', {name: 'Edit Field Sources'}));
  return screen.getByRole('dialog', {name: 'Field Source editor'});
}

async function openMaterialPropertyEditor(): Promise<HTMLElement> {
  await userEvent.click(screen.getByRole('button', {name: 'Edit Material Properties'}));
  return screen.getByRole('dialog', {name: 'Material Properties editor'});
}

async function openTimeFunctionEditor(): Promise<HTMLElement> {
  await userEvent.click(screen.getByRole('button', {name: 'Edit Time Functions'}));
  return screen.getByRole('dialog', {name: 'Time Function editor'});
}

async function openSpecialSourceEditor(type: 'NETWORK' | 'CIRCUIT', row = 2): Promise<{dialog: HTMLElement; editor: HTMLElement}> {
  const dialog = await openFieldSourceEditor();
  await userEvent.click(within(dialog).getByRole('button', {name: `Edit Field Source row ${row}`}));
  return {dialog, editor: within(dialog).getByRole('region', {name: `${type} editor`})};
}

async function applySpecialSourceEditor(dialog: HTMLElement, editor: HTMLElement): Promise<void> {
  await userEvent.click(within(editor).getByRole('button', {name: 'Apply changes'}));
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));
}

describe('InputControlFileEditorClient', () => {
  beforeEach(() => {
    disposedModels.clear();
    fullscreenElement = null;
    document.title = 'Original title';
    Object.defineProperty(window, 'showOpenFilePicker', {value: undefined, configurable: true});
    Object.defineProperty(URL, 'createObjectURL', {value: vi.fn(() => 'blob:test'), configurable: true});
    Object.defineProperty(URL, 'revokeObjectURL', {value: vi.fn(), configurable: true});
    Object.defineProperty(document, 'fullscreenElement', {
      configurable: true,
      get: () => fullscreenElement,
    });
    Object.defineProperty(HTMLElement.prototype, 'requestFullscreen', {
      configurable: true,
      value: vi.fn(async function requestFullscreen(this: HTMLElement) {
        fullscreenElement = this;
        document.dispatchEvent(new Event('fullscreenchange'));
      }),
    });
    Object.defineProperty(document, 'exitFullscreen', {
      configurable: true,
      value: vi.fn(async () => {
        fullscreenElement = null;
        document.dispatchEvent(new Event('fullscreenchange'));
      }),
    });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows a conventional drop target with a single prompt during dragging', () => {
    const {container} = render(<InputControlFileEditorClient />);

    expect(screen.queryByRole('heading', {name: 'Open input control files'})).not.toBeInTheDocument();
    expect(screen.getByText('Drag and drop one or more JSON files here.')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Open Input Control Files'})).toBeInTheDocument();

    fireEvent.dragEnter(container.querySelector('section')!);

    expect(screen.queryByText('Drag and drop one or more JSON files here.')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', {name: 'Open Input Control Files'})).not.toBeInTheDocument();
    expect(screen.getAllByText('Drop JSON files to open them')).toHaveLength(1);
  });

  it('disables Monaco occurrence highlighting to avoid model-switch cancellation errors', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('first.json', '{}')]);

    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveAttribute(
      'data-occurrences-highlight',
      'off',
    );

    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [jsonFile('second.json', '{}')]}});

    expect(await screen.findByRole('tab', {name: 'second.json'})).toBeInTheDocument();
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveAttribute(
      'data-occurrences-highlight',
      'off',
    );
  });

  it('opens multiple files, disambiguates names, and creates a split title', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [
      jsonFile('input.json', '{"value": 1}', 10),
      jsonFile('input.json', '{"value": 2}', 20),
    ]);

    expect(screen.getByRole('tab', {name: 'input.json'})).toBeInTheDocument();
    expect(screen.getByRole('tab', {name: 'input.json (2)'})).toHaveAttribute(
      'title',
      expect.stringContaining('The browser does not expose the source path.'),
    );
    expect(document.title).toBe('input.json — Input Control File Editor | pyemsi');

    await userEvent.selectOptions(screen.getByLabelText('Split editor with'), screen.getByRole('option', {name: 'input.json (2)'}));
    expect(await screen.findByLabelText('Comparison editor')).toBeInTheDocument();
    expect(document.title).toBe('input.json ↔ input.json (2) — Input Control File Editor | pyemsi');
    expect(screen.getAllByRole('button', {name: 'Format'})).toHaveLength(1);
    expect(screen.getAllByRole('button', {name: 'Save'})).toHaveLength(1);

    fireEvent.change(
      within(screen.getByLabelText('Comparison editor')).getByRole('textbox', {name: /Monaco/}),
      {target: {value: '{"value": 3}'}},
    );
    await userEvent.click(screen.getByRole('button', {name: 'Save'}));
    expect(await screen.findByText('Downloaded input.json (2).')).toBeInTheDocument();
  });

  it('tracks dirty state, validates, downloads, and clears the modified marker', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('input.json', '{"value": 1}')]);

    const textarea = screen.getByRole('textbox', {name: /Monaco/});
    fireEvent.change(textarea, {target: {value: '{"value": }'}});
    expect(screen.getByLabelText('Modified')).toBeInTheDocument();
    expect(await screen.findByText('1 JSON problem')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Format'})).toBeDisabled();

    fireEvent.click(screen.getByRole('button', {name: 'Save'}));
    await waitFor(() => expect(screen.queryByLabelText('Modified')).not.toBeInTheDocument());
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(screen.getByText('Downloaded input.json.')).toBeInTheDocument();
  });

  it('writes through a retained file handle and closes dirty files only after confirmation', async () => {
    const writable = {write: vi.fn(async () => undefined), close: vi.fn(async () => undefined)};
    const handle = {
      kind: 'file',
      name: 'picked.json',
      getFile: vi.fn(async () => jsonFile('picked.json', '{"picked": true}')),
      createWritable: vi.fn(async () => writable),
    };
    Object.defineProperty(window, 'showOpenFilePicker', {
      value: vi.fn(async () => [handle]),
      configurable: true,
    });
    render(<InputControlFileEditorClient />);

    await userEvent.click(screen.getByRole('button', {name: 'Open Input Control Files'}));
    expect(await screen.findByRole('tab', {name: 'picked.json'})).toBeInTheDocument();
    fireEvent.change(screen.getByRole('textbox', {name: /Monaco/}), {target: {value: '{"picked": false}'}});
    await userEvent.click(screen.getByRole('button', {name: 'Save'}));
    await waitFor(() => expect(writable.write).toHaveBeenCalledWith('{"picked": false}'));

    fireEvent.change(screen.getByRole('textbox', {name: /Monaco/}), {target: {value: '{"picked": null}'}});
    const confirm = vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true);
    await userEvent.click(screen.getByRole('button', {name: 'Close picked.json'}));
    expect(screen.getByRole('tab', {name: /^picked\.json/})).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', {name: 'Close picked.json'}));
    expect(screen.queryByRole('tab', {name: /^picked\.json/})).not.toBeInTheDocument();
    expect(confirm).toHaveBeenCalledTimes(2);
    expect(disposedModels.size).toBe(1);
  });

  it('rejects non-JSON files while opening valid dropped selections', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [
      jsonFile('valid.json', '{}'),
      new File(['hello'], 'notes.txt', {type: 'text/plain'}),
    ]}});

    expect(await screen.findByRole('tab', {name: 'valid.json'})).toBeInTheDocument();
    expect(screen.getByText(/Rejected notes\.txt/)).toBeInTheDocument();
    expect(within(screen.getByLabelText('Primary editor')).getByText('Valid JSON')).toBeInTheDocument();
  });

  it('enters and exits fullscreen mode', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('input.json', '{"first": 1, "second": 2}')]);

    await userEvent.click(screen.getByRole('button', {name: 'Fullscreen'}));
    expect(HTMLElement.prototype.requestFullscreen).toHaveBeenCalledOnce();
    expect(screen.getByRole('button', {name: 'Exit fullscreen'})).toHaveAttribute('aria-pressed', 'true');

    await userEvent.click(screen.getByRole('button', {name: '…'}));
    const menu = screen.getByRole('menu', {name: '… entries'});
    expect(menu.parentElement).toBe(fullscreenElement);
    expect(within(menu).getByRole('menuitem', {name: /first/})).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', {name: 'Exit fullscreen'}));
    expect(document.exitFullscreen).toHaveBeenCalledOnce();
    expect(screen.getByRole('button', {name: 'Fullscreen'})).toHaveAttribute('aria-pressed', 'false');
    expect(screen.queryByRole('menu', {name: '… entries'})).not.toBeInTheDocument();
  });

  it('edits YAML and saves the converted canonical JSON', async () => {
    const writable = {write: vi.fn(async () => undefined), close: vi.fn(async () => undefined)};
    const handle = {
      kind: 'file',
      name: 'picked.json',
      getFile: vi.fn(async () => jsonFile('picked.json', '{"picked": true}')),
      createWritable: vi.fn(async () => writable),
    };
    Object.defineProperty(window, 'showOpenFilePicker', {
      value: vi.fn(async () => [handle]),
      configurable: true,
    });
    render(<InputControlFileEditorClient />);

    await userEvent.click(screen.getByRole('button', {name: 'Open Input Control Files'}));
    const pane = await screen.findByLabelText('Primary editor');
    await userEvent.click(within(pane).getByRole('button', {name: 'YAML'}));
    const textarea = within(pane).getByRole('textbox', {name: /Monaco/});
    await waitFor(() => expect((textarea as HTMLTextAreaElement).value).toContain('picked: true'));

    fireEvent.change(textarea, {target: {value: 'picked: false\nnested:\n  count: 2\n'}});
    const saveButton = screen.getByRole('button', {name: 'Save'});
    expect(saveButton).toBeDisabled();
    await waitFor(() => expect(screen.getByLabelText('Modified')).toBeInTheDocument());
    expect(within(pane).getByText('Valid YAML. Comments are not saved to JSON.')).toBeInTheDocument();
    await waitFor(() => expect(saveButton).toBeEnabled());
    await userEvent.click(saveButton);

    await waitFor(() => expect(writable.write).toHaveBeenCalledWith(
      '{\n  "picked": false,\n  "nested": {\n    "count": 2\n  }\n}\n',
    ));
  });

  it('blocks invalid YAML switching and saving until the draft is discarded', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('input.json', '{"value": 1}')]);
    const pane = screen.getByLabelText('Primary editor');
    await userEvent.click(within(pane).getByRole('button', {name: 'YAML'}));
    const textarea = within(pane).getByRole('textbox', {name: /Monaco/});
    fireEvent.change(textarea, {target: {value: 'value: [\n'}});

    expect(await within(pane).findByText('1 YAML problem')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Save'})).toBeDisabled();
    expect(within(pane).getByRole('button', {name: 'JSON'})).toBeDisabled();
    expect(within(pane).getByRole('button', {name: 'TOML'})).toBeDisabled();

    await userEvent.click(within(pane).getByRole('button', {name: 'Discard invalid changes'}));
    expect(await within(pane).findByText('Valid YAML. Comments are not saved to JSON.')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Save'})).toBeEnabled();
  });

  it('disables TOML without losing incompatible JSON values', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('input.json', '{"solver": {"value": null}}')]);
    const tomlButton = within(screen.getByLabelText('Primary editor')).getByRole('button', {name: 'TOML'});

    expect(tomlButton).toBeDisabled();
    expect(tomlButton).toHaveAttribute('title', expect.stringContaining('$.solver.value'));
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveValue('{"solver": {"value": null}}');
  });

  it('keeps format selection independent across split panes', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [
      jsonFile('primary.json', '{"value": 1}'),
      jsonFile('comparison.json', '{"value": 2}'),
    ]);
    const primary = screen.getByLabelText('Primary editor');
    await userEvent.click(within(primary).getByRole('button', {name: 'YAML'}));
    await userEvent.selectOptions(
      screen.getByLabelText('Split editor with'),
      screen.getByRole('option', {name: 'comparison.json'}),
    );
    const comparison = await screen.findByLabelText('Comparison editor');
    await userEvent.click(within(comparison).getByRole('button', {name: 'TOML'}));

    expect(within(primary).getByRole('button', {name: 'YAML'})).toHaveAttribute('aria-pressed', 'true');
    expect(within(comparison).getByRole('button', {name: 'TOML'})).toHaveAttribute('aria-pressed', 'true');
    expect((within(primary).getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value).toContain('value: 1');
    expect((within(comparison).getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value).toContain('value = 2');
  });

  it('shows the Field Source action only for recognized EMSolution inputs', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('generic.json', '{"NETWORK": {"data": []}}')]);
    expect(screen.queryByRole('button', {name: 'Edit Field Sources'})).not.toBeInTheDocument();

    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [jsonFile('transient.json', emsolutionInput())]}});
    expect(await screen.findByRole('button', {name: 'Edit Field Sources'})).toBeInTheDocument();
    const {editor} = await openSpecialSourceEditor('NETWORK');
    expect(within(editor).getByText('FEM source')).toBeInTheDocument();
    expect(within(editor).getByText('Current source')).toBeInTheDocument();
    expect(within(editor).getByText('Resistor')).toBeInTheDocument();
    expect(within(editor).getByRole('link', {name: 'Official documentation'})).toHaveAttribute('href', expect.stringContaining('17_9_NETWORK'));
    fireEvent.keyDown(document, {key: 'Escape'});
    expect(within(screen.getByRole('dialog', {name: 'Field Source editor'})).queryByRole('region', {name: 'NETWORK editor'})).not.toBeInTheDocument();
  });

  it('applies staged NETWORK row edits through the canonical document', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('transient.json', emsolutionInput())]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK');

    await userEvent.click(within(editor).getByRole('button', {name: 'Edit NETWORK row 3'}));
    fireEvent.change(within(editor).getByLabelText('Resistance'), {target: {value: '42.5'}});
    await userEvent.click(within(editor).getByRole('button', {name: 'Save row'}));
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.data[2].RESISTANCE).toBe(42.5);
    expect(screen.getByLabelText('Modified')).toBeInTheDocument();
    expect(screen.getByText('Applied Field Source changes to the open document. Save the file to keep them.')).toBeInTheDocument();
  });

  it('discards staged NETWORK changes when the modal is cancelled', async () => {
    const original = emsolutionInput();
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('transient.json', original)]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK');
    fireEvent.change(within(editor).getByLabelText('Region factor'), {target: {value: '4'}});
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(editor).getByRole('button', {name: 'Cancel'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));

    expect(screen.queryByRole('dialog', {name: 'Field Source editor'})).not.toBeInTheDocument();
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveValue(original);
    expect(screen.queryByLabelText('Modified')).not.toBeInTheDocument();
  });

  it('adds and derives counts for a TABLE dataset', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('transient.json', emsolutionInput())]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK');
    await userEvent.selectOptions(within(editor).getByLabelText('New NETWORK component type'), 'TABLE');
    await userEvent.click(within(editor).getByRole('button', {name: 'Add component'}));
    await userEvent.click(within(editor).getByRole('button', {name: 'Add dataset'}));
    await userEvent.click(within(editor).getByRole('button', {name: 'Add I–V point'}));
    fireEvent.change(within(editor).getByLabelText('Table 1 current 1'), {target: {value: '2'}});
    fireEvent.change(within(editor).getByLabelText('Table 1 voltage 1'), {target: {value: '0.7'}});
    await userEvent.click(within(editor).getByRole('button', {name: 'Save row'}));
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    const table = savedValue['17_Field_Source'][1].NETWORK.data[3];
    expect(table).toMatchObject({type: 'TABLE', NUMBER: 1});
    expect(table.data[0]).toMatchObject({NO_DATA: 1, CURRENT: [2], VOLTAGE: [0.7]});
  });

  it('preserves unknown NETWORK properties through raw editing', async () => {
    const unknown = {type: 'FUTURE', ID: 77, vendor: {flag: true}};
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('future.json', emsolutionInput([unknown]))]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK');
    await userEvent.click(within(editor).getByRole('button', {name: 'Edit NETWORK row 1'}));
    const raw = within(editor).getByLabelText('Raw NETWORK component JSON');
    fireEvent.change(raw, {target: {value: JSON.stringify({...unknown, added: 'kept'})}});
    await userEvent.click(within(editor).getByRole('button', {name: 'Save row'}));
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.data[0]).toEqual({...unknown, added: 'kept'});
  });

  it('adds a SWITCH with paired timings and phase-aware fields', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('switch.json', emsolutionInput())]);
    const {dialog, editor: networkEditor} = await openSpecialSourceEditor('NETWORK');
    await userEvent.selectOptions(within(networkEditor).getByLabelText('New NETWORK component type'), 'SWITCH');
    await userEvent.click(within(networkEditor).getByRole('button', {name: 'Add component'}));
    const editor = within(networkEditor).getByLabelText('SWITCH component editor');
    for (const [label, value] of [
      ['Start node', '1'], ['End node', '2'], ['On resistance', '0.01'],
      ['Off resistance', '1000000'], ['Cycle', '0.02'], ['Time function', '1'],
    ]) {
      fireEvent.change(within(editor).getByLabelText(label), {target: {value}});
    }
    await userEvent.selectOptions(within(editor).getByLabelText('Time mode'), '1');
    await userEvent.click(within(editor).getByRole('button', {name: 'Add interval'}));
    fireEvent.change(within(editor).getByLabelText('Switch on time 1'), {target: {value: '30'}});
    fireEvent.change(within(editor).getByLabelText('Switch off time 1'), {target: {value: '180'}});
    await userEvent.click(within(editor).getByRole('button', {name: 'Save row'}));
    await applySpecialSourceEditor(dialog, networkEditor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.data[3]).toMatchObject({
      type: 'SWITCH', ID: 4, START: 1, END: 2, PHASE_OP: 1,
      ON_TIME: [30], OFF_TIME: [180],
    });
  });

  it('duplicates, reorders, and deletes NETWORK rows', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('actions.json', emsolutionInput())]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK');
    await userEvent.click(within(editor).getByRole('button', {name: 'Duplicate NETWORK row 3'}));
    await userEvent.click(within(editor).getByRole('button', {name: 'Move NETWORK row 4 up'}));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(editor).getByRole('button', {name: 'Delete NETWORK row 1'}));
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    const data = savedValue['17_Field_Source'][1].NETWORK.data;
    expect(data).toHaveLength(3);
    expect(data.map((item: {ID: number}) => item.ID)).toEqual([2, 4, 3]);
  });

  it('targets the focused split document and restores focus after Escape', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [
      jsonFile('generic.json', '{"value": 1}'),
      jsonFile('network.json', emsolutionInput()),
    ]);
    await userEvent.selectOptions(
      screen.getByLabelText('Split editor with'),
      screen.getByRole('option', {name: 'network.json'}),
    );
    const networkButton = await screen.findByRole('button', {name: 'Edit Field Sources'});
    await userEvent.click(networkButton);
    expect(screen.getByRole('dialog', {name: 'Field Source editor'})).toHaveTextContent('network.json');
    fireEvent.keyDown(document, {key: 'Escape'});
    expect(screen.queryByRole('dialog', {name: 'Field Source editor'})).not.toBeInTheDocument();
    expect(networkButton).toHaveFocus();
  });

  it('selects and updates one of multiple NETWORK occurrences', async () => {
    const payload = JSON.parse(emsolutionInput());
    payload['17_Field_Source'].push({NETWORK: {
      REGION_FACTOR: 2,
      REGION_PARALLEL: 1,
      data: [{type: 'R', ID: 10, START: 1, END: 2, RESISTANCE: 5}],
    }});
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('multiple.json', JSON.stringify(payload))]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK', 3);
    expect(within(editor).getByLabelText('NETWORK occurrence')).toHaveValue('1');
    fireEvent.change(within(editor).getByLabelText('Region factor'), {target: {value: '3'}});
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.REGION_FACTOR).toBe(8);
    expect(savedValue['17_Field_Source'][2].NETWORK.REGION_FACTOR).toBe(3);
  });

  it('shows Field Sources only for recognized EMSolution inputs and links CIRCUIT documentation', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('generic.json', JSON.stringify({CIRCUIT: {SERIES_IDS: []}}))]);
    expect(screen.queryByRole('button', {name: 'Edit Field Sources'})).not.toBeInTheDocument();

    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [jsonFile('circuit.json', emsolutionCircuitInput())]}});
    expect(await screen.findByRole('button', {name: 'Edit Field Sources'})).toBeInTheDocument();
    const {editor} = await openSpecialSourceEditor('CIRCUIT');
    expect(within(editor).getByText('Source series')).toBeInTheDocument();
    expect(within(editor).getByText('Power supplies')).toBeInTheDocument();
    expect(within(editor).getByRole('link', {name: 'Official documentation'})).toHaveAttribute('href', expect.stringContaining('17_8_CIRCUIT'));
  });

  it('applies staged CIRCUIT settings, matrix, and power-supply edits', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('circuit.json', emsolutionCircuitInput())]);
    const {dialog, editor} = await openSpecialSourceEditor('CIRCUIT');
    fireEvent.change(within(editor).getByLabelText('CIRCUIT region factor'), {target: {value: '4'}});
    fireEvent.change(within(editor).getByLabelText('External inductance row 1 column 1'), {target: {value: '0.25'}});
    fireEvent.change(within(editor).getByLabelText('Power supply 1 initial current'), {target: {value: '3'}});
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    const circuit = savedValue['17_Field_Source'][1].CIRCUIT;
    expect(circuit.REGION_FACTOR).toBe(4);
    expect(circuit.INDUCTANCE_MATRIX.MATRIX).toEqual([[0.25]]);
    expect(circuit.POWER_SUPPLIES[0]).toMatchObject({INITIAL_CURRENT: 3, vendor: 'keep'});
    expect(circuit.INDUCTANCE_MATRIX.comment).toBe('keep');
    expect(screen.getByText('Applied Field Source changes to the open document. Save the file to keep them.')).toBeInTheDocument();
    expect(screen.getByLabelText('Modified')).toBeInTheDocument();
  });

  it('resizes CIRCUIT matrices when adding a series and blocks Apply until new cells are complete', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('circuit.json', emsolutionCircuitInput())]);
    const {dialog, editor} = await openSpecialSourceEditor('CIRCUIT');
    await userEvent.click(within(editor).getByRole('button', {name: 'Add series'}));
    expect(within(editor).getByRole('button', {name: 'Apply changes'})).toBeDisabled();
    fireEvent.change(within(editor).getByLabelText('Series ID 2'), {target: {value: '2'}});
    for (const [label, value] of [
      ['External inductance row 2 column 1', '0.1'],
      ['External inductance row 2 column 2', '0.2'],
      ['External resistance row 2 column 1', '0'],
      ['External resistance row 2 column 2', '6'],
      ['Connection row 2 column 1', '1'],
    ]) fireEvent.change(within(editor).getByLabelText(label), {target: {value}});
    expect(within(editor).getByRole('button', {name: 'Apply changes'})).toBeEnabled();
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    const circuit = savedValue['17_Field_Source'][1].CIRCUIT;
    expect(circuit.SERIES_IDS).toEqual([1, 2]);
    expect(circuit.INDUCTANCE_MATRIX.MATRIX).toEqual([[0], [0.1, 0.2]]);
    expect(circuit.CONNECTION_MATRIX.MATRIX).toEqual([[1], [1]]);
  });

  it('duplicates power supplies, supports occurrence selection, and discards cancelled CIRCUIT edits', async () => {
    const payload = JSON.parse(emsolutionCircuitInput());
    payload['17_Field_Source'].push({CIRCUIT: {
      ...payload['17_Field_Source'][1].CIRCUIT,
      REGION_FACTOR: 2,
    }});
    const original = JSON.stringify(payload);
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('multiple-circuit.json', original)]);
    const {dialog, editor} = await openSpecialSourceEditor('CIRCUIT', 3);
    expect(within(editor).getByLabelText('CIRCUIT occurrence')).toHaveValue('1');
    await userEvent.click(within(editor).getByRole('button', {name: 'Duplicate power supply row 1'}));
    expect(within(editor).getByLabelText('Power supply 2 ID')).toHaveValue(2);
    expect(within(editor).getByLabelText('Connection row 1 column 2')).toHaveValue(1);
    fireEvent.change(within(editor).getByLabelText('CIRCUIT region factor'), {target: {value: '3'}});
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(editor).getByRole('button', {name: 'Cancel'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveValue(original);
    expect(screen.queryByLabelText('Modified')).not.toBeInTheDocument();
  });

  it('raw-edits malformed CIRCUIT data and targets the focused split document', async () => {
    const malformed = JSON.parse(emsolutionCircuitInput());
    malformed['17_Field_Source'][1].CIRCUIT = [];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [
      jsonFile('malformed.json', JSON.stringify(malformed)),
      jsonFile('focused-circuit.json', emsolutionCircuitInput()),
    ]);
    const malformedButton = screen.getByRole('button', {name: 'Edit Field Sources'});
    expect(malformedButton).toBeEnabled();
    await userEvent.click(malformedButton);
    let fieldDialog = screen.getByRole('dialog', {name: 'Field Source editor'});
    await userEvent.click(within(fieldDialog).getByRole('button', {name: 'Edit Field Source row 2'}));
    expect((within(fieldDialog).getByLabelText('Raw Field Source entry JSON') as HTMLTextAreaElement).value).toContain('"CIRCUIT"');
    await userEvent.click(within(fieldDialog).getByRole('button', {name: 'Cancel'}));

    await userEvent.selectOptions(
      screen.getByLabelText('Split editor with'),
      screen.getByRole('option', {name: 'focused-circuit.json'}),
    );
    const focusedButton = screen.getByRole('button', {name: 'Edit Field Sources'});
    expect(focusedButton).toBeEnabled();
    await userEvent.click(focusedButton);
    fieldDialog = screen.getByRole('dialog', {name: 'Field Source editor'});
    expect(fieldDialog).toHaveTextContent('focused-circuit.json');
    fireEvent.keyDown(document, {key: 'Escape'});
    expect(screen.queryByRole('dialog', {name: 'Field Source editor'})).not.toBeInTheDocument();
    expect(focusedButton).toHaveFocus();
  });

  it('creates a missing Field Source array through the unified editor', async () => {
    const input = JSON.stringify({
      metaData: {type: 'EMSolution_Input', version: '1.0'},
      '0_Release_Number': {RLS_NO: 'r6.6'},
      '1_Execution_Control': {},
      '2_Analysis_Type': {STATIC: 0, AC: 0, TRANSIENT: 1},
    });
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('empty-field-sources.json', input)]);

    const action = screen.getByRole('button', {name: 'Edit Field Sources'});
    expect(action).toBeEnabled();
    const dialog = await openFieldSourceEditor();
    expect(within(dialog).getByText('No Field Sources match the current filters.')).toBeInTheDocument();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add source'}));
    expect(within(dialog).getByRole('menu', {name: 'Choose Field Source type'})).toHaveTextContent('External lumped-element circuit network connected to FEM source series.');
    await userEvent.keyboard('{Escape}');
    expect(within(dialog).queryByRole('menu', {name: 'Choose Field Source type'})).not.toBeInTheDocument();
    expect(within(dialog).getByRole('button', {name: 'Add source'})).toHaveFocus();
    expect(screen.getByRole('dialog', {name: 'Field Source editor'})).toBeInTheDocument();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add source'}));
    await userEvent.click(within(dialog).getByRole('menuitem', {name: 'Add External network (NETWORK)'}));
    const editor = within(dialog).getByRole('region', {name: 'NETWORK editor'});
    await applySpecialSourceEditor(dialog, editor);

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source']).toEqual([{
      NETWORK: {REGION_FACTOR: 1, REGION_PARALLEL: 1, data: []},
    }]);
  });

  it('edits generic fields and nested rows with descriptions and documentation', async () => {
    const payload = JSON.parse(emsolutionInput());
    payload['17_Field_Source'][0].PHICOIL.vendor = 'retained';
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('generic-field-source.json', JSON.stringify(payload))]);
    const dialog = await openFieldSourceEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Field Source row 1'}));

    expect(within(dialog).getByText('Potential-derived current distribution for a single conductor region.')).toBeInTheDocument();
    expect(within(dialog).getByRole('link', {name: 'Official documentation'})).toHaveAttribute('href', expect.stringContaining('17_4_PHICOIL'));
    fireEvent.change(within(dialog).getByLabelText('Series ID (SERIES_ID)'), {target: {value: '2'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add row'}));
    fireEvent.change(within(dialog).getByLabelText('Material IDs (MAT_IDS)'), {target: {value: '10000, 10001'}});
    fireEvent.change(within(dialog).getByLabelText('Surface material ID (SMAT_ID)'), {target: {value: '20000'}});
    fireEvent.change(within(dialog).getByLabelText('Current (CURRENT)'), {target: {value: '12.5'}});
    fireEvent.change(within(dialog).getByLabelText('Conductivity (SIGMA)'), {target: {value: '58000000'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Duplicate nested row 1'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Move nested row 2 up'}));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Delete nested row 2'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][0].PHICOIL).toMatchObject({SERIES_ID: 2, vendor: 'retained'});
    expect(savedValue['17_Field_Source'][0].PHICOIL.data).toEqual([{
      MAT_IDS: [10000, 10001], SMAT_ID: 20000, CURRENT: 12.5, SIGMA: 58000000, CAL_Je: 0,
    }]);
  });

  it('browses current volume and surface materials while assigning Field Source IDs', async () => {
    const payload = JSON.parse(emsolutionInput());
    payload['16_Material_Properties'] = {
      EXTEND_TOTAL_for_COIL: 0,
      '16_1_3D_Element_Properties': [
        {MAT_ID: 10000, MAT_NAME: 'Copper', POTENTIAL: 0, ElectricProperty: {conductivity: {SIGMA: 58_000_000}}, vendor: 'keep'},
        {MAT_ID: 10001, MAT_NAME: 'Aluminium', ElectricProperty: {conductivity: {SIGMA: 35_000_000}}},
      ],
      '16_2_2D_Element_Properties': [
        {SMAT_ID: 20000, GAP_ELEMENT: {THICKNESS: 0.001}},
        {SMAT_ID: 'invalid', FUTURE_SURFACE: {vendor: true}},
      ],
    };
    payload['17_Field_Source'][0].PHICOIL.data = [{MAT_IDS: [], SMAT_ID: '', CURRENT: 12.5, SIGMA: 58_000_000, CAL_Je: 0}];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('material-picker.json', JSON.stringify(payload))]);
    const dialog = await openFieldSourceEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Field Source row 1'}));

    await userEvent.click(within(dialog).getByRole('button', {name: 'Browse volume materials for Material IDs (MAT_IDS)'}));
    await userEvent.keyboard('{Escape}');
    expect(within(dialog).queryByRole('region', {name: 'Material IDs (MAT_IDS) material picker'})).not.toBeInTheDocument();
    expect(screen.getByRole('dialog', {name: 'Field Source editor'})).toBeInTheDocument();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Browse volume materials for Material IDs (MAT_IDS)'}));
    const volumePicker = within(dialog).getByRole('region', {name: 'Material IDs (MAT_IDS) material picker'});
    expect(within(volumePicker).getByText('10000 · Copper')).toBeInTheDocument();
    await userEvent.click(within(volumePicker).getByRole('button', {name: 'Add volume material 10000 for Material IDs (MAT_IDS)'}));
    await userEvent.click(within(volumePicker).getByRole('button', {name: 'Remove volume material 10000 for Material IDs (MAT_IDS)'}));
    await userEvent.click(within(volumePicker).getByRole('button', {name: 'Add volume material 10000 for Material IDs (MAT_IDS)'}));
    await userEvent.click(within(volumePicker).getByRole('button', {name: 'Add volume material 10001 for Material IDs (MAT_IDS)'}));
    await userEvent.click(within(volumePicker).getByRole('button', {name: 'Close Material IDs (MAT_IDS) material picker'}));

    await userEvent.click(within(dialog).getByRole('button', {name: 'Browse surface and volume materials for Surface material ID (SMAT_ID)'}));
    const surfacePicker = within(dialog).getByRole('region', {name: 'Surface material ID (SMAT_ID) material picker'});
    expect(within(surfacePicker).getByRole('region', {name: 'Surface materials for Surface material ID (SMAT_ID)'})).toBeInTheDocument();
    expect(within(surfacePicker).getByRole('region', {name: 'Volume materials for Surface material ID (SMAT_ID)'})).toBeInTheDocument();
    expect(within(surfacePicker).getByRole('button', {name: 'Invalid ID surface material surface-1 for Surface material ID (SMAT_ID)'})).toBeDisabled();
    await userEvent.click(within(surfacePicker).getByRole('button', {name: 'Use volume material 10000 for Surface material ID (SMAT_ID)'}));

    expect(within(dialog).getByLabelText('Material IDs (MAT_IDS)')).toHaveValue('10000, 10001');
    expect(within(dialog).getByLabelText('Surface material ID (SMAT_ID)')).toHaveValue(10000);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][0].PHICOIL.data[0]).toMatchObject({MAT_IDS: [10000, 10001], SMAT_ID: 10000});
    expect(savedValue['16_Material_Properties']['16_1_3D_Element_Properties'][0].vendor).toBe('keep');
  });

  it('offers volume materials for SMAT_ID when the surface collection is empty', async () => {
    const payload = JSON.parse(emsolutionInput());
    payload['16_Material_Properties'] = {
      EXTEND_TOTAL_for_COIL: 0,
      '16_1_3D_Element_Properties': [{MAT_ID: 77, MAT_NAME: 'Volume fallback'}],
      '16_2_2D_Element_Properties': [],
    };
    payload['17_Field_Source'][0].PHICOIL.data = [{MAT_IDS: [1], SMAT_ID: 2, CURRENT: 1, SIGMA: 1, CAL_Je: 0}];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('material-picker-empty.json', JSON.stringify(payload))]);
    const dialog = await openFieldSourceEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Field Source row 1'}));

    await userEvent.click(within(dialog).getByRole('button', {name: 'Browse surface and volume materials for Surface material ID (SMAT_ID)'}));
    const picker = within(dialog).getByRole('region', {name: 'Surface material ID (SMAT_ID) material picker'});
    expect(within(picker).getByText('No surface materials are defined in 16_Material_Properties.')).toBeInTheDocument();
    expect(within(picker).getByText('77 · Volume fallback')).toBeInTheDocument();
    await userEvent.click(within(picker).getByRole('button', {name: 'Use volume material 77 for Surface material ID (SMAT_ID)'}));
    expect(within(dialog).getByLabelText('Material IDs (MAT_IDS)')).toHaveValue('1');
    expect(within(dialog).getByLabelText('Surface material ID (SMAT_ID)')).toHaveValue(77);
  });

  it('limits the SDEFCOIL boundary-surface picker to four material IDs', async () => {
    const payload = JSON.parse(emsolutionInput());
    payload['16_Material_Properties'] = {
      EXTEND_TOTAL_for_COIL: 0,
      '16_1_3D_Element_Properties': [{MAT_ID: 10, MAT_NAME: 'Coil'}],
      '16_2_2D_Element_Properties': [1, 2, 3, 4, 5].map((id) => ({SMAT_ID: id, GAP_ELEMENT: {THICKNESS: id / 1000}})),
    };
    payload['17_Field_Source'] = [{SDEFCOIL: {
      SERIES_ID: 1, IN_ROTOR: 0,
      data: [{MAT_ID: 10, SMAT_IDS: [], CURRENT: 1, SIGMA: 1, CAL_Je: 0}],
    }}];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('surface-limit.json', JSON.stringify(payload))]);
    const dialog = await openFieldSourceEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Field Source row 1'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Browse surface and volume materials for Boundary surfaces (SMAT_IDS)'}));
    const picker = within(dialog).getByRole('region', {name: 'Boundary surfaces (SMAT_IDS) material picker'});
    await userEvent.click(within(picker).getByRole('button', {name: 'Add volume material 10 for Boundary surfaces (SMAT_IDS)'}));
    for (const id of [1, 2, 3]) {
      await userEvent.click(within(picker).getByRole('button', {name: `Add surface material ${id} for Boundary surfaces (SMAT_IDS)`}));
    }
    expect(within(picker).getByRole('button', {name: 'Add surface material 4 for Boundary surfaces (SMAT_IDS)'})).toBeDisabled();
    await userEvent.click(within(picker).getByRole('button', {name: 'Remove volume material 10 for Boundary surfaces (SMAT_IDS)'}));
    await userEvent.click(within(picker).getByRole('button', {name: 'Add surface material 4 for Boundary surfaces (SMAT_IDS)'}));
    expect(within(dialog).getByLabelText('Boundary surfaces (SMAT_IDS)')).toHaveValue('1, 2, 3, 4');
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][0].SDEFCOIL.data[0].SMAT_IDS).toEqual([1, 2, 3, 4]);
  });

  it('duplicates, reorders, and deletes complete Field Source entries', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('source-crud.json', emsolutionInput())]);
    const dialog = await openFieldSourceEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Duplicate Field Source row 1'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Move Field Source row 2 down'}));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Delete Field Source row 1'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const sources = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value)['17_Field_Source'];
    expect(sources).toHaveLength(2);
    expect(Object.keys(sources[0])).toEqual(['NETWORK']);
    expect(Object.keys(sources[1])).toEqual(['PHICOIL']);
  });

  it('creates a missing Material Properties block and edits optional MAT_NAME', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('materials.json', emsolutionInput())]);
    const dialog = await openMaterialPropertyEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Volume (0)'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add volume material'}));
    fireEvent.change(within(dialog).getByLabelText('Material ID (MAT_ID)'), {target: {value: '10'}});
    fireEvent.change(within(dialog).getByLabelText('Material name (MAT_NAME)'), {target: {value: 'stator'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const saved = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(saved['16_Material_Properties']).toMatchObject({EXTEND_TOTAL_for_COIL: 0});
    expect(saved['16_Material_Properties']['16_1_3D_Element_Properties'][0]).toMatchObject({
      MAT_ID: 10, MAT_NAME: 'stator', POTENTIAL: 0,
      ElectricProperty: {conductivity: {SIGMA: 0}}, MagneticProperty: {MU: 1},
    });
    expect(screen.getByText('Applied Material Property changes to the open document. Save the file to keep them.')).toBeInTheDocument();
    expect(screen.getByLabelText('Modified')).toBeInTheDocument();
  });

  it('edits advanced volume properties while preserving vendor data', async () => {
    const input = JSON.parse(emsolutionInput());
    input['16_Material_Properties'] = {
      EXTEND_TOTAL_for_COIL: 0,
      vendorRoot: 'keep',
      '16_1_3D_Element_Properties': [{
        MAT_ID: 10, MAT_NAME: 'old', POTENTIAL: 0, vendor: {flag: true},
        ElectricProperty: {conductivity: {SIGMA: 0, note: 'keep'}},
        MagneticProperty: {MU: 1},
      }],
      '16_2_2D_Element_Properties': [],
    };
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('advanced-material.json', JSON.stringify(input))]);
    const dialog = await openMaterialPropertyEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Volume (1)'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit volume material row 1'}));
    fireEvent.change(within(dialog).getByLabelText('Material name (MAT_NAME)'), {target: {value: 'stator'}});
    const packingCard = within(dialog).getByText('Lamination packing').closest('section')!;
    await userEvent.click(within(packingCard).getByRole('button', {name: 'Add Lamination packing'}));
    fireEvent.change(within(dialog).getByLabelText('Packing factor (PACKING_FACTOR)'), {target: {value: '0.96'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const materialRoot = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value)['16_Material_Properties'];
    const material = materialRoot['16_1_3D_Element_Properties'][0];
    expect(materialRoot.vendorRoot).toBe('keep');
    expect(material).toMatchObject({MAT_NAME: 'stator', vendor: {flag: true}});
    expect(material.ElectricProperty.conductivity.note).toBe('keep');
    expect(material.MagneticProperty.PACKING).toMatchObject({PACKING_FACTOR: 0.96, PACKING_DIRECTION: [0, 0, 1]});
  });

  it('adds surface materials and preserves legacy nonlinear parameter spelling', async () => {
    const input = JSON.parse(emsolutionInput());
    input['16_Material_Properties'] = {
      EXTEND_TOTAL_for_COIL: 0,
      '16_1_3D_Element_Properties': [],
      '16_2_2D_Element_Properties': [{SMAT_ID: 1, SURFACE_IMPEDANCE: {
        SIGMA: 1, MU: 1, IMP_TYPE: 1,
        Nonliear_Parameters: {BH_CURVE_ID: 1, AGRWALL: 0.75, K: 5, HK: 2000, vendor: 'keep'},
      }}],
    };
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('surface-material.json', JSON.stringify(input))]);
    const dialog = await openMaterialPropertyEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Surface (1)'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit surface material row 1'}));
    fireEvent.change(within(dialog).getByLabelText('K value (K)'), {target: {value: '6'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Back to materials'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add surface material'}));
    expect(within(dialog).getByRole('menu', {name: 'Choose surface material type'})).toHaveTextContent('Thin magnetic or insulating gap element.');
    await userEvent.click(within(dialog).getByRole('menuitem', {name: 'Add Gap element (GAP_ELEMENT)'}));
    fireEvent.change(within(dialog).getByLabelText('Surface material ID (SMAT_ID)'), {target: {value: '2'}});
    fireEvent.change(within(dialog).getByLabelText('Thickness (THICKNESS)'), {target: {value: '0.01'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const surfaces = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value)['16_Material_Properties']['16_2_2D_Element_Properties'];
    expect(surfaces[0].SURFACE_IMPEDANCE.Nonliear_Parameters).toMatchObject({K: 6, vendor: 'keep'});
    expect(surfaces[0].SURFACE_IMPEDANCE).not.toHaveProperty('Nonlinear_Parameters');
    expect(surfaces[1]).toEqual({SMAT_ID: 2, GAP_ELEMENT: {THICKNESS: 0.01}});
  });

  it('disables malformed material roots and cancels staged changes', async () => {
    const malformed = JSON.parse(emsolutionInput());
    malformed['16_Material_Properties'] = {'16_1_3D_Element_Properties': {MAT_ID: 1}};
    const valid = JSON.parse(emsolutionInput());
    valid['16_Material_Properties'] = {EXTEND_TOTAL_for_COIL: 0, '16_1_3D_Element_Properties': [], '16_2_2D_Element_Properties': []};
    const original = JSON.stringify(valid);
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('malformed-material.json', JSON.stringify(malformed))]);
    expect(screen.getByRole('button', {name: 'Edit Material Properties'})).toBeDisabled();

    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [jsonFile('valid-material.json', original)]}});
    const dialog = await openMaterialPropertyEditor();
    fireEvent.change(within(dialog).getByLabelText('Extend total-potential region (EXTEND_TOTAL_for_COIL)'), {target: {value: '1'}});
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveValue(original);
    expect(screen.queryByLabelText('Modified')).not.toBeInTheDocument();
  });

  it('creates a missing Time Function collection and previews a guided AC waveform', async () => {
    const input = JSON.parse(emsolutionInput());
    delete input['18_Time_Function'];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('time-functions.json', JSON.stringify(input))]);
    const dialog = await openTimeFunctionEditor();
    expect(within(dialog).getByText('No Time Functions match the current filters.')).toBeInTheDocument();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add time function'}));
    expect(within(dialog).getByRole('menu', {name: 'Choose Time Function type'})).toHaveTextContent('Create an unsupported or advanced time function');
    await userEvent.click(within(dialog).getByRole('menuitem', {name: 'Add AC waveform (2)'}));
    expect(within(dialog).getByRole('img', {name: /f of t equals amplitude/})).toBeInTheDocument();
    expect(within(dialog).getByRole('img', {name: /Time-function preview/})).toBeInTheDocument();
    fireEvent.change(within(dialog).getByLabelText('Amplitude (AMPLITUDE)'), {target: {value: '5'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const saved = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(saved['18_Time_Function']).toEqual([{TIME_ID: 1, OPTION: 2, AMPLITUDE: 5, TCYCLE: 1, PHASE: 0}]);
    expect(screen.getByText('Applied Time Function changes to the open document. Save the file to keep them.')).toBeInTheDocument();
  });

  it('edits paired table points and keeps equal consecutive times as a vertical preview step', async () => {
    const input = JSON.parse(emsolutionInput());
    input['18_Time_Function'] = [{TIME_ID: 1, OPTION: 1, CYCLE: 1, TIME: [0, 0.5, 1], VALUE: [0, 1, 0]}];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('table-time.json', JSON.stringify(input))]);
    const dialog = await openTimeFunctionEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Time Function row 1'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Duplicate time point 2'}));
    fireEvent.change(within(dialog).getByLabelText('Value point 3'), {target: {value: '2'}});
    expect(within(dialog).getByRole('img', {name: /Time-function preview/})).toBeInTheDocument();
    expect(within(dialog).queryByText(/non-decreasing/)).not.toHaveClass('networkIssueError');
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));
    const table = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value)['18_Time_Function'][0];
    expect(table.TIME).toEqual([0, 0.5, 0.5, 1]);
    expect(table.VALUE).toEqual([0, 1, 2, 0]);
  });

  it('presents OPTION 3 and future options only as whole-entry raw JSON', async () => {
    const input = JSON.parse(emsolutionInput());
    input['18_Time_Function'] = [{TIME_ID: 4, OPTION: 3, SPRING: [{vendor: 'keep'}], custom: {nested: true}}];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('raw-time.json', JSON.stringify(input))]);
    const dialog = await openTimeFunctionEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Time Function row 1'}));
    expect((within(dialog).getByLabelText('Raw Time Function entry JSON') as HTMLTextAreaElement).value).toContain('"SPRING"');
    expect(within(dialog).queryByLabelText('Time Function option')).not.toBeInTheDocument();
    expect(within(dialog).queryByText('Preview')).not.toBeInTheDocument();
    fireEvent.change(within(dialog).getByLabelText('Raw Time Function entry JSON'), {target: {value: JSON.stringify({TIME_ID: 4, OPTION: 99, vendor: {keep: true}})}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Save raw JSON'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));
    const saved = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value)['18_Time_Function'][0];
    expect(saved).toEqual({TIME_ID: 4, OPTION: 99, vendor: {keep: true}});
  });

  it('disables malformed Time Function roots and repairs malformed array entries through raw JSON', async () => {
    const malformedRoot = JSON.parse(emsolutionInput());
    malformedRoot['18_Time_Function'] = {TIME_ID: 1, OPTION: 2};
    const repairable = JSON.parse(emsolutionInput());
    repairable['18_Time_Function'] = ['bad'];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('malformed-time-root.json', JSON.stringify(malformedRoot))]);
    expect(screen.getByRole('button', {name: 'Edit Time Functions'})).toBeDisabled();

    fireEvent.change(container.querySelector<HTMLInputElement>('input[type="file"]')!, {target: {files: [jsonFile('repair-time.json', JSON.stringify(repairable))]}});
    const dialog = await openTimeFunctionEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Time Function row 1'}));
    expect(within(dialog).getByRole('button', {name: 'Apply changes'})).toBeDisabled();
    fireEvent.change(within(dialog).getByLabelText('Raw Time Function entry JSON'), {target: {value: JSON.stringify({TIME_ID: 1, OPTION: 3, vendor: 'kept'})}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Save raw JSON'}));
    expect(within(dialog).getByRole('button', {name: 'Apply changes'})).toBeEnabled();
  });

  it('picks guided and raw TIME_ID references while retaining manual entry and pinned zero', async () => {
    const input = JSON.parse(emsolutionInput());
    input['17_Field_Source'][0] = {SUFCUR: {SERIES_ID: 1, TIME_ID: 123, SMAT_ID: 1, CURRENT: 2, IN_ROTOR: 0}};
    input['18_Time_Function'] = [
      {TIME_ID: 7, OPTION: 2, AMPLITUDE: 3, TCYCLE: 1, PHASE: 0},
      {TIME_ID: 9, OPTION: 99, vendorRaw: {searchable: true}},
      {TIME_ID: 'bad', OPTION: 4, PSIM_IN: 1, PSIM_OUT: 2},
    ];
    const timeFunctionsBefore = structuredClone(input['18_Time_Function']);
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('time-picker.json', JSON.stringify(input))]);
    const dialog = await openFieldSourceEditor();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit Field Source row 1'}));

    const trigger = within(dialog).getByRole('button', {name: 'Choose Time function'});
    const timeInput = within(dialog).getByLabelText('Time function (TIME_ID)');
    expect(timeInput).toHaveValue(123);
    await userEvent.click(trigger);
    let picker = screen.getByRole('dialog', {name: 'Choose a Time Function'});
    expect(dialog.contains(picker)).toBe(true);
    expect(within(picker).getByRole('button', {name: 'Entry 3 has an invalid TIME_ID'})).toBeDisabled();
    await userEvent.type(within(picker).getByRole('searchbox', {name: 'Search Time Functions'}), 'vendorRaw');
    expect(within(picker).getAllByText(/Unsupported OPTION 99/)).toHaveLength(2);
    await userEvent.click(within(picker).getByText('Raw JSON'));
    expect(within(picker).getByText(/"vendorRaw"/)).toBeInTheDocument();
    await userEvent.click(within(picker).getByRole('button', {name: 'Use TIME_ID 9'}));
    expect(timeInput).toHaveValue(9);

    await userEvent.click(trigger);
    picker = screen.getByRole('dialog', {name: 'Choose a Time Function'});
    await userEvent.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog', {name: 'Choose a Time Function'})).not.toBeInTheDocument());
    await waitFor(() => expect(trigger).toHaveFocus());
    expect(screen.getByRole('dialog', {name: 'Field Source editor'})).toBeInTheDocument();

    fireEvent.change(timeInput, {target: {value: '404'}});
    expect(timeInput).toHaveValue(404);
    await userEvent.click(trigger);
    fireEvent.mouseDown(within(dialog).getByText(/Entry 1 · SUFCUR/));
    await waitFor(() => expect(screen.queryByRole('dialog', {name: 'Choose a Time Function'})).not.toBeInTheDocument());
    await userEvent.click(trigger);
    picker = screen.getByRole('dialog', {name: 'Choose a Time Function'});
    await userEvent.click(within(picker).getByRole('button', {name: 'Use TIME_ID 0'}));
    expect(timeInput).toHaveValue(0);

    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));
    const saved = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(saved['17_Field_Source'][0].SUFCUR.TIME_ID).toBe(0);
    expect(saved['18_Time_Function']).toEqual(timeFunctionsBefore);
  });

  it('uses the TIME_ID picker in staged NETWORK components', async () => {
    const input = JSON.parse(emsolutionInput());
    input['18_Time_Function'].push({TIME_ID: 5, OPTION: 11, FUNCTION: 'T'});
    const timeFunctionsBefore = structuredClone(input['18_Time_Function']);
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('network-time-picker.json', JSON.stringify(input))]);
    const {dialog, editor} = await openSpecialSourceEditor('NETWORK');
    await userEvent.click(within(editor).getByRole('button', {name: 'Edit NETWORK row 2'}));
    await userEvent.click(within(editor).getByRole('button', {name: 'Choose Time function'}));
    const picker = screen.getByRole('dialog', {name: 'Choose a Time Function'});
    await userEvent.click(within(picker).getByRole('button', {name: 'Use TIME_ID 5'}));
    expect(within(editor).getByLabelText('Time function')).toHaveValue(5);
    await userEvent.click(within(editor).getByRole('button', {name: 'Save row'}));
    await applySpecialSourceEditor(dialog, editor);

    const saved = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(saved['17_Field_Source'][1].NETWORK.data[1].TIME_ID).toBe(5);
    expect(saved['18_Time_Function']).toEqual(timeFunctionsBefore);
  });

  it('uses the portaled TIME_ID picker in CIRCUIT power-supply rows', async () => {
    const input = JSON.parse(emsolutionCircuitInput());
    input['18_Time_Function'].push({TIME_ID: 5, OPTION: 3, vendor: 'raw-selectable'});
    const timeFunctionsBefore = structuredClone(input['18_Time_Function']);
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('circuit-time-picker.json', JSON.stringify(input))]);
    const {dialog, editor} = await openSpecialSourceEditor('CIRCUIT');
    await userEvent.click(within(editor).getByRole('button', {name: 'Choose Power supply 1 time ID'}));
    const picker = screen.getByRole('dialog', {name: 'Choose a Time Function'});
    expect(dialog.contains(picker)).toBe(true);
    await userEvent.click(within(picker).getByRole('button', {name: 'Use TIME_ID 5'}));
    expect(within(editor).getByLabelText('Power supply 1 time ID')).toHaveValue(5);
    await applySpecialSourceEditor(dialog, editor);

    const saved = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(saved['17_Field_Source'][1].CIRCUIT.POWER_SUPPLIES[0].TIME_ID).toBe(5);
    expect(saved['18_Time_Function']).toEqual(timeFunctionsBefore);
  });
});
