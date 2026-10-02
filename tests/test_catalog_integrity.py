"""Catalog-wide integrity checks for the v0.2.0 PRESETS dict.

These run at import time of the package; this file re-verifies the
invariants that matter for downstream consumers under the new
MachinePhysics + DesignRules schema.
"""

from __future__ import annotations

import importlib.metadata

import pytest

from emergent_matter_processes import (
    PRESETS,
    __catalog_version__,
    __version__,
    list_machines,
    list_presets,
)

# All DesignRules fields that hold a PropertyValue (i.e., not the `requires_supports` bool)
_DESIGN_RULES_PV_FIELDS = (
    "voxel_size",
    "min_wall_thickness",
    "min_clearance",
    "min_feature_size",
    "min_wall_vertical",
    "min_wall_horizontal",
    "integrated_clearance_small",
    "integrated_clearance_large",
    "bearing_clearance",
    "powder_removal_clearance",
    "min_pin_diameter",
    "min_hole_diameter",
    "min_embossed_width",
    "min_engraved_width",
    "min_escape_hole_diameter",
    "min_text_height_embossed",
    "min_text_height_engraved",
    "max_unsupported_overhang",
    "typical_layer_height",
    "max_part_size_x",
    "max_part_size_y",
    "max_part_size_z",
    "dimensional_tolerance",
    "shrinkage_linear",
)

_MACHINE_PHYSICS_PV_FIELDS = (
    "build_volume_x",
    "build_volume_y",
    "build_volume_z",
    "typical_layer_height",
    "layer_height_min",
    "layer_height_max",
    "nozzle_diameter",
    "laser_power",
    "laser_spot_size",
    "max_nozzle_temp",
    "max_bed_temp",
    "max_chamber_temp",
)


def _parse_semver(s_version: str) -> tuple[int, int, int]:
    n_major, n_minor, n_patch = (int(part) for part in s_version.split("."))
    return (n_major, n_minor, n_patch)


def test_module_version_agrees_with_installed_package_metadata():
    """The release workflow rewrites __version__ on every release, so the
    invariant is agreement with the installed distribution, not any one
    literal value.
    """
    try:
        s_installed = importlib.metadata.version("emergent-matter-sdm-processes")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("package not installed; run `uv sync` first")
    assert s_installed == __version__


def test_catalog_version_is_semver_and_no_preset_stamp_leads_it():
    """__catalog_version__ is a data version on its own schedule and is
    deliberately not managed by the release workflow. Per-file preset
    stamps may trail the catalog-wide version; they must never lead it.
    """
    catalog_version = _parse_semver(__catalog_version__)
    for s_id, p in PRESETS.items():
        assert _parse_semver(p.s_catalog_version) <= catalog_version, (
            f"{s_id}: s_catalog_version {p.s_catalog_version!r} is ahead of "
            f"__catalog_version__ {__catalog_version__!r}"
        )


def test_catalog_never_shrinks_below_the_core_preset_count():
    # The seven initial presets must always exist. The catalog can grow
    # above 7 as machines and families are contributed; this gate just
    # catches accidental deletion of existing entries.
    assert len(PRESETS) >= 7, sorted(PRESETS)


def test_every_preset_id_matches_its_key():
    for s_id, p in PRESETS.items():
        assert s_id == p.s_id, f"Catalog key {s_id!r} != Preset.s_id {p.s_id!r}"


def test_every_preset_has_required_design_rules():
    for s_id, p in PRESETS.items():
        dr = p.design_rules
        assert dr.voxel_size is not None, s_id
        assert dr.min_wall_thickness is not None, s_id
        assert dr.min_clearance is not None, s_id
        assert dr.min_feature_size is not None, s_id


def test_canonical_workflow_presets_are_present():
    expected = {
        "prusa_core_one",
        "fdm_pla",
        "fdm_abs",
        "fdm_petg",
        "formlabs_fuse1_pa12",
        "sls_pa12",
        "sls_pa11",
    }
    missing = expected - set(PRESETS.keys())
    assert not missing, f"Missing core preset(s): {sorted(missing)}"


def test_machine_specific_presets_populate_machine_physics():
    """Per the new schema: machine-specific presets must populate machine_physics."""
    for s_id in list_machines():
        p = PRESETS[s_id]
        assert p.machine_physics is not None, (
            f"Machine-specific preset {s_id!r} has no machine_physics"
        )


def test_machine_specific_presets_have_full_build_volumes():
    for s_id in list_machines():
        p = PRESETS[s_id]
        assert p.machine_physics.b_has_build_volume, (
            f"Machine-specific preset {s_id!r} has no build volume on machine_physics"
        )


def test_machine_specific_design_rules_use_acceptable_confidence():
    """Catalog policy: a named-machine preset's required design-rule
    values should use confidence in {datasheet, measured, derived, handbook}.
    The Prusa preset uses 'derived' for fields Prusa doesn't directly
    publish; the Formlabs preset uses 'datasheet' across the board.
    Handbook is acceptable for machine-specific presets when the vendor
    doesn't publish the value (per v0.1.1+ Tier-2 fallback policy)."""
    for s_id in list_machines():
        p = PRESETS[s_id]
        for fname in ("voxel_size", "min_wall_thickness", "min_clearance", "min_feature_size"):
            pv = getattr(p.design_rules, fname)
            allowed = {"datasheet", "measured", "derived", "handbook"}
            assert pv.s_confidence in allowed, (
                f"{s_id}.design_rules.{fname}: machine-specific preset "
                f"uses confidence {pv.s_confidence!r}, expected one of {allowed}"
            )


def test_process_family_generics_have_no_machine_physics():
    """Generic presets must have machine_physics=None: they don't model hardware."""
    generics = [s_id for s_id, p in PRESETS.items() if not p.b_is_machine_specific]
    for s_id in generics:
        p = PRESETS[s_id]
        assert p.machine_physics is None, (
            f"Generic preset {s_id!r} has machine_physics populated: "
            f"that's machine-specific data; move to a named preset."
        )


def test_every_preset_carries_catalog_version_and_review_date():
    for s_id, p in PRESETS.items():
        assert p.s_catalog_version, f"{s_id}: missing s_catalog_version"
        assert p.s_last_reviewed, f"{s_id}: missing s_last_reviewed"


def test_list_presets_family_filter_returns_only_that_family():
    fdm_ids = list_presets(s_family="FDM")
    assert "fdm_pla" in fdm_ids
    assert "prusa_core_one" in fdm_ids
    assert "sls_pa12" not in fdm_ids


def test_no_propertyvalue_uses_unspecified_confidence():
    """Every PropertyValue should cite a source: no 'unspecified' confidence."""
    for s_id, p in PRESETS.items():
        # Walk design_rules
        for fname in _DESIGN_RULES_PV_FIELDS:
            pv = getattr(p.design_rules, fname)
            if pv is None:
                continue
            assert pv.s_confidence != "unspecified", (
                f"{s_id}.design_rules.{fname}: 'unspecified' confidence "
                f"not allowed in v0.2.0+ catalog"
            )
        # Walk machine_physics if present
        if p.machine_physics is not None:
            for fname in _MACHINE_PHYSICS_PV_FIELDS:
                pv = getattr(p.machine_physics, fname)
                if pv is None:
                    continue
                assert pv.s_confidence != "unspecified", (
                    f"{s_id}.machine_physics.{fname}: 'unspecified' confidence not allowed"
                )


def test_every_propertyvalue_has_nonempty_source_unless_placeholder():
    for s_id, p in PRESETS.items():
        for fname in _DESIGN_RULES_PV_FIELDS:
            pv = getattr(p.design_rules, fname)
            if pv is None:
                continue
            if pv.s_confidence == "placeholder":
                assert pv.s_notes, f"{s_id}.design_rules.{fname}: placeholder without notes"
            else:
                assert pv.s_source, (
                    f"{s_id}.design_rules.{fname}: empty s_source (confidence={pv.s_confidence!r})"
                )
        if p.machine_physics is not None:
            for fname in _MACHINE_PHYSICS_PV_FIELDS:
                pv = getattr(p.machine_physics, fname)
                if pv is None:
                    continue
                if pv.s_confidence == "placeholder":
                    assert pv.s_notes, f"{s_id}.machine_physics.{fname}: placeholder without notes"
                else:
                    assert pv.s_source, (
                        f"{s_id}.machine_physics.{fname}: empty s_source "
                        f"(confidence={pv.s_confidence!r})"
                    )


def test_formlabs_preset_captures_the_nylon12_part_size_cap():
    """v0.2.0 audit finding: Formlabs publishes a Nylon 12 max part size
    (159.8 x 159.8 x 295.5 mm) smaller than the machine's nominal build
    volume (165 x 165 x 300 mm). The Formlabs preset should capture this."""
    p = PRESETS["formlabs_fuse1_pa12"]
    assert p.design_rules.b_has_material_specific_part_size, (
        "Formlabs Fuse 1+ Nylon 12 preset is missing max_part_size_x/y/z"
    )
    # Check the values match the Formlabs Nylon 12 design guide figures
    assert p.design_rules.max_part_size_x.d_value == pytest.approx(0.1598)
    assert p.design_rules.max_part_size_y.d_value == pytest.approx(0.1598)
    assert p.design_rules.max_part_size_z.d_value == pytest.approx(0.2955)


def test_pa11_has_distinct_integrated_clearance_from_pa12():
    """v0.2.0 audit finding: Nylon 11 needs >=1.0 mm integrated-assembly
    clearance vs Nylon 12's 0.3 mm. The sls_pa11 preset must reflect this."""
    pa11 = PRESETS["sls_pa11"]
    assert pa11.design_rules.integrated_clearance_small is not None, (
        "sls_pa11 should populate integrated_clearance_small (Formlabs Nylon 11 guidance: >=1.0 mm)"
    )
    assert pa11.design_rules.integrated_clearance_small.d_value >= 1.0e-3
    # PA12 stays at the conservative 0.3 mm scalar (no separate
    # integrated_clearance_small populated on the generic; the Formlabs
    # PA12 preset has 0.3 mm explicitly).
    formlabs = PRESETS["formlabs_fuse1_pa12"]
    assert formlabs.design_rules.integrated_clearance_small.d_value == pytest.approx(0.3e-3)


def test_formlabs_machine_physics_carries_laser_specs():
    """v0.2.0 schema addition: machine_physics carries laser_power +
    laser_spot_size for SLS machines."""
    p = PRESETS["formlabs_fuse1_pa12"]
    mp = p.machine_physics
    assert mp.laser_power is not None
    assert mp.laser_power.d_value == pytest.approx(30.0)
    assert mp.laser_spot_size is not None
    assert mp.laser_spot_size.d_value == pytest.approx(247e-6)


def test_prusa_machine_physics_carries_nozzle_and_temperatures():
    """v0.2.0 schema addition: machine_physics for FDM carries nozzle_diameter
    + max_nozzle/bed/chamber_temp."""
    p = PRESETS["prusa_core_one"]
    mp = p.machine_physics
    assert mp.nozzle_diameter is not None
    assert mp.nozzle_diameter.d_value == pytest.approx(0.4e-3)
    assert mp.max_nozzle_temp is not None
    assert mp.max_nozzle_temp.d_value == pytest.approx(290.0)
    assert mp.max_bed_temp is not None
    assert mp.max_bed_temp.d_value == pytest.approx(120.0)
    assert mp.max_chamber_temp is not None
    assert mp.max_chamber_temp.d_value == pytest.approx(55.0)


def test_sls_presets_dont_require_supports():
    """v0.2.0 schema addition: requires_supports on DesignRules. SLS
    doesn't need support material."""
    for s_id in ("formlabs_fuse1_pa12", "sls_pa12", "sls_pa11"):
        p = PRESETS[s_id]
        assert p.design_rules.requires_supports is False, (
            f"{s_id}: SLS doesn't need supports; requires_supports should be False"
        )


def test_fdm_presets_require_supports():
    for s_id in ("prusa_core_one", "fdm_pla", "fdm_abs", "fdm_petg"):
        p = PRESETS[s_id]
        assert p.design_rules.requires_supports is True, (
            f"{s_id}: FDM requires supports for >45 deg overhangs"
        )
