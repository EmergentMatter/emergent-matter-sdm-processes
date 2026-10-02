"""MachinePhysics schema + units-enforcement tests."""

from __future__ import annotations

import pytest

from emergent_matter_processes import MachinePhysics, PropertyValue


def _pv(d_value: float, s_units: str = "m") -> PropertyValue:
    return PropertyValue(
        d_value=d_value, s_units=s_units, s_source="test", s_confidence="datasheet"
    )


def test_machine_physics_with_all_fields_absent_is_valid():
    """All fields optional: empty MachinePhysics is valid (used for
    process-family generics where none of the machine specs apply)."""
    mp = MachinePhysics()
    assert mp.build_volume_x is None
    assert not mp.b_has_build_volume


def test_full_build_volume_enables_the_volume_accessor():
    mp = MachinePhysics(
        build_volume_x=_pv(0.165),
        build_volume_y=_pv(0.165),
        build_volume_z=_pv(0.300),
    )
    assert mp.b_has_build_volume
    assert mp.d_build_volume_m3 == pytest.approx(0.165 * 0.165 * 0.300)


def test_partial_build_volume_reports_absent_and_volume_raises():
    mp = MachinePhysics(
        build_volume_x=_pv(0.165),
        # y, z missing
    )
    assert not mp.b_has_build_volume
    with pytest.raises(ValueError, match="build volume not fully populated"):
        _ = mp.d_build_volume_m3


def test_laser_spot_size_converts_to_micrometers():
    mp = MachinePhysics(
        laser_power=_pv(30.0, s_units="W"),
        laser_spot_size=_pv(247e-6),  # 247 um in meters
    )
    assert mp.d_laser_spot_size_um == pytest.approx(247.0)


def test_laser_power_in_wrong_units_is_rejected():
    with pytest.raises(ValueError, match="laser_power.*'W'"):
        MachinePhysics(laser_power=_pv(30.0, s_units="m"))  # wrong


def test_temperature_in_wrong_units_is_rejected():
    with pytest.raises(ValueError, match="max_nozzle_temp.*'C'"):
        MachinePhysics(max_nozzle_temp=_pv(290.0, s_units="m"))  # wrong


def test_temperature_fields_accept_celsius():
    mp = MachinePhysics(
        max_nozzle_temp=_pv(290.0, s_units="C"),
        max_bed_temp=_pv(120.0, s_units="C"),
        max_chamber_temp=_pv(55.0, s_units="C"),
    )
    assert mp.max_nozzle_temp.d_value == 290.0


def test_negative_build_volume_is_rejected():
    with pytest.raises(ValueError, match="build_volume_x.*strictly positive"):
        MachinePhysics(build_volume_x=_pv(-0.1))


def test_layer_height_min_above_max_is_rejected():
    """layer_height_min must not exceed layer_height_max."""
    with pytest.raises(ValueError, match="layer_height_min.*> layer_height_max"):
        MachinePhysics(
            layer_height_min=_pv(0.30e-3),  # min > max
            layer_height_max=_pv(0.05e-3),
        )


def test_ordered_layer_height_range_constructs():
    mp = MachinePhysics(
        layer_height_min=_pv(0.05e-3),
        layer_height_max=_pv(0.30e-3),
        typical_layer_height=_pv(0.2e-3),
    )
    assert mp.d_typical_layer_height_um == pytest.approx(200.0)


def test_nozzle_diameter_converts_to_millimeters():
    mp = MachinePhysics(nozzle_diameter=_pv(0.4e-3))
    assert mp.d_nozzle_diameter_mm == pytest.approx(0.4)


def test_accessors_raise_when_their_field_is_absent():
    mp = MachinePhysics()
    with pytest.raises(ValueError, match="nozzle_diameter not defined"):
        _ = mp.d_nozzle_diameter_mm
    with pytest.raises(ValueError, match="laser_spot_size not defined"):
        _ = mp.d_laser_spot_size_um
    with pytest.raises(ValueError, match="typical_layer_height not defined"):
        _ = mp.d_typical_layer_height_m
