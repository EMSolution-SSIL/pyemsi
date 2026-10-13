"""Canonical material records (ems_material JSON v1) for the addon tests."""

STEEL = {
    "general": {"density": {"type": "scalar", "value": 7650, "unit": "kg/m^3"}},
    "electromagnetic": {
        "BH_curve": {
            "type": "curve",
            "x": {"name": "H", "unit": "A/m", "values": [0, 100, 1000]},
            "y": {"name": "B", "unit": "T", "values": [0, 1, 1.5]},
        },
        "electrical_conductivity": {"type": "scalar", "value": 2e6, "unit": "S/m"},
        "iron_loss_ke": {"type": "scalar", "value": 5e-5, "unit": "W/kg/T^2/Hz^2"},
        "iron_loss_kh": {"type": "scalar", "value": 0.02, "unit": "W/kg/T^2/Hz"},
    },
}
COPPER = {"electromagnetic": {"electrical_conductivity": {"type": "scalar", "value": 5.8e7, "unit": "S/m"}}}
AIR = {"electromagnetic": {"relative_permeability": {"type": "scalar", "value": 1, "unit": "1"}}}


def record(material_id, name, family="generic", properties=None, version="1.0.0"):
    return {
        "schema": "ems_material",
        "schema_version": "1.0",
        "material_id": material_id,
        "material_version": version,
        "identity": {
            "name": name,
            "family": family,
            "manufacturer": None,
            "grade": None,
            "description": None,
            "aliases": [],
            "tags": [],
        },
        "properties": properties or {},
        "provenance": {"source_type": "USER_INPUT", "reference": None, "date": None, "notes": None},
        "version_metadata": {"author": "test", "updated_at": "2026-10-13T00:00:00+00:00", "change_note": "fixture"},
    }
