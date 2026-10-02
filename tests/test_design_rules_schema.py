"""DesignRules schema + units-enforcement tests."""

from __future__ import annotations

import pytest

from emergent_matter_processes import DesignRules, PropertyValue


def _pv(d_value: float, s_units: str = "m") -> PropertyValue:
    return PropertyValue(
        d_value=d_value, s_units=s_units, s_source="test", s_confidence="datasheet"
    )


def test_required_scalars_construct_and_convert_to_millimeters():
    dr = DesignRules(
        voxel_size=_pv(0.2e-3),
        min_wall_thickness=_pv(0.8e-3),
        min_clearance=_pv(0.15e-3),
        min_feature_size=_pv(0.5e-3),
    )
    assert dr.d_voxel_size_mm == pytest.approx(0.2)
    assert dr.d_min_wall_mm == pytest.approx(0.8)
    assert dr.d_min_clearance_mm == pytest.approx(0.15)
    assert dr.d_min_feature_mm == pytest.approx(0.5)
    assert dr.requires_supports is True  # default


def test_requires_supports_can_be_disabled():
    dr = DesignRules(
        voxel_size=_pv(0.2e-3),
        min_wall_thickness=_pv(0.8e-3),
        min_clearance=_pv(0.15e-3),
        min_feature_size=_pv(0.5e-3),
        requires_supports=False,
    )
    assert dr.requires_supports is False


def test_voxel_size_in_wrong_units_is_rejected():
    with pytest.raises(ValueError, match="voxel_size.*s_units must be 'm'"):
        DesignRules(
            voxel_size=_pv(0.2, s_units="mm"),  # wrong
            min_wall_thickness=_pv(0.8e-3),
            min_clearance=_pv(0.15e-3),
            min_feature_size=_pv(0.5e-3),
        )


def test_overhang_in_wrong_units_is_rejected():
    with pytest.raises(ValueError, match="max_unsupported_overhang.*'deg'"):
        DesignRules(
            voxel_size=_pv(0.2e-3),
            min_wall_thickness=_pv(0.8e-3),
            min_clearance=_pv(0.15e-3),
            min_feature_size=_pv(0.5e-3),
            max_unsupported_overhang=_pv(45.0, s_units="m"),  # wrong
        )


def test_zero_voxel_size_is_rejected():
    with pytest.raises(ValueError, match="voxel_size.*must be strictly positive"):
        DesignRules(
            voxel_size=_pv(0.0),
            min_wall_thickness=_pv(0.8e-3),
            min_clearance=_pv(0.15e-3),
            min_feature_size=_pv(0.5e-3),
        )


def test_negative_clearance_is_rejected():
    with pytest.raises(ValueError, match="min_clearance.*non-negative"):
        DesignRules(
            voxel_size=_pv(0.2e-3),
            min_wall_thickness=_pv(0.8e-3),
            min_clearance=_pv(-0.001),
            min_feature_size=_pv(0.5e-3),
        )


def test_zero_clearance_is_allowed():
    """Monolithic processes can have effectively zero clearance."""
    dr = DesignRules(
        voxel_size=_pv(0.1e-3),
        min_wall_thickness=_pv(0.5e-3),
        min_clearance=_pv(0.0),
        min_feature_size=_pv(0.1e-3),
    )
    assert dr.d_min_clearance_mm == 0.0


def test_min_feature_exceeding_min_wall_is_rejected():
    with pytest.raises(ValueError, match="min_feature_size.*exceeds min_wall"):
        DesignRules(
            voxel_size=_pv(0.2e-3),
            min_wall_thickness=_pv(0.5e-3),
            min_clearance=_pv(0.1e-3),
            min_feature_size=_pv(1.5e-3),
        )


def test_optional_fields_default_to_none():
    dr = DesignRules(
        voxel_size=_pv(0.2e-3),
        min_wall_thickness=_pv(0.8e-3),
        min_clearance=_pv(0.15e-3),
        min_feature_size=_pv(0.5e-3),
    )
    assert dr.min_wall_vertical is None
    assert dr.integrated_clearance_small is None
    assert dr.min_pin_diameter is None
    assert dr.max_part_size_x is None
    assert not dr.b_has_material_specific_part_size


def test_full_part_size_cap_sets_the_material_specific_flag():
    dr = DesignRules(
        voxel_size=_pv(0.15e-3),
        min_wall_thickness=_pv(0.6e-3),
        min_clearance=_pv(0.3e-3),
        min_feature_size=_pv(0.3e-3),
        max_part_size_x=_pv(0.1598),
        max_part_size_y=_pv(0.1598),
        max_part_size_z=_pv(0.2955),
    )
    assert dr.b_has_material_specific_part_size


def test_requires_supports_must_be_bool():
    with pytest.raises(TypeError, match="requires_supports must be bool"):
        DesignRules(
            voxel_size=_pv(0.2e-3),
            min_wall_thickness=_pv(0.8e-3),
            min_clearance=_pv(0.15e-3),
            min_feature_size=_pv(0.5e-3),
            requires_supports="yes",  # type: ignore[arg-type]
        )


def test_per_feature_minima_in_wrong_units_are_rejected():
    """All the per-feature-type minima must be in meters."""
    with pytest.raises(ValueError, match="min_pin_diameter.*'m'"):
        DesignRules(
            voxel_size=_pv(0.15e-3),
            min_wall_thickness=_pv(0.6e-3),
            min_clearance=_pv(0.3e-3),
            min_feature_size=_pv(0.3e-3),
            min_pin_diameter=_pv(0.8, s_units="mm"),  # wrong
        )
