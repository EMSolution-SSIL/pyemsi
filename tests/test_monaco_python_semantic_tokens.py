"""Tests for Monaco Python semantic-highlighting rollout controls."""

from pyemsi.widgets.monaco_lsp._widget import _HTML
from pyemsi.widgets.monaco_lsp._config import (
    LSP_DEBUG_ENV,
    PY_SEMANTIC_FEATURE_ENV,
    build_python_lsp_launch_command,
    read_bool_env,
    read_str_env,
    semantic_theme_enabled,
)


def test_read_bool_env_truthy_values():
    env = {"A": "1", "B": "true", "C": "enabled", "D": "yes", "E": "on"}
    assert read_bool_env("A", env=env)
    assert read_bool_env("B", env=env)
    assert read_bool_env("C", env=env)
    assert read_bool_env("D", env=env)
    assert read_bool_env("E", env=env)


def test_read_bool_env_defaults_and_falsey_values():
    env = {"A": "0", "B": "no", "C": "disabled"}
    assert not read_bool_env("A", env=env)
    assert not read_bool_env("B", env=env)
    assert not read_bool_env("C", env=env)
    assert read_bool_env("MISSING", default=True, env=env)


def test_read_str_env_defaults_and_stripping():
    env = {"MODE": "  basic  ", "EMPTY": "   "}
    assert read_str_env("MODE", default="off", env=env) == "basic"
    assert read_str_env("EMPTY", default="off", env=env) == "off"
    assert read_str_env("MISSING", default="off", env=env) == "off"


def test_build_python_lsp_launch_command_uses_legacy_when_flag_off():
    env = {PY_SEMANTIC_FEATURE_ENV: "0"}
    command, mode = build_python_lsp_launch_command(
        9321,
        semantic_requested=True,
        basedpyright_executable="basedpyright-langserver",
        env=env,
    )
    assert mode == "legacy-pylsp"
    assert command[-4:] == ["pylsp", "--ws", "--port", "9321"]


def test_build_python_lsp_launch_command_defaults_to_relay_when_requested():
    command, mode = build_python_lsp_launch_command(
        9324,
        semantic_requested=True,
        basedpyright_executable="basedpyright-langserver",
        env={},
    )
    assert mode == "relay-basedpyright"
    assert "pyemsi.widgets.monaco_lsp._relay" in command


def test_build_python_lsp_launch_command_uses_legacy_when_basedpyright_missing():
    env = {PY_SEMANTIC_FEATURE_ENV: "1"}
    command, mode = build_python_lsp_launch_command(
        9322,
        semantic_requested=True,
        basedpyright_executable=None,
        env=env,
    )
    assert mode == "legacy-pylsp"
    assert command[-4:] == ["pylsp", "--ws", "--port", "9322"]


def test_build_python_lsp_launch_command_uses_relay_when_enabled():
    env = {PY_SEMANTIC_FEATURE_ENV: "1", LSP_DEBUG_ENV: "1"}
    exe = r"C:\venv\Scripts\basedpyright-langserver.exe"
    command, mode = build_python_lsp_launch_command(
        9323,
        semantic_requested=True,
        basedpyright_executable=exe,
        env=env,
    )
    assert mode == "relay-basedpyright"
    assert "pyemsi.widgets.monaco_lsp._relay" in command
    assert "--ws-port" in command
    assert "--debug" in command
    assert command[-3:] == ["--", exe, "--stdio"]


def test_semantic_theme_enabled_scoped_to_python_viewer():
    env = {PY_SEMANTIC_FEATURE_ENV: "1"}
    assert semantic_theme_enabled("python", semantic_requested=True, env=env)
    assert not semantic_theme_enabled("python", semantic_requested=False, env=env)
    assert not semantic_theme_enabled("json", semantic_requested=True, env=env)


def test_semantic_theme_enabled_defaults_on_when_requested():
    assert semantic_theme_enabled("python", semantic_requested=True, env={})


def test_embedded_monaco_html_includes_signature_help_preferred_top_hook():
    assert "function applySignatureHelpPreferredTopLayout()" in _HTML
    assert "function scheduleSignatureHelpLayout()" in _HTML
    assert ".parameter-hints-widget.pyemsi-prefer-top" in _HTML
