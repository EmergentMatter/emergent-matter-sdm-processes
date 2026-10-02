"""Accessor functions: get_preset, aliases, list_*, preset_summary."""

from __future__ import annotations

import pytest

from emergent_matter_processes import (
    PRESETS,
    Preset,
    get_preset,
    list_aliases,
    list_machines,
    list_presets,
    preset_summary,
    register_preset,
)


def test_get_preset_resolves_canonical_ids():
    p = get_preset("formlabs_fuse1_pa12")
    assert p.s_id == "formlabs_fuse1_pa12"
    assert p.b_is_machine_specific


def test_get_preset_resolves_registered_aliases():
    p1 = get_preset("Formlabs_Fuse1")
    p2 = get_preset("formlabs_fuse1_pa12")
    assert p1 is p2


def test_get_preset_resolves_case_folded_legacy_spellings():
    """Legacy em_sdm.manufacturing used .lower().replace('-','_').replace(' ','_').
    Preserve that behavior."""
    p = get_preset("FORMLABS_FUSE1_PA12")
    assert p.s_id == "formlabs_fuse1_pa12"


def test_get_preset_raises_keyerror_for_unknown_names():
    with pytest.raises(KeyError, match="Unknown preset"):
        get_preset("nonexistent_machine_xyz")


def test_list_presets_returns_sorted():
    ids = list_presets()
    assert ids == sorted(ids)
    assert "fdm_pla" in ids


def test_list_presets_family_filter_includes_machines_and_excludes_other_families():
    sls = list_presets(s_family="SLS")
    assert "sls_pa12" in sls
    assert "sls_pa11" in sls
    assert "formlabs_fuse1_pa12" in sls
    assert "fdm_pla" not in sls


def test_list_aliases_returns_a_defensive_copy():
    a = list_aliases()
    assert "Formlabs_Fuse1" in a
    a["something_new"] = "x"
    # Returned dict is a COPY; mutation doesn't affect the source
    assert "something_new" not in list_aliases()


def test_list_machines_only_returns_machine_specific():
    machines = list_machines()
    assert "formlabs_fuse1_pa12" in machines
    assert "prusa_core_one" in machines
    assert "sls_pa12" not in machines  # generic


def test_preset_summary_includes_key_fields():
    s = preset_summary("formlabs_fuse1_pa12")
    assert "formlabs_fuse1_pa12" in s
    assert "Formlabs Fuse 1+ 30W" in s
    assert "nylon12_sls" in s  # default material
    assert "0.600 mm" in s  # min_wall_mm
    assert "build_volume" in s
    assert "laser_spot_size" in s  # v0.2.0: machine_physics surface


def test_register_preset_rejects_name_id_mismatch(monkeypatch):
    # Build a dummy preset with the new MachinePhysics + DesignRules split
    from emergent_matter_processes import DesignRules, PropertyValue

    def _pv(d, u="m"):
        return PropertyValue(d_value=d, s_units=u, s_source="t", s_confidence="datasheet")

    rules = DesignRules(
        voxel_size=_pv(0.2e-3),
        min_wall_thickness=_pv(0.8e-3),
        min_clearance=_pv(0.15e-3),
        min_feature_size=_pv(0.5e-3),
    )
    p = Preset(
        s_id="dummy_test",
        s_description="dummy",
        s_family="FDM",
        s_method="x",
        design_rules=rules,
    )
    with pytest.raises(ValueError, match="register_preset name.*!="):
        register_preset("wrong_key", p)
    register_preset("dummy_test", p)
    assert "dummy_test" in PRESETS
    PRESETS.pop("dummy_test", None)
