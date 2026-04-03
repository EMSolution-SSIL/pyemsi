import json

from pyemsi.io import EMSolutionOutput


def _sample_payload():
    return {
        "metaData": {
            "EMSolutionVersion": "1.0",
            "releaseDate": "2026-01-01",
            "creationDate": "2026-01-02",
            "comments": "example",
        },
        "analysisCondition": {
            "analysisType": "TRANSIENT",
            "nonlinear": "LINEAR",
            "motionType": "SLIDE_MOTION",
            "circuitType": "NETWORK",
        },
        "timeStep": {
            "time": [0.0, 1.0, 2.0],
            "timeUnit": "s",
            "position": [[0.0, 10.0, 20.0]],
            "positionUnit": "deg",
            "motionDirection": "CW",
        },
        "postData": {
            "circuit": {
                "circuitUnit": ["A", "V", "Wb"],
                "sourceData": [
                    {
                        "serialNum": 1,
                        "current": [1.0, 2.0, 3.0],
                        "voltage": [10.0, 20.0, 30.0],
                        "flux": [0.1, 0.2, 0.3],
                    }
                ],
                "powerSourceData": [
                    {
                        "serialNum": 2,
                        "current": [4.0, 5.0, 6.0],
                        "voltage": [40.0, 50.0, 60.0],
                    }
                ],
            },
            "network": {
                "networkUnit": ["A", "V", "Wb"],
                "networkData": [
                    {
                        "elementNum": 7,
                        "elementName": "Coil",
                        "current": [0.4, 0.5, 0.6],
                        "voltage": [4.0, 5.0, 6.0],
                        "flux": [0.01, 0.02, 0.03],
                    }
                ],
            },
            "forceNodal": {
                "forceUnit": ["N", "Nm"],
                "forceNodalData": [
                    {
                        "propertyNum": 12,
                        "forceX": [1.0, 1.1, 1.2],
                        "forceY": [2.0, 2.1, 2.2],
                        "forceZ": [3.0, 3.1, 3.2],
                        "forceMX": [4.0, 4.1, 4.2],
                        "forceMY": [5.0, 5.1, 5.2],
                        "forceMZ": [6.0, 6.1, 6.2],
                    }
                ],
            },
        },
    }


def test_emsolution_output_lists_plot_x_options():
    result = EMSolutionOutput.from_dict(_sample_payload())

    options = result.get_plot_x_options()

    assert [option.key for option in options] == ["time", "position"]
    assert options[0].axis_label == "Time (s)"
    assert options[1].axis_label == "Position (deg)"


def test_emsolution_output_lists_plot_series_with_expected_labels():
    result = EMSolutionOutput.from_dict(_sample_payload())

    series = result.get_plot_series()
    labels = {entry.label for entry in series}

    assert "Source #1 Current" in labels
    assert "Source #1 Flux" in labels
    assert "Power Source #2 Voltage" in labels
    assert "Coil #7 Current" in labels
    assert "Property #12 Moment Z" in labels
    assert len(series) == 14


def test_emsolution_output_plot_series_preserve_tree_paths_and_units():
    result = EMSolutionOutput.from_dict(_sample_payload())

    force_y = next(entry for entry in result.get_plot_series() if entry.label == "Property #12 Force Y")

    assert force_y.tree_path == ("Force Nodal", "Property #12", "Force Y")
    assert force_y.axis_label == "Force Y (N)"
    assert force_y.values.tolist() == [2.0, 2.1, 2.2]


def test_emsolution_output_repr_is_tree_shaped():
    result = EMSolutionOutput.from_dict(_sample_payload())
    r = repr(result)

    assert r.startswith("EMSolutionOutput")
    assert "├──" in r or "└──" in r
    assert "ndarray[3]" in r
    # raw arrays must not appear
    assert "[0.0, 1.0, 2.0]" not in r


def test_emsolution_output_repr_contains_leaf_identifiers():
    result = EMSolutionOutput.from_dict(_sample_payload())
    r = repr(result)

    assert "Source #1" in r
    assert "Power Source #2" in r or "power_sources" in r
    assert "Coil #7" in r
    assert "Property #12" in r


def test_emsolution_output_repr_contains_units_and_condition():
    result = EMSolutionOutput.from_dict(_sample_payload())
    r = repr(result)

    assert "A/V/Wb" in r  # circuit/network units
    assert "N/Nm" in r  # force_nodal units
    assert "TRANSIENT" in r
    assert "SLIDE_MOTION" in r
    assert "deg" in r  # position unit
    assert "CW" in r  # motion direction


def test_circuit_element_repr_summarises_arrays():
    result = EMSolutionOutput.from_dict(_sample_payload())
    el = result.circuit.sources[0]
    r = repr(el)

    assert "Source #1" in r
    assert "ndarray[3]" in r
    assert "current=" in r
    assert "voltage=" in r
    assert "flux=" in r
    assert "[1.0, 2.0, 3.0]" not in r  # no raw list values


def test_network_element_repr_summarises_arrays():
    result = EMSolutionOutput.from_dict(_sample_payload())
    el = result.network.elements[0]
    r = repr(el)

    assert "Coil #7" in r
    assert "ndarray[3]" in r
    assert "[0.4, 0.5, 0.6]" not in r  # no raw list values


def test_force_nodal_entry_repr_summarises_arrays():
    result = EMSolutionOutput.from_dict(_sample_payload())
    en = result.force_nodal.entries[0]
    r = repr(en)

    assert "Property #12" in r
    assert "Fx=" in r
    assert "Mz=" in r
    assert "ndarray[3]" in r
    assert "[1.0, 1.1, 1.2]" not in r  # no raw list values
