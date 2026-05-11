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


def test_convert_source_to_femap_dispatches_format_readers_and_femap_writers(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    calls = []

    def _capture_read_mesh(path):
        calls.append(("read_mesh", os.path.abspath(os.path.normpath(path))))
        return "mesh"

    def _capture_read_post(path):
        calls.append(("read_post", os.path.abspath(os.path.normpath(path))))
        return [{"time": 0.0}]

    def _capture_write_neu(path, mesh):
        calls.append(("write_neu", os.path.abspath(os.path.normpath(path)), mesh))

    def _capture_write_neu_post(path, steps, mode=None):
        calls.append(("write_neu_post", os.path.abspath(os.path.normpath(path)), steps, mode))

    monkeypatch.setattr("pyemsi.tools.source_to_femap.atlas.read_mesh", _capture_read_mesh)
    monkeypatch.setattr("pyemsi.tools.source_to_femap.atlas.read_post", _capture_read_post)
    monkeypatch.setattr("pyemsi.tools.source_to_femap.femap.write_mesh", _capture_write_neu)
    monkeypatch.setattr("pyemsi.tools.source_to_femap.femap.write_post", _capture_write_neu_post)

    config = load_source_to_femap_config(
        {
            "source_format": "atlas",
            "input_dir": str(input_dir),
            "overwrite": False,
            "mesh": "post_geom.atl",
            "mesh_output": str(input_dir / "mesh-output.neu"),
            "electric": "electric.atl",
            "electric_output": str(input_dir / "electric-output.neu"),
        }
    )

    written_paths = convert_source_to_femap(config)

    assert calls == [
        ("read_mesh", os.path.abspath(os.path.normpath(str(input_dir / "post_geom.atl")))),
        ("write_neu", os.path.abspath(os.path.normpath(str(input_dir / "mesh-output.neu"))), "mesh"),
        ("read_post", os.path.abspath(os.path.normpath(str(input_dir / "electric.atl")))),
        (
            "write_neu_post",
            os.path.abspath(os.path.normpath(str(input_dir / "electric-output.neu"))),
            [{"time": 0.0}],
            "components",
        ),
    ]
    assert written_paths == [
        os.path.abspath(os.path.normpath(str(input_dir / "mesh-output.neu"))),
        os.path.abspath(os.path.normpath(str(input_dir / "electric-output.neu"))),
    ]


def test_convert_source_to_femap_overwrites_selected_source_paths(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    calls = []

    def _capture_read_mesh(path):
        calls.append(("read_mesh", os.path.abspath(os.path.normpath(path))))
        return "mesh"

    def _capture_read_post(path):
        calls.append(("read_post", os.path.abspath(os.path.normpath(path))))
        return [{"time": 0.0}]

    def _capture_write_neu(path, mesh):
        calls.append(("write_neu", os.path.abspath(os.path.normpath(path)), mesh))

    def _capture_write_neu_post(path, steps, mode=None):
        calls.append(("write_neu_post", os.path.abspath(os.path.normpath(path)), steps, mode))

    monkeypatch.setattr("pyemsi.tools.source_to_femap.unv.read_unv", _capture_read_mesh)
    monkeypatch.setattr("pyemsi.tools.source_to_femap.unv.read_unv_post", _capture_read_post)
    monkeypatch.setattr("pyemsi.tools.source_to_femap.femap.write_neu", _capture_write_neu)
    monkeypatch.setattr("pyemsi.tools.source_to_femap.femap.write_neu_post", _capture_write_neu_post)

    config = load_source_to_femap_config(
        {
            "source_format": "unv",
            "input_dir": str(input_dir),
            "overwrite": True,
            "mesh": "post_geom",
            "current": "current",
        }
    )

    written_paths = convert_source_to_femap(config)

    assert calls == [
        ("read_mesh", os.path.abspath(os.path.normpath(str(input_dir / "post_geom")))),
        ("write_neu", os.path.abspath(os.path.normpath(str(input_dir / "post_geom"))), "mesh"),
        ("read_post", os.path.abspath(os.path.normpath(str(input_dir / "current")))),
        (
            "write_neu_post",
            os.path.abspath(os.path.normpath(str(input_dir / "current"))),
            [{"time": 0.0}],
            "components",
        ),
    ]
    assert written_paths == [
        os.path.abspath(os.path.normpath(str(input_dir / "post_geom"))),
        os.path.abspath(os.path.normpath(str(input_dir / "current"))),
    ]
