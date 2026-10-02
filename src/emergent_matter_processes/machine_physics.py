"""MachinePhysics: vendor-published hardware specifications.

A ``MachinePhysics`` instance bundles facts the machine vendor publishes
about the hardware itself: build envelope, layer-height range, laser
spot size, nozzle diameter, operating temperatures.

Confidence rule: every PropertyValue here should be ``"datasheet"`` or
``"measured"`` (or ``"derived"`` for SDF-layer abstractions like
voxel_size). If the vendor doesn't publish the value, the field stays
``None``: vendor-published values do NOT mix with handbook fallbacks
on this dataclass.

For process-family generic presets (e.g. ``fdm_pla`` with no specific
machine), ``machine_physics`` on the ``Preset`` is itself ``None``:
generics carry design rules but no specific machine spec.

Why this is separate from DesignRules
-------------------------------------
v0.1.x bundled vendor hardware specs and process design rules into a
single ``Capabilities`` dataclass. The 2026-05-24 triple-source audit
revealed this conflated two distinct provenance regimes:

- Machine physics (build volume, layer height, laser spot, nozzle dia):
  vendor publishes these directly. Tier 1 datasheet confidence.
- Design rules (min wall, min clearance, min feature): vendor MAY
  publish these in a separate design guide, OR they may come from
  handbook practitioner guidance. Mixed confidence.

Splitting into two dataclasses lets each carry its own provenance
regime cleanly and lets consumers query "what did the vendor publish
about the hardware?" separately from "what design floors apply?"
"""

from __future__ import annotations

from dataclasses import dataclass, fields

from emergent_matter_processes.property_value import PropertyValue
from emergent_matter_processes.units_map import expected_units_for


@dataclass(frozen=True)
class MachinePhysics:
    """Vendor-published hardware specifications.

    All fields optional: different machines publish different specs.
    Required values for machine-specific presets are caller-enforced
    by the catalog-integrity tests, not by this dataclass.
    """

    # ── Build envelope (machine nominal)
    build_volume_x: PropertyValue | None = None  # m
    build_volume_y: PropertyValue | None = None  # m
    build_volume_z: PropertyValue | None = None  # m

    # ── Layer / extrusion
    typical_layer_height: PropertyValue | None = None  # m
    layer_height_min: PropertyValue | None = None  # m
    layer_height_max: PropertyValue | None = None  # m

    # ── FDM-specific
    nozzle_diameter: PropertyValue | None = None  # m

    # ── SLS / laser-based
    laser_power: PropertyValue | None = None  # W
    laser_spot_size: PropertyValue | None = None  # m (FWHM)

    # ── Operating temperatures (FDM)
    max_nozzle_temp: PropertyValue | None = None  # C
    max_bed_temp: PropertyValue | None = None  # C
    max_chamber_temp: PropertyValue | None = None  # C

    def __post_init__(self) -> None:
        # Units enforcement: every populated PV must match the canonical SI string
        for f in fields(self):
            pv = getattr(self, f.name)
            if pv is None:
                continue
            expected = expected_units_for(f.name)
            if pv.s_units != expected:
                raise ValueError(
                    f"MachinePhysics.{f.name}: PropertyValue.s_units must be "
                    f"{expected!r}, got {pv.s_units!r}"
                )

        # Sign rules: all populated lengths/powers/spots must be > 0
        for name in (
            "build_volume_x",
            "build_volume_y",
            "build_volume_z",
            "typical_layer_height",
            "layer_height_min",
            "layer_height_max",
            "nozzle_diameter",
            "laser_power",
            "laser_spot_size",
        ):
            pv = getattr(self, name)
            if pv is not None and pv.d_value <= 0:
                raise ValueError(
                    f"MachinePhysics.{name}: must be strictly positive, got {pv.d_value}"
                )

        # Layer-height range consistency
        if (
            self.layer_height_min is not None
            and self.layer_height_max is not None
            and self.layer_height_min.d_value > self.layer_height_max.d_value
        ):
            raise ValueError(
                f"MachinePhysics: layer_height_min ({self.layer_height_min.d_value}) "
                f"> layer_height_max ({self.layer_height_max.d_value})"
            )

    # ── Hot-path float accessors

    @property
    def b_has_build_volume(self) -> bool:
        return (
            self.build_volume_x is not None
            and self.build_volume_y is not None
            and self.build_volume_z is not None
        )

    @property
    def d_build_volume_m3(self) -> float:
        # Bind locals so the None checks narrow the types for mypy.
        bx, by, bz = self.build_volume_x, self.build_volume_y, self.build_volume_z
        if bx is None or by is None or bz is None:
            raise ValueError("MachinePhysics: build volume not fully populated")
        return bx.d_value * by.d_value * bz.d_value

    @property
    def d_typical_layer_height_m(self) -> float:
        if self.typical_layer_height is None:
            raise ValueError("typical_layer_height not defined")
        return self.typical_layer_height.d_value

    @property
    def d_typical_layer_height_um(self) -> float:
        return self.d_typical_layer_height_m * 1e6

    @property
    def d_nozzle_diameter_mm(self) -> float:
        if self.nozzle_diameter is None:
            raise ValueError("nozzle_diameter not defined")
        return self.nozzle_diameter.d_value * 1e3

    @property
    def d_laser_spot_size_um(self) -> float:
        if self.laser_spot_size is None:
            raise ValueError("laser_spot_size not defined")
        return self.laser_spot_size.d_value * 1e6


__all__ = ["MachinePhysics"]
