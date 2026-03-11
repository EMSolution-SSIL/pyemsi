"""Tests for Monaco LSP breadcrumb symbol helpers."""

from pyemsi.widgets.monaco_lsp._widget import (
    build_symbol_breadcrumb_items,
    find_containing_symbol_trail,
    normalize_lsp_document_symbols,
    normalize_uri_key,
    should_show_breadcrumbs,
)


def test_normalize_uri_key_canonicalizes_windows_file_uris():
    uri = "file:///C%3A/Users/Example/Project/main.py"
    assert normalize_uri_key(uri) == "file:///c:/users/example/project/main.py"


def test_normalize_lsp_document_symbols_preserves_hierarchical_symbols():
    symbols = [
        {
            "name": "Example",
            "detail": "class",
            "kind": 5,
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 9, "character": 0},
            },
            "selectionRange": {
                "start": {"line": 0, "character": 6},
                "end": {"line": 0, "character": 13},
            },
            "children": [
                {
                    "name": "method",
                    "kind": 6,
                    "range": {
                        "start": {"line": 2, "character": 4},
                        "end": {"line": 4, "character": 16},
                    },
                    "selectionRange": {
                        "start": {"line": 2, "character": 8},
                        "end": {"line": 2, "character": 14},
                    },
                }
            ],
        }
    ]

    normalized = normalize_lsp_document_symbols(symbols, "file:///workspace/example.py")

    assert normalized[0]["name"] == "Example"
    assert normalized[0]["detail"] == "class"
    assert normalized[0]["children"][0]["name"] == "method"
    assert normalized[0]["children"][0]["selectionRange"]["startLineNumber"] == 3
    assert normalized[0]["children"][0]["selectionRange"]["startColumn"] == 9


def test_normalize_lsp_document_symbols_nests_flat_symbol_information():
    uri = "file:///workspace/example.py"
    symbols = [
        {
            "name": "Example",
            "kind": 5,
            "location": {
                "uri": uri,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 9, "character": 0},
                },
            },
        },
        {
            "name": "method",
            "kind": 6,
            "location": {
                "uri": uri,
                "range": {
                    "start": {"line": 2, "character": 4},
                    "end": {"line": 4, "character": 16},
                },
            },
        },
        {
            "name": "ignored",
            "kind": 13,
            "location": {
                "uri": "file:///workspace/other.py",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 5},
                },
            },
        },
    ]

    normalized = normalize_lsp_document_symbols(symbols, uri)

    assert [symbol["name"] for symbol in normalized] == ["Example"]
    assert [child["name"] for child in normalized[0]["children"]] == ["method"]
    assert normalized[0]["children"][0]["selectionRange"]["startLineNumber"] == 3


def test_find_containing_symbol_trail_returns_deepest_path():
    symbols = [
        {
            "name": "Example",
            "range": {
                "startLineNumber": 1,
                "startColumn": 1,
                "endLineNumber": 12,
                "endColumn": 1,
            },
            "selectionRange": {
                "startLineNumber": 1,
                "startColumn": 7,
                "endLineNumber": 1,
                "endColumn": 14,
            },
            "children": [
                {
                    "name": "method",
                    "range": {
                        "startLineNumber": 3,
                        "startColumn": 5,
                        "endLineNumber": 8,
                        "endColumn": 20,
                    },
                    "selectionRange": {
                        "startLineNumber": 3,
                        "startColumn": 9,
                        "endLineNumber": 3,
                        "endColumn": 15,
                    },
                    "children": [
                        {
                            "name": "inner",
                            "range": {
                                "startLineNumber": 5,
                                "startColumn": 9,
                                "endLineNumber": 6,
                                "endColumn": 18,
                            },
                            "selectionRange": {
                                "startLineNumber": 5,
                                "startColumn": 13,
                                "endLineNumber": 5,
                                "endColumn": 18,
                            },
                            "children": [],
                        }
                    ],
                }
            ],
        }
    ]

    trail = find_containing_symbol_trail(symbols, {"lineNumber": 5, "column": 12})

    assert [segment["name"] for segment in trail] == ["Example", "method", "inner"]


def test_build_symbol_breadcrumb_items_includes_siblings_for_each_level():
    symbols = [
        {
            "name": "Alpha",
            "range": {
                "startLineNumber": 1,
                "startColumn": 1,
                "endLineNumber": 20,
                "endColumn": 1,
            },
            "selectionRange": {
                "startLineNumber": 1,
                "startColumn": 7,
                "endLineNumber": 1,
                "endColumn": 12,
            },
            "children": [
                {
                    "name": "first_method",
                    "range": {
                        "startLineNumber": 3,
                        "startColumn": 5,
                        "endLineNumber": 6,
                        "endColumn": 18,
                    },
                    "selectionRange": {
                        "startLineNumber": 3,
                        "startColumn": 9,
                        "endLineNumber": 3,
                        "endColumn": 21,
                    },
                    "children": [],
                },
                {
                    "name": "second_method",
                    "range": {
                        "startLineNumber": 8,
                        "startColumn": 5,
                        "endLineNumber": 12,
                        "endColumn": 18,
                    },
                    "selectionRange": {
                        "startLineNumber": 8,
                        "startColumn": 9,
                        "endLineNumber": 8,
                        "endColumn": 22,
                    },
                    "children": [],
                },
            ],
        },
        {
            "name": "Beta",
            "range": {
                "startLineNumber": 22,
                "startColumn": 1,
                "endLineNumber": 30,
                "endColumn": 1,
            },
            "selectionRange": {
                "startLineNumber": 22,
                "startColumn": 7,
                "endLineNumber": 22,
                "endColumn": 11,
            },
            "children": [],
        },
    ]

    items = build_symbol_breadcrumb_items(symbols, {"lineNumber": 9, "column": 10})

    assert [item["symbol"]["name"] for item in items] == ["Alpha", "second_method"]
    assert [symbol["name"] for symbol in items[0]["siblings"]] == ["Alpha", "Beta"]
    assert [symbol["name"] for symbol in items[1]["siblings"]] == ["first_method", "second_method"]
    assert items[0]["isLeaf"] is False
    assert items[1]["isLeaf"] is True


def test_build_symbol_breadcrumb_items_fails_open_when_no_symbol_contains_position():
    symbols = [
        {
            "name": "Example",
            "range": {
                "startLineNumber": 1,
                "startColumn": 1,
                "endLineNumber": 3,
                "endColumn": 1,
            },
            "selectionRange": {
                "startLineNumber": 1,
                "startColumn": 1,
                "endLineNumber": 1,
                "endColumn": 8,
            },
            "children": [],
        }
    ]

    assert build_symbol_breadcrumb_items(symbols, {"lineNumber": 10, "column": 1}) == []


def test_build_symbol_breadcrumb_items_tracks_json_array_indexes():
    symbols = [
        {
            "name": "items",
            "detail": "array",
            "range": {
                "startLineNumber": 1,
                "startColumn": 1,
                "endLineNumber": 9,
                "endColumn": 2,
            },
            "selectionRange": {
                "startLineNumber": 1,
                "startColumn": 2,
                "endLineNumber": 1,
                "endColumn": 7,
            },
            "children": [
                {
                    "name": "[0]",
                    "detail": "object",
                    "range": {
                        "startLineNumber": 2,
                        "startColumn": 3,
                        "endLineNumber": 4,
                        "endColumn": 4,
                    },
                    "selectionRange": {
                        "startLineNumber": 2,
                        "startColumn": 3,
                        "endLineNumber": 2,
                        "endColumn": 4,
                    },
                    "children": [
                        {
                            "name": "name",
                            "detail": "",
                            "range": {
                                "startLineNumber": 3,
                                "startColumn": 5,
                                "endLineNumber": 3,
                                "endColumn": 20,
                            },
                            "selectionRange": {
                                "startLineNumber": 3,
                                "startColumn": 6,
                                "endLineNumber": 3,
                                "endColumn": 10,
                            },
                            "children": [],
                        }
                    ],
                },
                {
                    "name": "[1]",
                    "detail": "number",
                    "range": {
                        "startLineNumber": 5,
                        "startColumn": 3,
                        "endLineNumber": 5,
                        "endColumn": 4,
                    },
                    "selectionRange": {
                        "startLineNumber": 5,
                        "startColumn": 3,
                        "endLineNumber": 5,
                        "endColumn": 4,
                    },
                    "children": [],
                },
            ],
        }
    ]

    items = build_symbol_breadcrumb_items(symbols, {"lineNumber": 3, "column": 8})

    assert [item["symbol"]["name"] for item in items] == ["items", "[0]", "name"]
    assert [symbol["name"] for symbol in items[1]["siblings"]] == ["[0]", "[1]"]
    assert items[2]["isLeaf"] is True


def test_normalize_lsp_document_symbols_fails_open_for_empty_or_unsupported_payloads():
    assert normalize_lsp_document_symbols(None, "file:///workspace/example.py") == []
    assert normalize_lsp_document_symbols([], "file:///workspace/example.py") == []
    assert normalize_lsp_document_symbols(["bad"], "file:///workspace/example.py") == []


def test_should_show_breadcrumbs_requires_matching_symbol_capable_language():
    symbols = [{"name": "Example"}]

    assert should_show_breadcrumbs("python", "python", True, symbols) is True
    assert should_show_breadcrumbs("json", "json", True, symbols) is True
    assert should_show_breadcrumbs("markdown", "python", True, symbols) is False
    assert should_show_breadcrumbs("python", "python", False, symbols) is False


def test_should_show_breadcrumbs_requires_non_empty_symbols():
    assert should_show_breadcrumbs("python", "python", True, []) is False
    assert should_show_breadcrumbs("python", "python", True, None) is False
