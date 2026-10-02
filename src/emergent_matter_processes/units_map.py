"""Single source of truth for canonical SI units per manufacturing field.

Each ``PropertyValue.s_units`` MUST match the entry in
:data:`_PROPERTY_EXPECTED_UNITS` for the slot it occupies. The
:class:`~emergent_matter_processes.machine_physics.MachinePhysics` and
:class:`~emergent_matter_processes.design_rules.DesignRules` dataclasses
enforce this in ``__post_init__``: a wrong units string is a
construction-time ``ValueError``.

Conventions:

- **Lengths**: ``"m"`` (not mm or um). Internal SI. Display accessors
  on the group dataclass return mm/um as needed.
- **Angles**: ``"deg"`` (degrees, NOT radians). Manufacturing specs
  uniformly use degrees and converting at storage would just add
  friction to entry creation.
- **Temperatures**: ``"C"`` (degrees Celsius).
- **Power**: ``"W"``.
- **Operators in unit strings**: ``"*"`` for multiplication, ``"/"`` for
  division. ASCII only.
"""

from __future__ import annotations

#: Canonical SI units string per field slot. Every PropertyValue's
#: ``s_units`` must match the value in this table for the dataclass field
#: it occupies.
_PROPERTY_EXPECTED_UNITS: dict[str, str] = {
    # ── MachinePhysics: build envelope
    "build_volume_x": "m",
    "build_volume_y": "m",
    "build_volume_z": "m",
    # ── MachinePhysics: layer / extrusion
    "typical_layer_height": "m",
    "layer_height_min": "m",
    "layer_height_max": "m",
    "nozzle_diameter": "m",
    # ── MachinePhysics: laser
    "laser_power": "W",
    "laser_spot_size": "m",
    # ── MachinePhysics: operating temperatures
    "max_nozzle_temp": "C",
    "max_bed_temp": "C",
    "max_chamber_temp": "C",
    # ── DesignRules: required conservative scalars
    "voxel_size": "m",
    "min_wall_thickness": "m",
    "min_clearance": "m",  # non-negative
    "min_feature_size": "m",
    # ── DesignRules: walls split by orientation
    "min_wall_vertical": "m",
    "min_wall_horizontal": "m",
    # ── DesignRules: clearances split by use case
    "integrated_clearance_small": "m",
    "integrated_clearance_large": "m",
    "bearing_clearance": "m",
    "powder_removal_clearance": "m",
    # ── DesignRules: feature sizes split by feature type
    "min_pin_diameter": "m",
    "min_hole_diameter": "m",
    "min_embossed_width": "m",
    "min_engraved_width": "m",
    "min_escape_hole_diameter": "m",
    # ── DesignRules: text minima
    "min_text_height_embossed": "m",
    "min_text_height_engraved": "m",
    # ── DesignRules: overhang / supports
    "max_unsupported_overhang": "deg",
    # ── DesignRules: material-specific build-volume cap
    "max_part_size_x": "m",
    "max_part_size_y": "m",
    "max_part_size_z": "m",
    # ── DesignRules: accuracy
    "dimensional_tolerance": "m",
    "shrinkage_linear": "",  # dimensionless fraction
    # ── ProcessNoise: sigma(L) = sigma_abs + scale_residual * L
    "sigma_abs": "m",
    "scale_residual": "",  # dimensionless fraction
    "differential_sigma": "m",
}


def expected_units_for(s_field_name: str) -> str:
    """Look up the canonical units string for a field slot.

    Raises ``KeyError`` if the field isn't a known field.
    """
    if s_field_name not in _PROPERTY_EXPECTED_UNITS:
        raise KeyError(
            f"No expected-units entry for {s_field_name!r}. "
            f"Known fields: {sorted(_PROPERTY_EXPECTED_UNITS)}"
        )
    return _PROPERTY_EXPECTED_UNITS[s_field_name]


__all__ = [
    "_PROPERTY_EXPECTED_UNITS",
    "expected_units_for",
]
