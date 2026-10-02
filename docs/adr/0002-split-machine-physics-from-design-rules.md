# 0002. Split `MachinePhysics` from `DesignRules`

## Status

Accepted (2026-05-24)

## Context

The v0.1.x schema bundled vendor hardware specifications and process
design rules into a single `Capabilities` dataclass. A 2026-05-24
triple-source audit, cross-checking every field against its cited
source, found that this conflated two different provenance regimes:

- **Hardware facts** (build volume, layer height range, nozzle
  diameter, laser power, laser spot size, operating temperatures) come
  straight from the vendor's tech-specs page. Confidence on these is
  `"datasheet"`, `"measured"`, or `"derived"` (for an SDF-layer
  abstraction like `voxel_size`), and nothing else.
- **Design rules** (minimum wall, clearance, feature size, and the
  more granular per-feature-type minima) may come from a vendor design
  guide, but just as often come from a practitioner handbook (Hubs,
  Gibson/Rosen/Stucker) instead, because there is no equivalent of a
  NIST reference value for "minimum FDM wall thickness." Confidence on
  these legitimately includes `"handbook"`.

One dataclass covering both meant a single confidence policy had to
cover fields that do not share a provenance regime, and a consumer
could not ask "what did the vendor publish about the hardware?"
separately from "what design floors apply?"

## Decision

Split `Capabilities` into two dataclasses, composed together (with
`ProcessNoise`) on `Preset`:

- **`MachinePhysics`**: vendor-published hardware facts only.
  Confidence is restricted to `"datasheet"`, `"measured"`, or
  `"derived"`. `None` for process-family generics, which do not model
  a specific machine.
- **`DesignRules`**: process+material printability floors. Confidence
  may additionally be `"handbook"`. Always populated: every preset,
  generic or machine-specific, publishes at least the four required
  conservative scalars (`voxel_size`, `min_wall_thickness`,
  `min_clearance`, `min_feature_size`).

`Preset.__post_init__` enforces the pairing this split implies:
`s_machine_vendor` and `s_machine_model` must both be set or both be
empty, and `machine_physics` must be populated exactly when they are.
A machine-specific preset without hardware facts, or a generic with
them, fails at construction rather than at first use.

## Consequences

- A consumer can query hardware facts and design floors independently,
  and each carries only the confidence levels that are legitimate for
  it; a `"handbook"`-sourced value can never end up on `MachinePhysics`
  by accident, because the dataclass its field lives on decides which
  confidence levels are meaningful in context.
- Every process-family generic (`fdm_pla`, `sls_pa12`, and similar)
  carries `machine_physics=None`; every machine-specific preset
  (`prusa_core_one`, `formlabs_fuse1_pa12`) carries both groups
  populated. This is checked by the catalog-integrity test suite, not
  by the dataclasses themselves at the schema level beyond the vendor/
  model/`machine_physics` pairing rule above.
- The catalog data files (`catalog/fdm.py`, `catalog/sls.py`, and
  similar) are correspondingly split into two constructor calls per
  preset rather than one, which is more verbose per preset in exchange
  for the provenance guarantee.
