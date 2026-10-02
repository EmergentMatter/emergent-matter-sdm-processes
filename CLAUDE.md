# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Code standard

Follow STYLE.md at the repo root for all code, comments, tests, and
docs. Pull request descriptions follow .github/PULL_REQUEST_TEMPLATE.md.

## What This Is

`emergent-matter-sdm-processes` is the **Layer-0 substrate** for manufacturing
process and machine capability data across the Software Defined Matter ecosystem.
One repo, one schema, one catalog of process families and machines (FDM
and SLS today, any process later), with per-value provenance enforced by
validators.

See [docs/architecture.md](docs/architecture.md) for the scope boundary
and how the pieces compose, and
[ADR 0001](docs/adr/0001-promote-manufacturing-substrate.md) for why
this substrate exists and what it replaced.

## Build & Run

```bash
uv sync                           # dev deps (pytest, ruff, mypy)
uv run pytest                     # full suite
uv run pytest -k catalog_integrity  # catalog gate tests only
uv run pytest -k units            # units enforcement only
uv run pytest -k back_compat      # legacy em_sdm.manufacturing API shim
uv run ruff check .               # lint
uv run ruff format --check .      # formatting
uv run mypy src                   # typecheck
```

## Architecture

Composition of provenance-carrying values into capability groups,
split between hardware facts, design rules, and the statistical noise
layer. See
[docs/architecture.md](docs/architecture.md) for the composition
diagram, [ADR 0002](docs/adr/0002-split-machine-physics-from-design-rules.md)
for why `MachinePhysics` and `DesignRules` are separate dataclasses,
and [ADR 0003](docs/adr/0003-process-noise-statistical-model.md) for
what `ProcessNoise` models.

Both groups validate units via `units_map.py` in their `__post_init__`:
a wrong units string is a construction-time error.

## Naming Conventions

Hungarian prefixes on scalar fields and method names (see STYLE.md):

| Prefix | Type | Example |
|---|---|---|
| `d_` | float | `d_value`, `d_min_wall_mm` |
| `n_` | int | `n_features` (none yet) |
| `b_` | bool | `b_is_machine_specific`, `b_has_build_volume` |
| `s_` | str | `s_units`, `s_source`, `s_machine_vendor` |

Composite dataclass names (`PropertyValue`, `MachinePhysics`,
`DesignRules`, `ProcessNoise`, `Preset`) have no prefix.

Hot-path accessors carry the unit in the name:
- `DesignRules.d_voxel_size_m` and `d_voxel_size_mm` (both available;
  storage is m)
- `DesignRules.d_min_wall_mm`, `d_min_clearance_mm`, `d_min_feature_mm`
- `MachinePhysics.d_typical_layer_height_um`
- `MachinePhysics.d_build_volume_m3` (volume; raises if any axis is None)

## Catalog policy

This catalog deliberately accepts Tier 2 sources, not Tier 1 only,
because process-family generic capability values rarely have Tier 1
sources: there's no NIST SRD for "minimum FDM wall thickness."
Practitioner handbooks (Hubs, Gibson/Rosen/Stucker) are the
authoritative sources for process-family floors, and they map to
`confidence="handbook"` (Tier 2).

Machine-specific presets DO have Tier 1 sources (vendor spec sheets)
and use `confidence="datasheet"`, or `confidence="derived"` with the
derivation explained in `s_notes` when the vendor does not publish the
value directly.

When adding new presets:

- **Machine-specific**: cite vendor spec sheet, `confidence="datasheet"`.
- **Process-family generic**: cite a practitioner handbook or peer-
  reviewed design guide, `confidence="handbook"`.
- **Stub/placeholder** (`confidence="placeholder"`, for a machine whose
  values are not yet measured): explicit non-empty `s_notes` required;
  enforced at construction time by `PropertyValue.__post_init__`.

## Provenance gates

The catalog invariants are pinned by the test suite, mainly
`tests/test_catalog_integrity.py` plus the per-group schema files
(`test_property_value.py`, `test_machine_physics_schema.py`,
`test_design_rules_schema.py`, `test_process_noise_schema.py`):

1. Every `PropertyValue` cites a source (`s_source` non-empty), unless
   confidence is `"placeholder"` AND `s_notes` is non-empty.
2. Every `PropertyValue.s_units` matches the expected units map;
   violations raise at construction time.
3. No catalog value uses `"unspecified"` confidence.
4. Machine-specific presets keep their required design-rule confidences
   within `{"datasheet", "measured", "derived", "handbook"}`; noise
   values may additionally be `"estimated"` with reasoning notes.
5. Machine-specific presets populate `machine_physics` including a full
   build volume; generics keep `machine_physics=None`.
6. No preset's `s_catalog_version` leads `__catalog_version__`.

Schema validation itself runs at import time inside `__post_init__`;
a catalog that violates units or confidence shapes fails to import.

## Catalog data format

Python catalog files in `src/emergent_matter_processes/catalog/`,
one per process family, assembled into the runtime `PRESETS` dict by
`catalog/_loader.py`, the only module that knows the data is stored as
Python. See [docs/adding-a-preset.md](docs/adding-a-preset.md) for how
a preset or a family is added, and the README's Catalog section for
the catalog's scope.

## Material identifiers

This package has no runtime dependencies and does not ship materials
data. `Preset.s_default_material` is a **string identifier only**
(e.g. `"nylon12_sls"`, `"pla_fdm"`); resolving it against a materials
catalog is the consumer's responsibility. Keeping the handoff to a
plain string means this substrate can be released independently of
whatever materials source a consumer pairs it with.

## Backward compatibility shim

See the README's
[Backward compatibility](README.md#backward-compatibility) section for
what `get_preset_as_legacy_dict` returns and why.

When the migration of `em_sdm.manufacturing` consumers is complete,
the shim can be deprecated (announce in CHANGELOG.md, remove no sooner
than two MINOR releases later).
