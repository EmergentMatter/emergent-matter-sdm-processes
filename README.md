<a id="readme-top"></a>

# emergent-matter-sdm-processes

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-033388.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-0055FF.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/packaged%20with-uv-DE5FE9.svg)](https://docs.astral.sh/uv/)

**Layer-0 substrate** for manufacturing-process and machine-capability
data across the Software Defined Matter ecosystem.

One repo. One schema. One merged catalog of manufacturing processes
and machines, with both **process-family generics** and
**machine-specific presets**: every numeric capability carries its
citation, condition, and confidence. The catalog ships today with FDM
and SLS families and is built to grow: adding a machine or a process
family is a data contribution, not a schema change.

## What this is for

This is an **outer-bounds input library** for design and optimization
tooling: the hard floors and ceilings an optimizer must respect, not
manufacturing execution. See [docs/architecture.md](docs/architecture.md)
for the full scope boundary, what this substrate deliberately does not
do, and how the pieces compose.

The optimizer's job is to MINIMIZE geometry within these bounds.
The substrate's job is to TELL the optimizer what those bounds are.

**Typical consumer pattern.** An optimizer asks: *"design me a planetary
bearing that handles 2000 N axial in SLS at minimum mass, max OD 100 mm."*
It pulls the `formlabs_fuse1_pa12` preset and uses:

- **Build envelope** as a hard ceiling: `max_part_size_x/y/z` for the
  material-specific cap (Formlabs Nylon 12: 159.8 × 159.8 × 295.5 mm),
  falling back to `build_volume_x/y/z` for the nominal machine envelope
  (165 × 165 × 300 mm). If the optimizer's solution exceeds these the
  request is genuinely impossible on this machine; the caller should
  be told so.
- **Minimum feature sizes** as hard floors: `min_wall_thickness`,
  `min_pin_diameter`, `min_hole_diameter`, `min_clearance`. The
  optimizer can't propose walls thinner than `min_wall` and expect
  them to print.
- **Machine physics** as inputs to physics-aware optimizers:
  `laser_spot_size` (247 µm on the Fuse 1+) for melt-pool / hatch
  spacing models; `nozzle_diameter` (0.4 mm on the Prusa) for
  extrusion-width derivations; `max_nozzle_temp` / `max_bed_temp`
  for material-compatibility checks.

## Install

The package has no runtime dependencies and needs Python 3.13 or newer.

**As a dependency, from the Software Defined Matter package index** (not PyPI). Browse versions and file hashes at [get.softwaredefinedmatter.com](https://get.softwaredefinedmatter.com/):

```bash
uv pip install emergent-matter-sdm-processes --index https://get.softwaredefinedmatter.com/simple
```

In a uv project, declare the index once and pin the package to it, so its name never resolves from public PyPI:

```toml
[[tool.uv.index]]
name = "em"
url = "https://get.softwaredefinedmatter.com/simple"
explicit = true

[tool.uv.sources]
emergent-matter-sdm-processes = { index = "em" }
```

**From a clone, for contributing:**

```bash
git clone https://github.com/EmergentMatter/emergent-matter-sdm-processes.git
cd emergent-matter-sdm-processes
uv sync
```

## Quickstart

```python
from emergent_matter_processes import (
    PRESETS,
    get_preset,
    get_preset_as_legacy_dict,
    list_presets,
    list_machines,
    preset_summary,
)

# Object access: full Preset with provenance
p = get_preset("formlabs_fuse1_pa12")
print(p.design_rules.d_min_wall_mm)  # 0.6 mm (conservative; vertical)
print(p.design_rules.min_wall_thickness.s_source)
print(p.s_machine_full_name)  # "Formlabs Fuse 1+ 30W"
print(p.s_default_material)  # "nylon12_sls" (material identifier string)

# Machine-physics: vendor-published hardware specs
if p.machine_physics is not None and p.machine_physics.b_has_build_volume:
    bv = p.machine_physics
    bx, by, bz = bv.build_volume_x.d_value, bv.build_volume_y.d_value, bv.build_volume_z.d_value
    print(f"machine build volume: {bx * 1e3:.0f} x {by * 1e3:.0f} x {bz * 1e3:.0f} mm")
    print(f"laser: {bv.laser_power.d_value} W, spot {bv.d_laser_spot_size_um:.0f} um")

# Design-rules: per-feature-type minima + material-specific build cap
dr = p.design_rules
print(f"vertical wall floor: {dr.min_wall_vertical.d_value * 1e3} mm")
print(f"horizontal wall floor: {dr.min_wall_horizontal.d_value * 1e3} mm")
print(f"min pin: {dr.min_pin_diameter.d_value * 1e3} mm")
print(f"min hole: {dr.min_hole_diameter.d_value * 1e3} mm")
if dr.b_has_material_specific_part_size:
    # Formlabs Nylon 12 has a smaller printable region than the machine envelope
    print(
        f"Nylon 12 max part: {dr.max_part_size_x.d_value * 1e3} x "
        f"{dr.max_part_size_y.d_value * 1e3} x {dr.max_part_size_z.d_value * 1e3} mm"
    )

# Aliases
get_preset("Formlabs_Fuse1")  # same object
get_preset("FDM_PLA")  # canonical lookup via alias

# List operations
list_presets()  # every registered preset
list_presets(s_family="FDM")  # subset by family
list_machines()  # machine-specific only

# Human-readable summary
print(preset_summary("prusa_core_one"))

# Legacy em_sdm.manufacturing API shim
get_preset_as_legacy_dict("sls_pa12")
# {'description': 'SLS Nylon PA12 (generic process-family default)',
#  'd_voxel_size': 0.2, 'd_min_wall_mm': 0.8, 'd_min_clearance_mm': 0.3,
#  'd_min_feature_mm': 0.8, 'default_material': 'nylon12_sls', 'notes': '...'}
```

## Bounds-checking patterns

The substrate ships only *data*. The checks below belong in the
consumer's input-validation layer (optimizer, design CLI, Blender
addon): they're the canonical patterns for using the substrate as
the outer-bounds library it's meant to be.

### Hard ceiling: reject impossible requests

If a design exceeds the printable region for this machine + material,
fail fast and tell the caller why.

```python
from emergent_matter_processes import get_preset


def assert_part_fits(s_preset: str, d_x_mm: float, d_y_mm: float, d_z_mm: float) -> None:
    """Raise ValueError if the requested part won't fit in the printable region.

    Prefers material-specific cap (e.g. Formlabs Nylon 12's 159.8x159.8x295.5 mm)
    over machine envelope; falls back to machine envelope when no
    material-specific cap exists.
    """
    p = get_preset(s_preset)
    dr = p.design_rules
    if dr.b_has_material_specific_part_size:
        d_cap = (
            dr.max_part_size_x.d_value * 1e3,
            dr.max_part_size_y.d_value * 1e3,
            dr.max_part_size_z.d_value * 1e3,
        )
        s_basis = f"{s_preset} material-specific cap"
    elif p.machine_physics is not None and p.machine_physics.b_has_build_volume:
        mp = p.machine_physics
        d_cap = (
            mp.build_volume_x.d_value * 1e3,
            mp.build_volume_y.d_value * 1e3,
            mp.build_volume_z.d_value * 1e3,
        )
        s_basis = f"{s_preset} machine envelope"
    else:
        return  # generic preset with no envelope, nothing to check
    if d_x_mm > d_cap[0] or d_y_mm > d_cap[1] or d_z_mm > d_cap[2]:
        raise ValueError(
            f"Part {d_x_mm}x{d_y_mm}x{d_z_mm} mm exceeds {s_basis} "
            f"of {d_cap[0]}x{d_cap[1]}x{d_cap[2]} mm."
        )


# Ask for a 200 mm bearing on the Fuse 1+ → genuinely impossible
assert_part_fits("formlabs_fuse1_pa12", 200, 200, 50)
# → ValueError: Part 200x200x50 mm exceeds formlabs_fuse1_pa12
#     material-specific cap of 159.8x159.8x295.5 mm.
```

### Hard floor: warn on sub-resolution features

When the requested feature is below the published floor, print may
still succeed but quality is at risk. Warn, don't crash.

```python
import warnings
from emergent_matter_processes import get_preset


def warn_if_below_floor(s_preset: str, s_feature: str, d_requested_mm: float) -> None:
    """Issue UserWarning if the requested feature is finer than the published floor."""
    p = get_preset(s_preset)
    floor_pv = getattr(p.design_rules, s_feature, None)
    if floor_pv is None:
        return  # preset doesn't publish this feature minimum
    d_floor_mm = floor_pv.d_value * 1e3
    if d_requested_mm < d_floor_mm:
        warnings.warn(
            f"{s_preset}: requested {s_feature}={d_requested_mm} mm is below "
            f"published floor {d_floor_mm} mm. Print quality at risk.",
            UserWarning,
        )


warn_if_below_floor("prusa_core_one", "min_wall_thickness", 0.3)
# → UserWarning: prusa_core_one: requested min_wall_thickness=0.3 mm
#     is below published floor 0.9 mm. Print quality at risk.
```

### Physics-aware optimization (laser / nozzle inputs)

Pull machine physics for downstream models: melt-pool simulation,
hatch-spacing optimization, extrusion-width derivation.

```python
p = get_preset("formlabs_fuse1_pa12")
mp = p.machine_physics
laser_power_W = mp.laser_power.d_value  # 30.0
laser_spot_um = mp.d_laser_spot_size_um  # 247.0
layer_um = mp.d_typical_layer_height_um  # 110.0
# Feed (laser_power_W, laser_spot_um, layer_um) into a melt-pool model
# that computes scan velocity / hatch overlap.
```

```python
p = get_preset("prusa_core_one")
mp = p.machine_physics
nozzle_mm = mp.d_nozzle_diameter_mm  # 0.4
max_nozzle_C = mp.max_nozzle_temp.d_value  # 290 (400 with HT hotend)
# Use nozzle_mm to derive a slicer-side extrusion-width default; use
# max_nozzle_C to filter materials by required print temperature.
```

The substrate stays a *data* library by design. It doesn't ship any
of these utilities. Consumers compose them where their domain logic
already lives.

## Documentation

| Page | What it covers |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Where this substrate sits, the scope boundary, and how PropertyValue, MachinePhysics, DesignRules, ProcessNoise, and Preset compose |
| [`docs/adr/`](docs/adr/) | Architecture decision records: why the substrate was promoted, why MachinePhysics and DesignRules are split, and the ProcessNoise statistical model |
| [`docs/adding-a-preset.md`](docs/adding-a-preset.md) | The contributor checklist for adding a preset to the catalog |
| [`docs/`](docs/) | Everything else, indexed |
| [STYLE.md](STYLE.md) / [CONTRIBUTING.md](CONTRIBUTING.md) | House style and how a change ships |

## Catalog

Each process family (FDM, SLS, and any added later) has one catalog
file under
[`src/emergent_matter_processes/catalog/`](src/emergent_matter_processes/catalog/),
holding both its process-family generics and its machine-specific
presets. `catalog/_loader.py` is the only module that assembles those
files into the runtime `PRESETS` dict; `list_presets()` and
`list_machines()` are the live way to see what's currently registered,
rather than a table here that goes stale the moment a preset is added.

Machine-specific presets cite vendor datasheets (Tier 1: datasheet).
Process-family generics cite Hubs / Gibson-Rosen-Stucker
(Tier 2: handbook).

**Scope of the catalog.** This library is not limited in the types of
machinery and processes it supports. It serves to provide designers
with manufacturing constraints across all manufacturing and processing
methods: additive families beyond FDM and SLS (MJF, DMLS / SLM, and
others), subtractive processes such as CNC machining, and forming
processes such as injection molding all fit the same schema. The
`ProcessFamily` enum already names several of these. FDM and SLS are
simply the families with presets today. Adding a family is a data
contribution: drop a new file in `catalog/`, register it in
`_loader.py`, and cite your sources (see
[docs/adding-a-preset.md](docs/adding-a-preset.md)).

## Why this substrate exists

See [ADR 0001](docs/adr/0001-promote-manufacturing-substrate.md).

## Backward compatibility

`get_preset_as_legacy_dict(name)` returns the exact `em_sdm.manufacturing`
dict shape with mm-unit values, for consumers that haven't migrated yet.
This shim is documented as a migration aid. New code should use
`get_preset(name)` and reach for the Preset's typed attributes.

## Development

```bash
# Install (editable) with dev deps
uv sync

# Run tests
uv run pytest                  # full suite
uv run pytest -k catalog_integrity  # catalog gate tests only
uv run pytest -k units         # units enforcement only

# Lint, formatting, types (the CI gates)
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Adding a new preset

See [docs/adding-a-preset.md](docs/adding-a-preset.md) for the
contributor checklist. Contributions of new machines and process
families are welcome.

## Built with

| | |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Packaging, the locked dev environment, and the src-layout + hatchling build |
| [pytest](https://docs.pytest.org/) | The full test suite, including the catalog provenance and units gates |
| [ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [mypy](https://mypy-lang.org/) | Static typing, `disallow_untyped_defs` |

The package itself has no runtime dependencies.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how a change ships: the
changeset a pull request needs, and how a release is cut.
[STYLE.md](STYLE.md) is the house style for code, tests, and docs, and
it wins over habit.

By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Support

Questions and usage help go to
[Discussions](https://github.com/EmergentMatter/emergent-matter-sdm/discussions);
bugs and feature requests go to
[Issues](https://github.com/EmergentMatter/emergent-matter-sdm-processes/issues).
See [SUPPORT.md](SUPPORT.md) for what is and is not supported.

For security reports, do not open a public issue. Follow
[SECURITY.md](SECURITY.md).

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

## Acknowledgments

Catalog values cite the vendor specifications and practitioner guides
they're drawn from at the point of use (see
[`src/emergent_matter_processes/catalog/`](src/emergent_matter_processes/catalog/)).
The recurring sources:

- Prusa Research's published Prusa CORE One+ specifications and
  Knowledge Base guidance, for the FDM machine-specific preset.
- Formlabs' published Fuse 1+ 30W technical specifications and SLS
  Design Guide, for the SLS machine-specific preset.
- Hubs (a Protolabs company)'s FDM and SLS design guides, and Gibson,
  Rosen, Stucker, and Khorasani's *Additive Manufacturing
  Technologies* (3rd ed., Springer 2021), for the process-family
  generics.

Citing these sources is not an endorsement by them of this project.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
