"""DesignRules: process + material design rules for printability.

A ``DesignRules`` instance bundles the printability floors a designer
needs to honour for a given process+material combination: minimum
wall thicknesses, clearances, feature sizes, support requirements,
material-specific build-volume caps.

Confidence rule: PropertyValues here can be ``"datasheet"`` (vendor
design guide), ``"measured"`` (lab characterisation), ``"derived"``
(computed from a physical/process model), or ``"handbook"`` (Hubs,
Gibson-Rosen-Stucker, Bayer IM guide). Practitioner handbook is
acceptable here because design rules genuinely come from practitioner
experience: they're not a "the vendor stamped this on a tech-specs
page" type of figure.

Required vs optional
--------------------
Four conservative scalars are REQUIRED (every preset has them
populated): ``voxel_size``, ``min_wall_thickness``, ``min_clearance``,
``min_feature_size``. These serve as the catch-all floors a generic
optimizer can rely on.

Everything else is OPTIONAL and populated only when the source
publishes the more granular figure (e.g. Formlabs publishes
``integrated_clearance_small`` = 0.3 mm AND ``integrated_clearance_large``
= 0.6 mm separately; Prusa publishes neither, only the conservative
scalar).

Why this is separate from MachinePhysics
----------------------------------------
v0.1.x bundled vendor hardware specs and process design rules into a
single ``Capabilities`` dataclass. The audit revealed this conflated
two distinct provenance regimes (see ``machine_physics.py`` docstring).
"""

from __future__ import annotations

from dataclasses import dataclass, fields

from emergent_matter_processes.property_value import PropertyValue
from emergent_matter_processes.units_map import expected_units_for


@dataclass(frozen=True)
class DesignRules:
    """Process+material design rules.

    Required (every preset populates these conservative scalars):
    - voxel_size              SDF grid voxel size (m)
    - min_wall_thickness      conservative minimum wall (m)
    - min_clearance           conservative minimum gap (m, non-negative)
    - min_feature_size        conservative minimum feature (m)

    Optional per-feature-type minima (populated when vendor/handbook
    publishes the more granular figure).
    """

    # ── Required conservative scalars
    voxel_size: PropertyValue  # m
    min_wall_thickness: PropertyValue  # m
    min_clearance: PropertyValue  # m (non-negative)
    min_feature_size: PropertyValue  # m

    # ── Wall thickness, split by orientation
    min_wall_vertical: PropertyValue | None = None  # m
    min_wall_horizontal: PropertyValue | None = None  # m

    # ── Clearance, split by use case
    integrated_clearance_small: PropertyValue | None = None  # m (features <20 mm²)
    integrated_clearance_large: PropertyValue | None = None  # m (features ≥20 mm²)
    bearing_clearance: PropertyValue | None = None  # m (running axle)
    powder_removal_clearance: PropertyValue | None = None  # m (SLS shaft/hole)

    # ── Feature size, split by feature type
    min_pin_diameter: PropertyValue | None = None  # m (protruding pin)
    min_hole_diameter: PropertyValue | None = None  # m (through-hole)
    min_embossed_width: PropertyValue | None = None  # m (raised text/feature)
    min_engraved_width: PropertyValue | None = None  # m (recessed)
    min_escape_hole_diameter: PropertyValue | None = None  # m (SLS powder evacuation)

    # ── Text minima
    min_text_height_embossed: PropertyValue | None = None  # m
    min_text_height_engraved: PropertyValue | None = None  # m

    # ── Overhang / support strategy
    requires_supports: bool = True  # FDM: True; SLS: False
    max_unsupported_overhang: PropertyValue | None = None  # deg (FDM-relevant)
    typical_layer_height: PropertyValue | None = None  # m (process-typical; mirrors MachinePhysics)

    # ── Material-specific build-volume cap (e.g. Formlabs Nylon 12)
    max_part_size_x: PropertyValue | None = None  # m
    max_part_size_y: PropertyValue | None = None  # m
    max_part_size_z: PropertyValue | None = None  # m

    # ── Shrinkage / accuracy
    dimensional_tolerance: PropertyValue | None = None  # m (typical ±)
    shrinkage_linear: PropertyValue | None = None  # dimensionless fraction

    def __post_init__(self) -> None:
        # Units enforcement on every populated PV
        for f in fields(self):
            if f.name == "requires_supports":
                if not isinstance(self.requires_supports, bool):
                    raise TypeError(
                        f"DesignRules.requires_supports must be bool, "
                        f"got {type(self.requires_supports).__name__}"
                    )
                continue
            pv = getattr(self, f.name)
            if pv is None:
                continue
            expected = expected_units_for(f.name)
            if pv.s_units != expected:
                raise ValueError(
                    f"DesignRules.{f.name}: PropertyValue.s_units must be "
                    f"{expected!r}, got {pv.s_units!r}"
                )

        # Sign rules
        # Strictly positive
        for name in (
            "voxel_size",
            "min_wall_thickness",
            "min_feature_size",
            "min_wall_vertical",
            "min_wall_horizontal",
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
        ):
            pv = getattr(self, name)
            if pv is not None and pv.d_value <= 0:
                raise ValueError(f"DesignRules.{name}: must be strictly positive, got {pv.d_value}")

        # Non-negative
        if self.min_clearance.d_value < 0:
            raise ValueError(
                f"DesignRules.min_clearance: must be non-negative, got {self.min_clearance.d_value}"
            )
        for name in (
            "integrated_clearance_small",
            "integrated_clearance_large",
            "bearing_clearance",
            "powder_removal_clearance",
            "shrinkage_linear",
        ):
            pv = getattr(self, name)
            if pv is not None and pv.d_value < 0:
                raise ValueError(f"DesignRules.{name}: must be non-negative, got {pv.d_value}")

        # Sanity: min_feature_size can't dramatically exceed min_wall_thickness
        if self.min_feature_size.d_value > 1.5 * self.min_wall_thickness.d_value:
            raise ValueError(
                f"DesignRules: min_feature_size ({self.min_feature_size.d_value} m) "
                f"significantly exceeds min_wall_thickness "
                f"({self.min_wall_thickness.d_value} m). Physically backwards. "
                f"Check the values."
            )

    # ── Hot-path float accessors

    @property
    def d_voxel_size_m(self) -> float:
        return self.voxel_size.d_value

    @property
    def d_voxel_size_mm(self) -> float:
        return self.voxel_size.d_value * 1e3

    @property
    def d_min_wall_m(self) -> float:
        return self.min_wall_thickness.d_value

    @property
    def d_min_wall_mm(self) -> float:
        return self.min_wall_thickness.d_value * 1e3

    @property
    def d_min_clearance_m(self) -> float:
        return self.min_clearance.d_value

    @property
    def d_min_clearance_mm(self) -> float:
        return self.min_clearance.d_value * 1e3

    @property
    def d_min_feature_m(self) -> float:
        return self.min_feature_size.d_value

    @property
    def d_min_feature_mm(self) -> float:
        return self.min_feature_size.d_value * 1e3

    @property
    def b_has_material_specific_part_size(self) -> bool:
        return (
            self.max_part_size_x is not None
            and self.max_part_size_y is not None
            and self.max_part_size_z is not None
        )


__all__ = ["DesignRules"]
