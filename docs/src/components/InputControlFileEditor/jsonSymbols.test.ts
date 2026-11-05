import {describe, expect, it} from 'vitest';

import {
  buildJsonSymbolTree,
  editorWindowTitle,
  findJsonSymbolTrail,
  uniqueDisplayName,
} from './jsonSymbols';

describe('JSON symbols', () => {
  it('builds nested object and array breadcrumbs', () => {
    const text = `{
  "solver": {
    "boundaries": [
      {"voltage": 12},
      {"voltage": 24}
    ]
  }
}`;
    const tree = buildJsonSymbolTree(text);
    const offset = text.indexOf('24');
    const trail = findJsonSymbolTrail(tree.roots, offset);

    expect(tree.errors).toHaveLength(0);
    expect(trail.map(({symbol}) => symbol.name)).toEqual([
      'solver',
      'boundaries',
      '[1]',
      'voltage',
    ]);
    expect(trail[1].children.map(({name}) => name)).toEqual(['[0]', '[1]']);
  });

  it('keeps escaped property names and primitive details', () => {
    const tree = buildJsonSymbolTree('{"quoted\\"key": true}');
    expect(tree.roots[0].name).toBe('quoted"key');
    expect(tree.roots[0].detail).toBe('true');
  });

  it('returns safe partial symbols for malformed JSON', () => {
    const tree = buildJsonSymbolTree('{"valid": {"child": 1}, "broken": }');
    expect(tree.errors.length).toBeGreaterThan(0);
    expect(tree.roots.some(({name}) => name === 'valid')).toBe(true);
  });
});

describe('document naming', () => {
  it('numbers duplicate filenames deterministically', () => {
    expect(uniqueDisplayName('input.json', [])).toBe('input.json');
    expect(uniqueDisplayName('input.json', ['input.json'])).toBe('input.json (2)');
    expect(uniqueDisplayName('input.json', ['input.json', 'input.json (2)'])).toBe('input.json (3)');
  });

  it('creates the specified browser titles', () => {
    expect(editorWindowTitle()).toBe('Input Control File Editor | pyemsi');
    expect(editorWindowTitle('input.json')).toBe('input.json — Input Control File Editor | pyemsi');
    expect(editorWindowTitle('a.json', 'b.json')).toBe('a.json ↔ b.json — Input Control File Editor | pyemsi');
  });
});
