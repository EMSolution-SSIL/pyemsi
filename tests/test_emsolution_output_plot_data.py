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
