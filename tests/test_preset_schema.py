"""Preset construction + machine-pairing rules + group composition."""

from __future__ import annotations

import pytest

from emergent_matter_processes import (
    DesignRules,
    MachinePhysics,
    Preset,
    PropertyValue,
)


def _pv(d: float, u: str = "m") -> PropertyValue:
    return PropertyValue(d_value=d, s_units=u, s_source="test", s_confidence="datasheet")


def _minimal_rules() -> DesignRules:
    return DesignRules(
        voxel_size=_pv(0.2e-3),
        min_wall_thickness=_pv(0.8e-3),
        min_clearance=_pv(0.15e-3),
        min_feature_size=_pv(0.5e-3),
    )


def _minimal_physics() -> MachinePhysics:
    return MachinePhysics(
        build_volume_x=_pv(0.165),
        build_volume_y=_pv(0.165),
        build_volume_z=_pv(0.300),
    )


def test_minimal_generic_preset_constructs():
    p = Preset(
        s_id="sls_test",
        s_description="Test SLS preset",
        s_family="SLS",
        s_method="SLS_powder_bed",
        design_rules=_minimal_rules(),
    )
    assert p.s_id == "sls_test"
    assert not p.b_is_machine_specific
    assert p.machine_physics is None
    assert p.s_machine_full_name == ""


def test_machine_specific_preset_constructs_with_machine_physics():
    p = Preset(
        s_id="x_machine",
        s_description="Test machine preset",
        s_family="SLS",
        s_method="SLS_powder_bed",
        s_machine_vendor="TestCo",
        s_machine_model="Test-1000",
        design_rules=_minimal_rules(),
        machine_physics=_minimal_physics(),
    )
    assert p.b_is_machine_specific
    assert p.s_machine_full_name == "TestCo Test-1000"


def test_empty_id_is_rejected():
    with pytest.raises(ValueError, match="s_id must be non-empty"):
        Preset(
            s_id="",
            s_description="bad",
            s_family="SLS",
            s_method="x",
            design_rules=_minimal_rules(),
        )


def test_unknown_family_is_rejected():
    with pytest.raises(ValueError, match="s_family must be one of"):
        Preset(
            s_id="x",
            s_description="x",
            s_family="SOMETHING",  # type: ignore[arg-type]
            s_method="x",
            design_rules=_minimal_rules(),
        )


def test_vendor_without_model_is_rejected():
    with pytest.raises(ValueError, match="must be paired"):
        Preset(
            s_id="x",
            s_description="x",
            s_family="SLS",
            s_method="x",
            s_machine_vendor="Formlabs",
            s_machine_model="",
            design_rules=_minimal_rules(),
            machine_physics=_minimal_physics(),
        )


def test_model_without_vendor_is_rejected():
    with pytest.raises(ValueError, match="must be paired"):
        Preset(
            s_id="x",
            s_description="x",
            s_family="SLS",
            s_method="x",
            s_machine_vendor="",
            s_machine_model="Fuse 1+",
            design_rules=_minimal_rules(),
            machine_physics=_minimal_physics(),
        )


def test_machine_specific_requires_machine_physics():
    """A preset with vendor/model populated must have machine_physics populated too."""
    with pytest.raises(ValueError, match="machine_physics is None but s_machine_vendor"):
        Preset(
            s_id="x",
            s_description="x",
            s_family="SLS",
            s_method="x",
            s_machine_vendor="Formlabs",
            s_machine_model="Fuse 1+",
            design_rules=_minimal_rules(),
            machine_physics=None,  # missing!
        )


def test_machine_physics_on_a_generic_preset_is_rejected():
    """Inverse: machine_physics populated but no vendor. Disallowed."""
    with pytest.raises(ValueError, match="machine_physics is populated but s_machine_vendor"):
        Preset(
            s_id="x",
            s_description="x",
            s_family="SLS",
            s_method="x",
            # no vendor/model
            design_rules=_minimal_rules(),
            machine_physics=_minimal_physics(),
        )
