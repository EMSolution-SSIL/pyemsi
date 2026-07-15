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
      {PHICOIL: {SERIES_ID: 1, data: []}},
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
      {ELMCUR: {SERIES_ID: 1, data: []}},
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

  it('shows the NETWORK action only for recognized EMSolution inputs', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('generic.json', '{"NETWORK": {"data": []}}')]);
    expect(screen.queryByRole('button', {name: 'Edit NETWORK'})).not.toBeInTheDocument();

    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [jsonFile('transient.json', emsolutionInput())]}});
    expect(await screen.findByRole('button', {name: 'Edit NETWORK'})).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    expect(within(dialog).getByText('FEM source')).toBeInTheDocument();
    expect(within(dialog).getByText('Current source')).toBeInTheDocument();
    expect(within(dialog).getByText('Resistor')).toBeInTheDocument();
    expect(within(dialog).getByRole('link', {name: 'Official documentation'})).toHaveAttribute('href', expect.stringContaining('17_9_NETWORK'));
  });

  it('applies staged NETWORK row edits through the canonical document', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('transient.json', emsolutionInput())]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});

    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit NETWORK row 3'}));
    fireEvent.change(within(dialog).getByLabelText('Resistance'), {target: {value: '42.5'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Save row'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.data[2].RESISTANCE).toBe(42.5);
    expect(screen.getByLabelText('Modified')).toBeInTheDocument();
    expect(screen.getByText('Applied NETWORK changes to the open document. Save the file to keep them.')).toBeInTheDocument();
  });

  it('discards staged NETWORK changes when the modal is cancelled', async () => {
    const original = emsolutionInput();
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('transient.json', original)]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    fireEvent.change(within(dialog).getByLabelText('Region factor'), {target: {value: '4'}});
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));

    expect(screen.queryByRole('dialog', {name: 'NETWORK editor'})).not.toBeInTheDocument();
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveValue(original);
    expect(screen.queryByLabelText('Modified')).not.toBeInTheDocument();
  });

  it('adds and derives counts for a TABLE dataset', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('transient.json', emsolutionInput())]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    await userEvent.selectOptions(within(dialog).getByLabelText('New NETWORK component type'), 'TABLE');
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add component'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add dataset'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add I–V point'}));
    fireEvent.change(within(dialog).getByLabelText('Table 1 current 1'), {target: {value: '2'}});
    fireEvent.change(within(dialog).getByLabelText('Table 1 voltage 1'), {target: {value: '0.7'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Save row'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    const table = savedValue['17_Field_Source'][1].NETWORK.data[3];
    expect(table).toMatchObject({type: 'TABLE', NUMBER: 1});
    expect(table.data[0]).toMatchObject({NO_DATA: 1, CURRENT: [2], VOLTAGE: [0.7]});
  });

  it('preserves unknown NETWORK properties through raw editing', async () => {
    const unknown = {type: 'FUTURE', ID: 77, vendor: {flag: true}};
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('future.json', emsolutionInput([unknown]))]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Edit NETWORK row 1'}));
    const raw = within(dialog).getByLabelText('Raw NETWORK component JSON');
    fireEvent.change(raw, {target: {value: JSON.stringify({...unknown, added: 'kept'})}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Save row'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.data[0]).toEqual({...unknown, added: 'kept'});
  });

  it('adds a SWITCH with paired timings and phase-aware fields', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('switch.json', emsolutionInput())]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    await userEvent.selectOptions(within(dialog).getByLabelText('New NETWORK component type'), 'SWITCH');
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add component'}));
    const editor = within(dialog).getByLabelText('SWITCH component editor');
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
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.data[3]).toMatchObject({
      type: 'SWITCH', ID: 4, START: 1, END: 2, PHASE_OP: 1,
      ON_TIME: [30], OFF_TIME: [180],
    });
  });

  it('duplicates, reorders, and deletes NETWORK rows', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('actions.json', emsolutionInput())]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Duplicate NETWORK row 3'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Move NETWORK row 4 up'}));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Delete NETWORK row 1'}));
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

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
    const networkButton = await screen.findByRole('button', {name: 'Edit NETWORK'});
    await userEvent.click(networkButton);
    expect(screen.getByRole('dialog', {name: 'NETWORK editor'})).toHaveTextContent('network.json');
    fireEvent.keyDown(document, {key: 'Escape'});
    expect(screen.queryByRole('dialog', {name: 'NETWORK editor'})).not.toBeInTheDocument();
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
    await userEvent.click(screen.getByRole('button', {name: 'Edit NETWORK'}));
    const dialog = screen.getByRole('dialog', {name: 'NETWORK editor'});
    await userEvent.selectOptions(within(dialog).getByLabelText('NETWORK occurrence'), '1');
    fireEvent.change(within(dialog).getByLabelText('Region factor'), {target: {value: '3'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    expect(savedValue['17_Field_Source'][1].NETWORK.REGION_FACTOR).toBe(8);
    expect(savedValue['17_Field_Source'][2].NETWORK.REGION_FACTOR).toBe(3);
  });

  it('shows CIRCUIT only for recognized EMSolution field sources and links its documentation', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('generic.json', JSON.stringify({CIRCUIT: {SERIES_IDS: []}}))]);
    expect(screen.queryByRole('button', {name: 'Edit CIRCUIT'})).not.toBeInTheDocument();

    const input = container.querySelector<HTMLInputElement>('input[type="file"]')!;
    fireEvent.change(input, {target: {files: [jsonFile('circuit.json', emsolutionCircuitInput())]}});
    const button = await screen.findByRole('button', {name: 'Edit CIRCUIT'});
    await userEvent.click(button);
    const dialog = screen.getByRole('dialog', {name: 'CIRCUIT editor'});
    expect(within(dialog).getByText('Source series')).toBeInTheDocument();
    expect(within(dialog).getByText('Power supplies')).toBeInTheDocument();
    expect(within(dialog).getByRole('link', {name: 'Official documentation'})).toHaveAttribute('href', expect.stringContaining('17_8_CIRCUIT'));
  });

  it('applies staged CIRCUIT settings, matrix, and power-supply edits', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('circuit.json', emsolutionCircuitInput())]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit CIRCUIT'}));
    const dialog = screen.getByRole('dialog', {name: 'CIRCUIT editor'});
    fireEvent.change(within(dialog).getByLabelText('CIRCUIT region factor'), {target: {value: '4'}});
    fireEvent.change(within(dialog).getByLabelText('External inductance row 1 column 1'), {target: {value: '0.25'}});
    fireEvent.change(within(dialog).getByLabelText('Power supply 1 initial current'), {target: {value: '3'}});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

    const savedValue = JSON.parse((screen.getByRole('textbox', {name: /Monaco/}) as HTMLTextAreaElement).value);
    const circuit = savedValue['17_Field_Source'][1].CIRCUIT;
    expect(circuit.REGION_FACTOR).toBe(4);
    expect(circuit.INDUCTANCE_MATRIX.MATRIX).toEqual([[0.25]]);
    expect(circuit.POWER_SUPPLIES[0]).toMatchObject({INITIAL_CURRENT: 3, vendor: 'keep'});
    expect(circuit.INDUCTANCE_MATRIX.comment).toBe('keep');
    expect(screen.getByText('Applied CIRCUIT changes to the open document. Save the file to keep them.')).toBeInTheDocument();
    expect(screen.getByLabelText('Modified')).toBeInTheDocument();
  });

  it('resizes CIRCUIT matrices when adding a series and blocks Apply until new cells are complete', async () => {
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [jsonFile('circuit.json', emsolutionCircuitInput())]);
    await userEvent.click(screen.getByRole('button', {name: 'Edit CIRCUIT'}));
    const dialog = screen.getByRole('dialog', {name: 'CIRCUIT editor'});
    await userEvent.click(within(dialog).getByRole('button', {name: 'Add series'}));
    expect(within(dialog).getByRole('button', {name: 'Apply changes'})).toBeDisabled();
    fireEvent.change(within(dialog).getByLabelText('Series ID 2'), {target: {value: '2'}});
    for (const [label, value] of [
      ['External inductance row 2 column 1', '0.1'],
      ['External inductance row 2 column 2', '0.2'],
      ['External resistance row 2 column 1', '0'],
      ['External resistance row 2 column 2', '6'],
      ['Connection row 2 column 1', '1'],
    ]) fireEvent.change(within(dialog).getByLabelText(label), {target: {value}});
    expect(within(dialog).getByRole('button', {name: 'Apply changes'})).toBeEnabled();
    await userEvent.click(within(dialog).getByRole('button', {name: 'Apply changes'}));

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
    await userEvent.click(screen.getByRole('button', {name: 'Edit CIRCUIT'}));
    const dialog = screen.getByRole('dialog', {name: 'CIRCUIT editor'});
    await userEvent.selectOptions(within(dialog).getByLabelText('CIRCUIT occurrence'), '1');
    await userEvent.click(within(dialog).getByRole('button', {name: 'Duplicate power supply row 1'}));
    expect(within(dialog).getByLabelText('Power supply 2 ID')).toHaveValue(2);
    expect(within(dialog).getByLabelText('Connection row 1 column 2')).toHaveValue(1);
    fireEvent.change(within(dialog).getByLabelText('CIRCUIT region factor'), {target: {value: '3'}});
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
    expect(screen.getByRole('textbox', {name: /Monaco/})).toHaveValue(original);
    expect(screen.queryByLabelText('Modified')).not.toBeInTheDocument();
  });

  it('disables malformed CIRCUIT data and targets the focused split document', async () => {
    const malformed = JSON.parse(emsolutionCircuitInput());
    malformed['17_Field_Source'][1].CIRCUIT = [];
    const {container} = render(<InputControlFileEditorClient />);
    await chooseFiles(container, [
      jsonFile('malformed.json', JSON.stringify(malformed)),
      jsonFile('focused-circuit.json', emsolutionCircuitInput()),
    ]);
    const malformedButton = screen.getByRole('button', {name: 'Edit CIRCUIT'});
    expect(malformedButton).toBeDisabled();
    expect(malformedButton).toHaveAttribute('title', expect.stringContaining('not an editable object'));

    await userEvent.selectOptions(
      screen.getByLabelText('Split editor with'),
      screen.getByRole('option', {name: 'focused-circuit.json'}),
    );
    const focusedButton = screen.getByRole('button', {name: 'Edit CIRCUIT'});
    expect(focusedButton).toBeEnabled();
    await userEvent.click(focusedButton);
    expect(screen.getByRole('dialog', {name: 'CIRCUIT editor'})).toHaveTextContent('focused-circuit.json');
    fireEvent.keyDown(document, {key: 'Escape'});
    expect(screen.queryByRole('dialog', {name: 'CIRCUIT editor'})).not.toBeInTheDocument();
    expect(focusedButton).toHaveFocus();
  });
});
