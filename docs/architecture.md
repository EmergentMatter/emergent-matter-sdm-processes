# Architecture

## Scope

This is an **outer-bounds input library** for design and optimization
tooling. It answers one question: is this design physically possible on
this machine running this material, and if so, what are the hard floors
and ceilings the optimizer must respect?

It is **not** a slicer, a print-strategy planner, or a design-rule
enforcer. Supports, rafts, infill, scan strategy, retraction, and cure
schedules belong to the slicer or the machine operator, not here.
Catalog values are *descriptive* ("the smallest pin Formlabs publishes
for Nylon 12 on a Fuse 1+ is 0.8 mm"), not *prescriptive* ("your design
must contain a 0.8 mm pin").

The substrate stays a data library by design. It ships no
bounds-checking utilities of its own; a consumer (an optimizer, a design
CLI, a Blender addon) composes the accessors wherever its own
input-validation layer already lives.

## Composition

```
PropertyValue  (d_value + s_units + s_source + s_condition + s_confidence + s_notes)
    ▲
    │ composes
    │
    ├── MachinePhysics    (build_volume_x/y/z?, typical_layer_height?,
    │                      layer_height_min/max?, nozzle_diameter?,
    │                      laser_power?, laser_spot_size?,
    │                      max_nozzle/bed/chamber_temp?)
    │                     : vendor-published hardware facts;
    │                       confidence: datasheet/measured/derived only
    │
    └── DesignRules       (voxel_size, min_wall_thickness, min_clearance,
                           min_feature_size  ← required conservative scalars,
                           min_wall_vertical/horizontal?,
                           integrated_clearance_small/large?,
                           bearing_clearance?, powder_removal_clearance?,
                           min_pin/hole/embossed/engraved/escape_hole?,
                           min_text_height_embossed/engraved?,
                           max_part_size_x/y/z?  ← material-specific build cap,
                           requires_supports: bool,
                           max_unsupported_overhang?, typical_layer_height?,
                           dimensional_tolerance?, shrinkage_linear?)
                          : process+material printability floors;
                            confidence: datasheet/measured/derived/handbook
    ▲     ▲
    │     │ both compose
    │     │
    ├── ProcessNoise      (sigma_abs?, scale_residual?, differential_sigma?,
    │                      s_bias_field, s_calibration_status, s_notes)
    │                     : post-compensation statistical layer
    │                       sigma(L) = sigma_abs + scale_residual·L;
    │                       confidence: estimated allowed pending calibration
    │     │
    └─────┴── Preset      (s_id, s_description, s_family, s_method,
                           s_machine_vendor?, s_machine_model?,
                           s_default_material?, s_catalog_version, s_last_reviewed,
                           machine_physics: MachinePhysics | None,
                           design_rules:    DesignRules,
                           noise_model:     ProcessNoise | None)
```

Simplified to show the shape of the composition; the docstrings on each
dataclass are the reference for the full field list and the validation
each one runs at construction.

`machine_physics` is `None` on process-family generics (`fdm_pla`,
`sls_pa12`, and similar) and required on machine-specific presets
(`prusa_core_one`, `formlabs_fuse1_pa12`); `design_rules` is always
populated. See [ADR 0002](adr/0002-split-machine-physics-from-design-rules.md)
for why `MachinePhysics` and `DesignRules` are separate dataclasses
rather than one, and [ADR 0003](adr/0003-process-noise-statistical-model.md)
for what `ProcessNoise` models and why.

Every numeric value is a `PropertyValue` with provenance. Hot-path float
accessors (`d_min_wall_mm`, `d_build_volume_m3`, and similar) return bare
floats for consumer code that just wants the number.

Units are SI internally (m, W, °C, deg, dimensionless) and
validator-enforced on construction. Display accessors with a `_mm` /
`_um` suffix convert at read time.
