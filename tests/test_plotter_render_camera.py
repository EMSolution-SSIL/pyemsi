import numpy as np

from pyemsi.plotter.plotter import Plotter


class _FakeActor:
    def SetVisibility(self, _visible):
        return None


class _FakeDerivedMesh:
    def __init__(self, n_points=1):
        self.n_points = n_points


class _FakeBlock:
    def __init__(self):
        self.n_points = 2
        self.array_names = ["scalar", "vector"]
        self._arrays = {
            "scalar": np.array([0.0, 1.0]),
            "vector": np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        }

    def __getitem__(self, key):
        return self._arrays[key]

    def extract_feature_edges(self):
        return _FakeDerivedMesh()

    def contour(self, isosurfaces, scalars):
        assert scalars == "scalar"
        assert len(isosurfaces) >= 1
        return _FakeDerivedMesh()

    def glyph(self, **_kwargs):
        return _FakeDerivedMesh()


class _FakeReader:
    def __init__(self, block):
        self._block = block
        self.read_calls = 0

    def read(self):
        self.read_calls += 1
        return self._block


class _FakeScenePlotter:
    def __init__(self):
        self.add_mesh_calls = []
        self.render_calls = 0
        self.suppress_rendering = False

    def add_mesh(self, mesh, **kwargs):
        self.add_mesh_calls.append({"mesh": mesh, "kwargs": kwargs})
        return _FakeActor()

    def render(self):
        self.render_calls += 1


def test_render_replots_without_resetting_camera():
    block = _FakeBlock()
    scene_plotter = _FakeScenePlotter()

    plotter = Plotter.__new__(Plotter)
    plotter._notebook = True
    plotter._window = None
    plotter._mesh = block
    plotter.reader = _FakeReader(block)
    plotter.plotter = scene_plotter
    plotter._feature_edges_props = {"color": "white", "line_width": 1, "opacity": 1.0}
    plotter._scalar_props = {"name": "scalar", "mode": "node"}
    plotter._contour_props = {"name": "scalar", "n_contours": 2, "color": "red", "line_width": 3}
    plotter._vector_props = {
        "name": "vector",
        "scale": False,
        "glyph_type": "arrow",
        "factor": 1.0,
        "tolerance": None,
        "color_mode": "scale",
    }
    plotter._block_visibility = {}

    plotter.render()

    assert plotter.reader.read_calls >= 1
    assert scene_plotter.render_calls == 1
    assert len(scene_plotter.add_mesh_calls) == 4
    assert all(call["kwargs"].get("reset_camera") is False for call in scene_plotter.add_mesh_calls)
    assert scene_plotter.suppress_rendering is False
