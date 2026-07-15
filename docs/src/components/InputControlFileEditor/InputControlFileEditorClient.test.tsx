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
});
