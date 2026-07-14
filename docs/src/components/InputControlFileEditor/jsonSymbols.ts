import {
  type Node as JsonNode,
  type ParseError,
  parseTree,
} from 'jsonc-parser';

export interface JsonSymbol {
  id: string;
  name: string;
  detail: string;
  offset: number;
  length: number;
  selectionOffset: number;
  children: JsonSymbol[];
}

export interface JsonSymbolLevel {
  symbol: JsonSymbol;
  siblings: JsonSymbol[];
  children: JsonSymbol[];
}

export interface JsonSymbolTree {
  roots: JsonSymbol[];
  errors: ParseError[];
}

function primitiveDetail(node: JsonNode): string {
  if (node.type === 'object') {
    const count = node.children?.length ?? 0;
    return `${count} ${count === 1 ? 'property' : 'properties'}`;
  }
  if (node.type === 'array') {
    const count = node.children?.length ?? 0;
    return `${count} ${count === 1 ? 'item' : 'items'}`;
  }
  if (node.type === 'string') {
    const value = String(node.value ?? '');
    return value.length > 36 ? `“${value.slice(0, 33)}…”` : `“${value}”`;
  }
  return String(node.value ?? node.type);
}

function symbolsForValue(node: JsonNode): JsonSymbol[] {
  if (node.type === 'object') {
    return (node.children ?? []).flatMap((property, index) => {
      const keyNode = property.children?.[0];
      const valueNode = property.children?.[1];
      if (!keyNode || !valueNode) {
        return [];
      }
      return [{
        id: `${property.offset}:${index}`,
        name: String(keyNode.value ?? '(property)'),
        detail: primitiveDetail(valueNode),
        offset: property.offset,
        length: Math.max(property.length, 1),
        selectionOffset: keyNode.offset,
        children: symbolsForValue(valueNode),
      }];
    });
  }

  if (node.type === 'array') {
    return (node.children ?? []).map((child, index) => ({
      id: `${child.offset}:${index}`,
      name: `[${index}]`,
      detail: primitiveDetail(child),
      offset: child.offset,
      length: Math.max(child.length, 1),
      selectionOffset: child.offset,
      children: symbolsForValue(child),
    }));
  }

  return [];
}

export function buildJsonSymbolTree(text: string): JsonSymbolTree {
  const errors: ParseError[] = [];
  const root = parseTree(text, errors, {
    allowTrailingComma: false,
    disallowComments: true,
  });

  return {
    roots: root ? symbolsForValue(root) : [],
    errors,
  };
}

function containsOffset(symbol: JsonSymbol, offset: number): boolean {
  return offset >= symbol.offset && offset <= symbol.offset + symbol.length;
}

export function findJsonSymbolTrail(
  roots: JsonSymbol[],
  offset: number,
): JsonSymbolLevel[] {
  function find(symbols: JsonSymbol[]): JsonSymbolLevel[] {
    for (const symbol of symbols) {
      if (!containsOffset(symbol, offset)) {
        continue;
      }
      const childTrail = find(symbol.children);
      return [{symbol, siblings: symbols, children: symbol.children}, ...childTrail];
    }
    return [];
  }

  return find(roots);
}

export function uniqueDisplayName(
  filename: string,
  existingDisplayNames: string[],
): string {
  if (!existingDisplayNames.includes(filename)) {
    return filename;
  }

  let suffix = 2;
  while (existingDisplayNames.includes(`${filename} (${suffix})`)) {
    suffix += 1;
  }
  return `${filename} (${suffix})`;
}

export function editorWindowTitle(
  primaryName?: string,
  comparisonName?: string,
): string {
  if (!primaryName) {
    return 'Input Control File Editor | pyemsi';
  }
  if (comparisonName) {
    return `${primaryName} ↔ ${comparisonName} — Input Control File Editor | pyemsi`;
  }
  return `${primaryName} — Input Control File Editor | pyemsi`;
}
