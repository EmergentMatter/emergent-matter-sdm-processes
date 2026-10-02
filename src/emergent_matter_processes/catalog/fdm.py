"""FDM / FFF preset catalog: generic polymer presets + Prusa CORE One+.

Three process-family generics (PLA, ABS, PETG) and one machine-specific
preset (Prusa CORE One+) at v0.2.0. Schema-rewritten from v0.1.1:
machine physics (build volume, layer range, nozzle diameter, max
temperatures) lives on ``MachinePhysics``; design rules (min wall,
clearance, feature) lives on ``DesignRules``.

Sources
-------
- Prusa Research, "Prusa CORE One+: Product page,"
  https://www.prusa3d.com/product/prusa-core-one/
- Prusa Knowledge Base, "Modeling with 3D printing in mind" +
  "Layers and Perimeters"
- Hubs (a Protolabs company), "How to design parts for FDM 3D printing,"
  https://www.hubs.com/knowledge-base/how-design-parts-fdm-3d-printing/
  and "3D printing geometry restrictions"
"""

from __future__ import annotations

from emergent_matter_processes.design_rules import DesignRules
from emergent_matter_processes.machine_physics import MachinePhysics
from emergent_matter_processes.preset import Preset
from emergent_matter_processes.process_noise import ProcessNoise
from emergent_matter_processes.property_value import PropertyValue as _PV

# Catalog revision stamped onto this file's presets (Preset.s_catalog_version).
# A data version, independent of the package version and never written by the
# release workflow. It may trail __catalog_version__ but must not lead it.
_S_CATALOG_VERSION = "0.3.0"
_S_LAST_REVIEWED = "2026-05-24"

_PRUSA_CORE_ONE_SPEC = (
    "Prusa Research a.s., 'Prusa CORE One+: Product page,' 2025, "
    "retrieved 2026-05-24 from https://www.prusa3d.com/product/prusa-core-one/"
)
_PRUSA_KB_PERIMETERS = (
    "Prusa Research a.s., 'Modeling with 3D printing in mind' + "
    "'Layers and Perimeters' (Prusa Knowledge Base), retrieved 2026-05-24: "
    "Prusa publishes extrusion width ~0.45 mm for a 0.4 mm nozzle in "
    "PrusaSlicer, making 2-perimeter floor = 0.9 mm."
)
_HUBS_FDM_GUIDE = (
    "Hubs (a Protolabs company), 'How to design parts for FDM 3D printing' + "
    "'3D printing geometry restrictions,' 2024, retrieved 2026-05-24: "
    "Hubs publishes 0.8 mm min wall, 0.3 mm moving clearance, 45 deg "
    "unsupported overhang."
)


# The preset tables below are hand-aligned catalog data; keep the layout.
# fmt: off

# ── Prusa CORE One+ (0.4 mm nozzle) ──────────────────────────────────────

prusa_core_one = Preset(
    s_id="prusa_core_one",
    s_description="Prusa CORE One+ (0.4 mm nozzle)",
    s_family="FDM",
    s_method="FFF",
    s_machine_vendor="Prusa Research",
    s_machine_model="CORE One+",
    s_default_material="pla_fdm",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "Build volume 250x220x270 mm. 0.4 mm stock nozzle (alternatives "
        "0.25/0.6/0.8 mm available). Layer 0.05-0.30 mm. Max nozzle "
        "290 C (400 C with HT hotend upgrade), max bed 120 C, max "
        "chamber 55 C. Filament 1.75 mm."
    ),
    machine_physics=MachinePhysics(
        build_volume_x=_PV(
            d_value=0.250, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": X axis 250 mm.",
            s_confidence="datasheet",
        ),
        build_volume_y=_PV(
            d_value=0.220, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": Y axis 220 mm.",
            s_confidence="datasheet",
        ),
        build_volume_z=_PV(
            d_value=0.270, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": Z axis 270 mm.",
            s_confidence="datasheet",
        ),
        typical_layer_height=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC +
                     ": community-default typical for 0.4 mm nozzle "
                     "(Prusa publishes the 0.05-0.30 mm range, not a "
                     "single 'typical').",
            s_confidence="derived",
        ),
        layer_height_min=_PV(
            d_value=0.05e-3, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": minimum layer 0.05 mm.",
            s_confidence="datasheet",
        ),
        layer_height_max=_PV(
            d_value=0.30e-3, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": maximum layer 0.30 mm.",
            s_confidence="datasheet",
        ),
        nozzle_diameter=_PV(
            d_value=0.4e-3, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": 0.4 mm stock nozzle.",
            s_confidence="datasheet",
            s_notes="Alternatives 0.25 / 0.6 / 0.8 mm available; this preset "
                    "models the 0.4 mm default configuration.",
        ),
        max_nozzle_temp=_PV(
            d_value=290.0, s_units="C",
            s_source=_PRUSA_CORE_ONE_SPEC +
                     ": stock hotend max 290 C (HT hotend upgrade: 400 C).",
            s_confidence="datasheet",
            s_notes="HT hotend is a separate upgrade SKU; default preset "
                    "assumes stock hotend.",
        ),
        max_bed_temp=_PV(
            d_value=120.0, s_units="C",
            s_source=_PRUSA_CORE_ONE_SPEC + ": max heatbed 120 C.",
            s_confidence="datasheet",
        ),
        max_chamber_temp=_PV(
            d_value=55.0, s_units="C",
            s_source=_PRUSA_CORE_ONE_SPEC + ": max chamber 55 C.",
            s_confidence="datasheet",
        ),
    ),
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC +
                     ": derived from 0.4 mm nozzle + 0.2 mm typical layer.",
            s_confidence="derived",
            s_notes="SDF grid spacing matches layer height for FDM.",
        ),
        min_wall_thickness=_PV(
            d_value=0.9e-3, s_units="m",
            s_source=_PRUSA_KB_PERIMETERS,
            s_condition="0.4 mm nozzle, 2 perimeters at 0.45 mm extrusion width",
            s_confidence="derived",
            s_notes="Prusa doesn't publish a machine-level 'minimum wall'; "
                    "derived from PrusaSlicer 0.45 mm extrusion * 2 perimeters.",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="moving fit, 0.4 mm nozzle, FDM",
            s_confidence="handbook",
            s_notes="Prusa doesn't publish a clearance scalar; Hubs is the source.",
        ),
        min_feature_size=_PV(
            d_value=0.4e-3, s_units="m",
            s_source=_PRUSA_CORE_ONE_SPEC + ": nozzle diameter.",
            s_condition="0.4 mm nozzle (derivation)",
            s_confidence="derived",
            s_notes="min_feature = nozzle diameter; for finer features see "
                    "the 0.25 mm nozzle option. Prusa KB also notes "
                    "single-wall width is closer to 0.45 mm extrusion width.",
        ),
        requires_supports=True,
        max_unsupported_overhang=_PV(
            d_value=45.0, s_units="deg",
            s_source=_HUBS_FDM_GUIDE +
                     ": 45 deg from vertical; supports needed above.",
            s_confidence="handbook",
        ),
    ),
    noise_model=ProcessNoise(
        sigma_abs=_PV(
            d_value=0.2e-3, s_units="m",
            s_source="Engineering rule-of-thumb for a well-tuned desktop "
                     "FFF machine (Hubs-class guidance quotes ±0.5% with "
                     "a ±0.5 mm floor for desktop FDM; a CoreXY with "
                     "input shaping does meaningfully better). "
                     "EmergentMatter working estimate (2026-08-05), "
                     "pending calibration.",
            s_condition="0.4 mm nozzle, PLA, post input-shaper tuning",
            s_confidence="estimated",
            s_notes="Absolute (NOT ratiometric) at feature scale: nozzle "
                    "width + extrusion-width quantization set the floor. "
                    "Upgrade to 'measured' after a calibration artifact "
                    "is printed and measured on the target machine.",
        ),
        scale_residual=None,       # uncharacterized; thermal scaling on
                                   # PLA is small but nonzero
        differential_sigma=None,   # gap-ladder measurement pending
        s_calibration_status="uncalibrated",
        s_notes="v0 statistical layer for chance-constrained SDM design. "
                "sigma(L) = sigma_abs + scale_residual*L.",
    ),
)


# ── FDM PLA (generic, process-family default) ────────────────────────────
#
# Process-family generics have machine_physics=None: they don't model
# any specific hardware. design_rules carries the Hubs-published floors.

fdm_pla = Preset(
    s_id="fdm_pla",
    s_description="FDM PLA (generic process-family default)",
    s_family="FDM",
    s_method="FFF",
    s_default_material="pla_fdm",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "Generic FDM PLA defaults. Use a machine-specific preset "
        "(e.g. prusa_core_one) when you know the printer. PLA-specific "
        "material concerns (warp, shrinkage) are tracked in the "
        "materials substrate, not here."
    ),
    # machine_physics intentionally None: this is a generic process preset
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.25e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE +
                     ": derived from typical 0.4 mm nozzle + 0.2 mm layer.",
            s_confidence="derived",
        ),
        min_wall_thickness=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE +
                     ": 2 perimeters at 0.4 mm nozzle.",
            s_condition="0.4 mm nozzle, 2 perimeters",
            s_confidence="handbook",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE +
                     ": Hubs moving-fit clearance.",
            s_condition="moving fit (running clearance)",
            s_confidence="handbook",
        ),
        min_feature_size=_PV(
            d_value=0.4e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE +
                     ": minimum resolvable feature = nozzle diameter.",
            s_condition="0.4 mm nozzle",
            s_confidence="derived",
        ),
        typical_layer_height=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_confidence="handbook",
        ),
        requires_supports=True,
        max_unsupported_overhang=_PV(
            d_value=45.0, s_units="deg",
            s_source=_HUBS_FDM_GUIDE,
            s_confidence="handbook",
        ),
    ),
)


# ── FDM ABS (generic) ────────────────────────────────────────────────────

fdm_abs = Preset(
    s_id="fdm_abs",
    s_description="FDM ABS (generic process-family default)",
    s_family="FDM",
    s_method="FFF",
    s_default_material="abs_fdm",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "Generic FDM ABS: same geometric floors as PLA (nozzle/layer-"
        "bound). ABS-specific shrinkage / warp issues are material-"
        "domain, not capability-domain; heated chamber recommended."
    ),
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.25e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE, s_confidence="derived",
        ),
        min_wall_thickness=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="0.4 mm nozzle, 2 perimeters",
            s_confidence="handbook",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="moving fit",
            s_confidence="handbook",
        ),
        min_feature_size=_PV(
            d_value=0.4e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="0.4 mm nozzle",
            s_confidence="derived",
        ),
        typical_layer_height=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_confidence="handbook",
        ),
        requires_supports=True,
        max_unsupported_overhang=_PV(
            d_value=45.0, s_units="deg",
            s_source=_HUBS_FDM_GUIDE,
            s_confidence="handbook",
        ),
    ),
)


# ── FDM PETG (generic) ───────────────────────────────────────────────────

fdm_petg = Preset(
    s_id="fdm_petg",
    s_description="FDM PETG (generic process-family default)",
    s_family="FDM",
    s_method="FFF",
    s_default_material="petg_fdm",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "Generic FDM PETG. Moderate stringing, easier than ABS, less "
        "brittle than PLA."
    ),
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.25e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE, s_confidence="derived",
        ),
        min_wall_thickness=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="0.4 mm nozzle, 2 perimeters",
            s_confidence="handbook",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="moving fit",
            s_confidence="handbook",
        ),
        min_feature_size=_PV(
            d_value=0.4e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_condition="0.4 mm nozzle",
            s_confidence="derived",
        ),
        typical_layer_height=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_HUBS_FDM_GUIDE,
            s_confidence="handbook",
        ),
        requires_supports=True,
        max_unsupported_overhang=_PV(
            d_value=45.0, s_units="deg",
            s_source=_HUBS_FDM_GUIDE,
            s_confidence="handbook",
        ),
    ),
)


# ── Catalog dict ─────────────────────────────────────────────────────────

CATALOG: dict[str, Preset] = {
    prusa_core_one.s_id: prusa_core_one,
    fdm_pla.s_id:        fdm_pla,
    fdm_abs.s_id:        fdm_abs,
    fdm_petg.s_id:       fdm_petg,
}

# fmt: on


__all__ = [
    "CATALOG",
    "prusa_core_one",
    "fdm_pla",
    "fdm_abs",
    "fdm_petg",
]
