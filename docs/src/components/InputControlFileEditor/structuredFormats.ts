import {
  isMap,
  isPair,
  isSeq,
  parseDocument,
  stringify as stringifyYaml,
  type Node as YamlNode,
  type Pair as YamlPair,
} from 'yaml';
import {stringify as stringifyToml} from 'smol-toml';
import {
  type AST,
  getStaticTOMLValue,
  ParseError as TomlParseError,
  parseTOML,
} from 'toml-eslint-parser';

import {
  buildJsonSymbolTree,
  type StructuredSymbol,
} from './jsonSymbols';

export type EditorFormat = 'json' | 'yaml' | 'toml';

export interface FormatIssue {
  message: string;
  offset: number;
  length: number;
}

export interface ParsedFormat {
  value?: unknown;
  roots: StructuredSymbol[];
  issues: FormatIssue[];
}

export interface CompatibilityIssue {
  message: string;
  path: Array<string | number>;
}

export const FORMAT_LABELS: Record<EditorFormat, string> = {
  json: 'JSON',
  yaml: 'YAML',
  toml: 'TOML',
};

function pathLabel(path: Array<string | number>): string {
  if (path.length === 0) return '$';
  return path.reduce<string>((result, segment) => (
    typeof segment === 'number'
      ? `${result}[${segment}]`
      : `${result}.${segment}`
  ), '$');
}

function valueDetail(value: unknown): string {
  if (Array.isArray(value)) {
    return `${value.length} ${value.length === 1 ? 'item' : 'items'}`;
  }
  if (isPlainObject(value)) {
    const count = Object.keys(value).length;
    return `${count} ${count === 1 ? 'property' : 'properties'}`;
  }
  if (typeof value === 'string') {
    return value.length > 36 ? `“${value.slice(0, 33)}…”` : `“${value}”`;
  }
  return String(value);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  if (value === null || typeof value !== 'object') return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

export function findJsonCompatibilityIssue(
  value: unknown,
  path: Array<string | number> = [],
  seen = new Set<object>(),
): CompatibilityIssue | undefined {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') {
    return undefined;
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) {
      return {message: `${pathLabel(path)} is not a finite JSON number.`, path};
    }
    if (Number.isInteger(value) && !Number.isSafeInteger(value)) {
      return {message: `${pathLabel(path)} is outside JavaScript's safe integer range.`, path};
    }
    return undefined;
  }
  if (typeof value !== 'object') {
    return {message: `${pathLabel(path)} contains an unsupported ${typeof value} value.`, path};
  }
  if (value instanceof Date) {
    return {message: `${pathLabel(path)} is a TOML date or time, which cannot round-trip to JSON without changing type.`, path};
  }
  if (seen.has(value)) {
    return {message: `${pathLabel(path)} contains a circular reference.`, path};
  }
  seen.add(value);
  const entries: Array<[string | number, unknown]> = Array.isArray(value)
    ? value.map((item, index) => [index, item])
    : isPlainObject(value)
      ? Object.entries(value)
      : [];
  if (!Array.isArray(value) && !isPlainObject(value)) {
    seen.delete(value);
    return {message: `${pathLabel(path)} is not a plain JSON object.`, path};
  }
  for (const [key, child] of entries) {
    const issue = findJsonCompatibilityIssue(child, [...path, key], seen);
    if (issue) return issue;
  }
  seen.delete(value);
  return undefined;
}

export function findTomlCompatibilityIssue(value: unknown): CompatibilityIssue | undefined {
  if (!isPlainObject(value)) {
    return {message: 'TOML requires the JSON document root to be an object.', path: []};
  }
  function find(current: unknown, path: Array<string | number>): CompatibilityIssue | undefined {
    if (current === null) {
      return {message: `${pathLabel(path)} is null, which TOML cannot represent.`, path};
    }
    const jsonIssue = findJsonCompatibilityIssue(current, path);
    if (jsonIssue) return jsonIssue;
    if (Array.isArray(current)) {
      for (let index = 0; index < current.length; index += 1) {
        const issue = find(current[index], [...path, index]);
        if (issue) return issue;
      }
    } else if (isPlainObject(current)) {
      for (const [key, child] of Object.entries(current)) {
        const issue = find(child, [...path, key]);
        if (issue) return issue;
      }
    }
    return undefined;
  }
  return find(value, []);
}

function yamlNodeRange(node: YamlNode | null | undefined): [number, number] {
  const range = node?.range;
  return range ? [range[0], Math.max(range[1], range[0] + 1)] : [0, 1];
}

function yamlValue(node: YamlNode | null | undefined): unknown {
  if (!node) return null;
  return node.toJSON();
}

function yamlSymbols(node: YamlNode | null | undefined): StructuredSymbol[] {
  if (isMap(node)) {
    return node.items.flatMap((item, index) => {
      if (!isPair(item)) return [];
      const pair = item as YamlPair<YamlNode, YamlNode>;
      const key = String(yamlValue(pair.key));
      const [keyStart, keyEnd] = yamlNodeRange(pair.key);
      const [, valueEnd] = yamlNodeRange(pair.value);
      return [{
        id: `${keyStart}:${index}`,
        name: key,
        detail: valueDetail(yamlValue(pair.value)),
        offset: keyStart,
        length: Math.max(valueEnd - keyStart, keyEnd - keyStart, 1),
        selectionOffset: keyStart,
        children: yamlSymbols(pair.value),
      }];
    });
  }
  if (isSeq(node)) {
    return node.items.map((item, index) => {
      const child = item as YamlNode | null;
      const [start, end] = yamlNodeRange(child);
      return {
        id: `${start}:${index}`,
        name: `[${index}]`,
        detail: valueDetail(yamlValue(child)),
        offset: start,
        length: Math.max(end - start, 1),
        selectionOffset: start,
        children: yamlSymbols(child),
      };
    });
  }
  return [];
}

function parseYaml(text: string): ParsedFormat {
  const document = parseDocument(text, {
    keepSourceTokens: true,
    logLevel: 'silent',
    version: '1.2',
  });
  const issues = document.errors.map((error) => ({
    message: error.message,
    offset: error.pos[0] ?? 0,
    length: Math.max((error.pos[1] ?? error.pos[0] ?? 0) - (error.pos[0] ?? 0), 1),
  }));
  if (issues.length > 0) {
    return {roots: yamlSymbols(document.contents), issues};
  }
  try {
    const value = document.toJSON();
    const compatibility = findJsonCompatibilityIssue(value);
    if (compatibility) {
      return {roots: yamlSymbols(document.contents), issues: [{message: compatibility.message, offset: 0, length: 1}]};
    }
    return {value, roots: yamlSymbols(document.contents), issues: []};
  } catch (error) {
    return {
      roots: [],
      issues: [{message: error instanceof Error ? error.message : 'YAML could not be converted to JSON.', offset: 0, length: 1}],
    };
  }
}

type TomlLocation = {offset: number; length: number; selectionOffset: number};

function tomlPathKey(path: Array<string | number>): string {
  return JSON.stringify(path);
}

function tomlKeyParts(key: AST.TOMLKey): string[] {
  return key.keys.map((part) => part.type === 'TOMLBare' ? part.name : part.value);
}

function collectTomlLocations(ast: AST.TOMLProgram): Map<string, TomlLocation> {
  const locations = new Map<string, TomlLocation>();
  const add = (path: Array<string | number>, node: AST.TOMLNode, selectionOffset = node.range[0]) => {
    locations.set(tomlPathKey(path), {
      offset: node.range[0],
      length: Math.max(node.range[1] - node.range[0], 1),
      selectionOffset,
    });
  };
  const visitContent = (node: AST.TOMLContentNode, path: Array<string | number>) => {
    add(path, node);
    if (node.type === 'TOMLArray') {
      node.elements.forEach((element, index) => visitContent(element, [...path, index]));
    } else if (node.type === 'TOMLInlineTable') {
      node.body.forEach((entry) => visitKeyValue(entry, path));
    }
  };
  const visitKeyValue = (node: AST.TOMLKeyValue, basePath: Array<string | number>) => {
    const parts = tomlKeyParts(node.key);
    const path = [...basePath, ...parts];
    add(path, node, node.key.range[0]);
    visitContent(node.value, path);
  };
  for (const node of ast.body[0].body) {
    if (node.type === 'TOMLKeyValue') {
      visitKeyValue(node, []);
    } else {
      add(node.resolvedKey, node, node.key.range[0]);
      node.body.forEach((entry) => visitKeyValue(entry, node.resolvedKey));
    }
  }
  return locations;
}

function symbolsFromValue(
  value: unknown,
  locations: Map<string, TomlLocation>,
  path: Array<string | number> = [],
): StructuredSymbol[] {
  const entries: Array<[string | number, unknown]> = Array.isArray(value)
    ? value.map((item, index) => [index, item])
    : isPlainObject(value)
      ? Object.entries(value)
      : [];
  return entries.map(([key, child], index) => {
    const childPath = [...path, key];
    const children = symbolsFromValue(child, locations, childPath);
    const exactLocation = locations.get(tomlPathKey(childPath));
    const firstChild = children[0];
    const lastChild = children.at(-1);
    const location = exactLocation ?? (firstChild && lastChild ? {
      offset: firstChild.offset,
      length: Math.max(lastChild.offset + lastChild.length - firstChild.offset, 1),
      selectionOffset: firstChild.selectionOffset,
    } : {offset: 0, length: 1, selectionOffset: 0});
    return {
      id: `${location.offset}:${index}:${String(key)}`,
      name: typeof key === 'number' ? `[${key}]` : key,
      detail: valueDetail(child),
      ...location,
      children,
    };
  });
}

function parseToml(text: string): ParsedFormat {
  try {
    const ast = parseTOML(text, {tomlVersion: '1.0.0'});
    const value = getStaticTOMLValue(ast);
    const compatibility = findTomlCompatibilityIssue(value);
    const roots = symbolsFromValue(value, collectTomlLocations(ast));
    if (compatibility) {
      return {roots, issues: [{message: compatibility.message, offset: 0, length: 1}]};
    }
    return {value, roots, issues: []};
  } catch (error) {
    if (error instanceof TomlParseError) {
      return {roots: [], issues: [{message: error.message, offset: error.index, length: 1}]};
    }
    return {
      roots: [],
      issues: [{message: error instanceof Error ? error.message : 'TOML could not be parsed.', offset: 0, length: 1}],
    };
  }
}

function parseJson(text: string): ParsedFormat {
  const tree = buildJsonSymbolTree(text);
  if (tree.errors.length > 0) {
    return {
      roots: tree.roots,
      issues: tree.errors.map((error) => ({message: `Invalid JSON (error ${error.error}).`, offset: error.offset, length: Math.max(error.length, 1)})),
    };
  }
  try {
    return {value: JSON.parse(text), roots: tree.roots, issues: []};
  } catch (error) {
    return {roots: tree.roots, issues: [{message: error instanceof Error ? error.message : 'Invalid JSON.', offset: 0, length: 1}]};
  }
}

export function parseStructuredFormat(text: string, format: EditorFormat): ParsedFormat {
  if (format === 'yaml') return parseYaml(text);
  if (format === 'toml') return parseToml(text);
  return parseJson(text);
}

export function serializeStructuredFormat(value: unknown, format: EditorFormat): string {
  const compatibility = findJsonCompatibilityIssue(value);
  if (compatibility) throw new Error(compatibility.message);
  if (format === 'json') return `${JSON.stringify(value, null, 2)}\n`;
  if (format === 'yaml') return stringifyYaml(value, {indent: 2, lineWidth: 0});
  const tomlIssue = findTomlCompatibilityIssue(value);
  if (tomlIssue) throw new Error(tomlIssue.message);
  return stringifyToml(value as Record<string, unknown>);
}

export function formatStructuredText(text: string, format: EditorFormat): string {
  const parsed = parseStructuredFormat(text, format);
  if (parsed.value === undefined || parsed.issues.length > 0) {
    throw new Error(parsed.issues[0]?.message ?? `Invalid ${FORMAT_LABELS[format]}.`);
  }
  return serializeStructuredFormat(parsed.value, format);
}
