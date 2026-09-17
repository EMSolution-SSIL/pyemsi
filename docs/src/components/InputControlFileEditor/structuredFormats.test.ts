import {describe, expect, it} from 'vitest';

import {findSymbolTrail} from './jsonSymbols';
import {
  findTomlCompatibilityIssue,
  parseStructuredFormat,
  serializeStructuredFormat,
} from './structuredFormats';

describe('structured format conversion', () => {
  const value = {
    solver: {
      boundaries: [
        {name: 'left', voltage: 12},
        {name: 'right', voltage: 24},
      ],
    },
  };

  it('round-trips nested JSON values through YAML', () => {
    const text = serializeStructuredFormat(value, 'yaml');
    const parsed = parseStructuredFormat(text, 'yaml');

    expect(parsed.issues).toEqual([]);
    expect(parsed.value).toEqual(value);
    const trail = findSymbolTrail(parsed.roots, text.indexOf('24'));
    expect(trail.map(({symbol}) => symbol.name)).toEqual([
      'solver',
      'boundaries',
      '[1]',
      'voltage',
    ]);
  });

  it('round-trips objects and arrays of tables through TOML', () => {
    const text = serializeStructuredFormat(value, 'toml');
    const parsed = parseStructuredFormat(text, 'toml');

    expect(parsed.issues).toEqual([]);
    expect(parsed.value).toEqual(value);
    const trail = findSymbolTrail(parsed.roots, text.lastIndexOf('24'));
    expect(trail.map(({symbol}) => symbol.name)).toEqual([
      'solver',
      'boundaries',
      '[1]',
      'voltage',
    ]);
  });

  it('preserves escaped YAML keys in breadcrumbs', () => {
    const text = '"quoted\\"key":\n  child: true\n';
    const parsed = parseStructuredFormat(text, 'yaml');
    expect(parsed.roots[0].name).toBe('quoted"key');
    expect(parsed.roots[0].children[0].name).toBe('child');
  });

  it('reports TOML-incompatible JSON without dropping values', () => {
    expect(findTomlCompatibilityIssue({solver: {value: null}})?.message).toContain('$.solver.value');
    expect(findTomlCompatibilityIssue([1, 2])?.message).toContain('root');
    expect(findTomlCompatibilityIssue({value: Number.MAX_SAFE_INTEGER + 1})?.message).toContain('safe integer');
  });

  it('rejects TOML-only dates and non-finite numbers', () => {
    const date = parseStructuredFormat('created = 1979-05-27T07:32:00Z\n', 'toml');
    const infinity = parseStructuredFormat('value = inf\n', 'toml');

    expect(date.issues[0].message).toContain('date or time');
    expect(infinity.issues[0].message).toContain('finite JSON number');
  });

  it('returns parser issues for invalid alternate drafts', () => {
    expect(parseStructuredFormat('value: [\n', 'yaml').issues.length).toBeGreaterThan(0);
    expect(parseStructuredFormat('value = [\n', 'toml').issues.length).toBeGreaterThan(0);
  });
});
