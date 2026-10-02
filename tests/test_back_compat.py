"""Backward-compatibility shim: get_preset_as_legacy_dict matches em_sdm.manufacturing shape.

The legacy ``em_sdm.manufacturing.PRESETS`` returned a dict per preset with
these keys (mm units, no provenance):

    description, d_voxel_size, d_min_wall_mm, d_min_clearance_mm,
    d_min_feature_mm, default_material (optional), notes (optional)

This shim preserves that exact shape for consumers that haven't migrated.
"""

from __future__ import annotations

import pytest

from emergent_matter_processes import (
    PRESETS,
    get_preset_as_legacy_dict,
)


def test_legacy_dict_has_required_keys():
    d = get_preset_as_legacy_dict("sls_pa12")
    for key in (
        "description",
        "d_voxel_size",
        "d_min_wall_mm",
        "d_min_clearance_mm",
        "d_min_feature_mm",
    ):
        assert key in d, f"missing key {key!r}"


def test_legacy_dict_values_are_in_millimeters():
    """The legacy API used mm; the substrate stores in m. Conversion at
    accessor time must produce the expected mm values.

    Values updated for v0.1.1 verified-facts patch:
    - min_clearance: 1.0 mm -> 0.3 mm (Nylon 12 integrated assembly per
      Formlabs Design Guide; 1.0 mm was wrongly imported Nylon 11 / TPU
      guidance in v0.1.0)
    - min_feature_size: 0.5 mm -> 0.3 mm (Formlabs's actual Nylon 12
      engraved-horizontal-width minimum)
    """
    d = get_preset_as_legacy_dict("formlabs_fuse1_pa12")
    assert d["d_voxel_size"] == pytest.approx(0.15)  # mm
    assert d["d_min_wall_mm"] == pytest.approx(0.6)
    assert d["d_min_clearance_mm"] == pytest.approx(0.3)  # v0.1.1
    assert d["d_min_feature_mm"] == pytest.approx(0.3)  # v0.1.1


def test_legacy_dict_includes_default_material_when_present():
    d = get_preset_as_legacy_dict("sls_pa12")
    assert d["default_material"] == "nylon12_sls"


def test_legacy_dict_includes_notes_when_present():
    d = get_preset_as_legacy_dict("prusa_core_one")
    assert "notes" in d
    assert "250" in d["notes"]  # build volume mentioned in notes


def test_legacy_dict_omits_optional_when_absent():
    """Some presets have empty notes; the key should be absent."""
    # SLS PA12 has a default_material but if a preset's notes are empty
    # the legacy dict should omit the key. We don't currently have such
    # a preset in v0.1.0 (every entry has both fields populated), so
    # this test asserts the omission behaviour via a unit-level probe
    # against the dict builder.
    from emergent_matter_processes.accessors import get_preset_as_legacy_dict

    # Walk the catalog; for any preset with empty notes, the key must be absent.

    for s_id, p in PRESETS.items():
        d = get_preset_as_legacy_dict(s_id)
        if not p.s_notes:
            assert "notes" not in d, f"{s_id}: empty notes leaked into dict"
        if not p.s_default_material:
            assert "default_material" not in d, f"{s_id}: empty default_material leaked into dict"


def test_legacy_dict_returns_verified_v011_values():
    """Lock down the v0.1.1 verified-correct values returned by the
    legacy-dict shim. This is the regression gate against future drift.

    Originally this test was test_legacy_em_sdm_value_parity, asserting
    bit-for-bit parity with the old em_sdm.manufacturing.PRESETS dict.
    The 2026-05-24 triple-source audit revealed em_sdm had several
    wrong values (Formlabs min_clearance was Nylon 11 guidance, SLS
    generic clearances were unsourced, etc.), so "faithful port" no
    longer means "correct." The test was renamed and the snapshot
    updated to the v0.1.1 verified values.

    Pre-audit em_sdm values that v0.1.1 corrected (for historical record):
      formlabs_fuse1_pa12: min_clearance 1.0 -> 0.3 mm, min_feature 0.5 -> 0.3 mm
      sls_pa12 / sls_pa11: min_clearance 0.15 -> 0.3 mm, min_feature 0.5 -> 0.8 mm
      fdm_pla / fdm_abs / fdm_petg: min_wall 0.9 -> 0.8 mm, min_clearance 0.2 -> 0.3 mm
    """
    # v0.1.1 verified values per the triple-source audit. If any of these
    # drift in a future patch without a deliberate value-update commit,
    # this test catches it.
    verified_snapshot = {
        "prusa_core_one": {
            "d_voxel_size": 0.2,
            "d_min_wall_mm": 0.9,
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.4,
            "default_material": "pla_fdm",
        },
        "sls_pa12": {
            "d_voxel_size": 0.2,
            "d_min_wall_mm": 0.8,
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.8,  # v0.1.1
            "default_material": "nylon12_sls",
        },
        "formlabs_fuse1_pa12": {
            "d_voxel_size": 0.15,
            "d_min_wall_mm": 0.6,
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.3,  # v0.1.1
            "default_material": "nylon12_sls",
        },
        "sls_pa11": {
            "d_voxel_size": 0.2,
            "d_min_wall_mm": 0.8,
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.8,  # v0.1.1
            "default_material": "nylon11_sls",
        },
        "fdm_pla": {
            "d_voxel_size": 0.25,
            "d_min_wall_mm": 0.8,  # v0.1.1
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.4,  # v0.1.1
            "default_material": "pla_fdm",
        },
        "fdm_abs": {
            "d_voxel_size": 0.25,
            "d_min_wall_mm": 0.8,  # v0.1.1
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.4,  # v0.1.1
            "default_material": "abs_fdm",
        },
        "fdm_petg": {
            "d_voxel_size": 0.25,
            "d_min_wall_mm": 0.8,  # v0.1.1
            "d_min_clearance_mm": 0.3,
            "d_min_feature_mm": 0.4,  # v0.1.1
            "default_material": "petg_fdm",
        },
    }

    for preset_id, expected in verified_snapshot.items():
        actual = get_preset_as_legacy_dict(preset_id)
        for key, expected_val in expected.items():
            if isinstance(expected_val, (int, float)):
                assert actual.get(key) == pytest.approx(expected_val), (
                    f"{preset_id}.{key}: substrate value "
                    f"{actual.get(key)!r} != v0.1.1 verified {expected_val!r}"
                )
            elif key == "default_material":
                assert key in actual, f"{preset_id}: default_material missing"
                assert actual[key] == expected_val, (
                    f"{preset_id}.default_material: substrate "
                    f"{actual[key]!r} != verified {expected_val!r}"
                )
