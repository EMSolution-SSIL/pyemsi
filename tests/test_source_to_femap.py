import os

from pyemsi.tools.source_to_femap import convert_source_to_femap, load_source_to_femap_config


def test_load_source_to_femap_config_uses_source_paths_when_overwriting(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    config = load_source_to_femap_config(
        {
            "source_format": "atlas",
            "input_dir": str(input_dir),
            "overwrite": True,
            "mesh": "post_geom.atl",
            "magnetic": os.path.join("nested", "magnetic.atl"),
        }
    )

    assert config.mesh.output_path == os.path.abspath(os.path.normpath(str(input_dir / "post_geom.atl")))
    assert config.magnetic is not None
    assert config.magnetic.output_path == os.path.abspath(os.path.normpath(str(input_dir / "nested" / "magnetic.atl")))


def test_load_source_to_femap_config_preserves_extensionless_paths_when_overwriting(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    config = load_source_to_femap_config(
        {
            "source_format": "unv",
            "input_dir": str(input_dir),
            "overwrite": True,
            "mesh": "post_geom",
            "current": "current",
        }
    )

    assert config.mesh.output_path == os.path.abspath(os.path.normpath(str(input_dir / "post_geom")))
    assert config.current is not None
    assert config.current.output_path == os.path.abspath(os.path.normpath(str(input_dir / "current")))


def test_load_source_to_femap_config_defaults_custom_outputs_when_overwrite_disabled(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    config = load_source_to_femap_config(
        {
            "source_format": "unv",
            "input_dir": str(input_dir),
            "overwrite": False,
            "mesh": "post_geom.unv",
            "current": "current.unv",
        }
    )

    assert config.mesh.output_path == os.path.abspath(os.path.normpath(str(input_dir / "post_geom")))
    assert config.current is not None
    assert config.current.output_path == os.path.abspath(os.path.normpath(str(input_dir / "current")))


def test_load_source_to_femap_config_defaults_extensionless_output_to_same_name(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    config = load_source_to_femap_config(
        {
            "source_format": "atlas",
            "input_dir": str(input_dir),
            "overwrite": False,
            "mesh": "post_geom",
            "current": "current",
        }
    )

    assert config.mesh.output_path == os.path.abspath(os.path.normpath(str(input_dir / "post_geom")))
    assert config.current is not None
    assert config.current.output_path == os.path.abspath(os.path.normpath(str(input_dir / "current")))


def test_load_source_to_femap_config_resolves_relative_custom_outputs_from_input_dir(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    config = load_source_to_femap_config(
        {
            "source_format": "atlas",
            "input_dir": str(input_dir),
            "overwrite": False,
            "mesh": "post_geom.atl",
            "mesh_output": os.path.join("exports", "post_geom_custom.neu"),
        }
    )

    assert config.mesh.output_path == os.path.abspath(
        os.path.normpath(str(input_dir / "exports" / "post_geom_custom.neu"))
    )
