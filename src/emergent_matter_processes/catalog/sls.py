"""SLS preset catalog: generic PA12/PA11 + Formlabs Fuse 1+ 30W.

Two process-family generics (PA12, PA11) and one machine-specific preset
(Formlabs Fuse 1+ 30W) at v0.2.0. Schema-rewritten: machine physics
(build volume, layer height, laser power, laser spot) on
``MachinePhysics``; design rules (walls, clearances, per-feature minima,
Nylon-12 material-specific build-volume cap) on ``DesignRules``.

Sources
-------
- Formlabs Tech Specs (machine physics):
  https://formlabs.com/3d-printers/fuse-1/tech-specs/
- Formlabs SLS Design Guide PDF (design rules):
  https://media.formlabs.com/m/3dd7e18937c55e27/original/-ENUS-Fuse-Series-SLS-Design-Guide.pdf
- Hubs SLS Design Guide:
  https://www.hubs.com/knowledge-base/how-design-parts-sls-3d-printing/
- Gibson, Rosen, Stucker, Khorasani, "Additive Manufacturing
  Technologies," 3rd ed., Springer 2021, Chapter 5
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

_FORMLABS_FUSE1_SPEC = (
    "Formlabs Inc., 'Fuse Series SLS 3D Printers: Technical Specifications,' "
    "retrieved 2026-05-24 from "
    "https://formlabs.com/3d-printers/fuse-1/tech-specs/"
)
_FORMLABS_FUSE_DESIGN_GUIDE = (
    "Formlabs Inc., 'Fuse Series SLS Design Guide,' March 2023, retrieved "
    "2026-05-24 from "
    "https://media.formlabs.com/m/3dd7e18937c55e27/original/-ENUS-Fuse-Series-SLS-Design-Guide.pdf"
)
_HUBS_SLS_GUIDE = (
    "Hubs (a Protolabs company), 'How to design parts for SLS 3D printing,' "
    "2024, retrieved 2026-05-24 from "
    "https://www.hubs.com/knowledge-base/how-design-parts-sls-3d-printing/"
)
_GIBSON_AM_TECH_CH5 = (
    "Gibson, Rosen, Stucker, Khorasani, 'Additive Manufacturing "
    "Technologies,' 3rd ed., Springer 2021, Chapter 5 'Powder Bed Fusion.' "
    "Source identified but full-text auth-walled; values cross-verified "
    "via Hubs SLS design page."
)


# The preset tables below are hand-aligned catalog data; keep the layout.
# fmt: off

# ── Formlabs Fuse 1+ 30W (with Nylon 12) ─────────────────────────────────
#
# v0.2.0 additions per audit recommendations:
# - MachinePhysics: laser_power=30W, laser_spot_size=247um (audit found
#   the laser spot is a better physical voxel floor than 150um)
# - DesignRules.min_wall_vertical = 0.6 mm + min_wall_horizontal = 0.3 mm
#   (Formlabs publishes orientation-specific minima)
# - DesignRules.integrated_clearance_small = 0.3 mm + integrated_clearance_large = 0.6 mm
#   (the v0.1.1 conservative scalar of 0.3 mm is preserved; this adds
#   the per-feature-size split)
# - DesignRules.min_pin_diameter = 0.8 mm + min_hole_diameter = 1.0 mm
# - DesignRules.min_embossed_width = 0.35 mm + min_engraved_width = 0.3 mm
# - DesignRules.min_text_height_embossed = 4.5 mm + min_text_height_engraved = 3.0 mm
# - DesignRules.max_part_size_{x,y,z} = 159.8 × 159.8 × 295.5 mm: Nylon 12
#   specific largest part size (smaller than the 165×165×300 build volume)
# - DesignRules.requires_supports = False (SLS doesn't need support material)

formlabs_fuse1_pa12 = Preset(
    s_id="formlabs_fuse1_pa12",
    s_description="Formlabs Fuse 1+ 30W (Nylon 12)",
    s_family="SLS",
    s_method="SLS_powder_bed",
    s_machine_vendor="Formlabs",
    s_machine_model="Fuse 1+ 30W",
    s_default_material="nylon12_sls",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "30 W Ytterbium fiber laser (1070 nm), 247 um spot size. "
        "Build volume 165x165x300 mm (Nylon 12 largest part: "
        "159.8x159.8x295.5 mm). Layer 110 um. No supports required. "
        "Fuse Sift bench-top depowdering."
    ),
    machine_physics=MachinePhysics(
        build_volume_x=_PV(
            d_value=0.165, s_units="m",
            s_source=_FORMLABS_FUSE1_SPEC + ": X 165 mm.",
            s_confidence="datasheet",
        ),
        build_volume_y=_PV(
            d_value=0.165, s_units="m",
            s_source=_FORMLABS_FUSE1_SPEC + ": Y 165 mm.",
            s_confidence="datasheet",
        ),
        build_volume_z=_PV(
            d_value=0.300, s_units="m",
            s_source=_FORMLABS_FUSE1_SPEC + ": Z 300 mm.",
            s_confidence="datasheet",
        ),
        typical_layer_height=_PV(
            d_value=0.110e-3, s_units="m",
            s_source=_FORMLABS_FUSE1_SPEC + ": layer thickness 110 um.",
            s_confidence="datasheet",
        ),
        laser_power=_PV(
            d_value=30.0, s_units="W",
            s_source=_FORMLABS_FUSE1_SPEC + ": 30 W Ytterbium fiber laser.",
            s_confidence="datasheet",
        ),
        laser_spot_size=_PV(
            d_value=247e-6, s_units="m",
            s_source=_FORMLABS_FUSE1_SPEC +
                     ": 247 um spot size FWHM, 1070 nm.",
            s_confidence="datasheet",
            s_notes="Physical X-Y resolution floor of the laser; the "
                    "voxel_size on DesignRules is a higher-level SDF "
                    "abstraction (150 um) that doesn't try to match the "
                    "laser spot exactly.",
        ),
    ),
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.15e-3, s_units="m",
            s_source=_FORMLABS_FUSE1_SPEC +
                     ": derived from 110 um layer + PreForm slicer.",
            s_condition="0.110 mm layer",
            s_confidence="derived",
        ),
        min_wall_thickness=_PV(
            d_value=0.6e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 vertical wall minimum (conservative scalar).",
            s_condition="Nylon 12, vertical wall (conservative scalar; "
                        "horizontal can go to 0.3 mm)",
            s_confidence="datasheet",
        ),
        min_wall_vertical=_PV(
            d_value=0.6e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 vertical wall minimum.",
            s_condition="Nylon 12, vertical orientation",
            s_confidence="datasheet",
        ),
        min_wall_horizontal=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 horizontal wall minimum.",
            s_condition="Nylon 12, horizontal orientation",
            s_confidence="datasheet",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 integrated assembly, features <20 mm² "
                     "(conservative scalar).",
            s_condition="Nylon 12 integrated assembly, features <20 mm²",
            s_confidence="datasheet",
        ),
        integrated_clearance_small=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 integrated assembly clearance for "
                     "features <20 mm².",
            s_condition="Nylon 12, features <20 mm²",
            s_confidence="datasheet",
        ),
        integrated_clearance_large=_PV(
            d_value=0.6e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 integrated assembly clearance for "
                     "features ≥20 mm².",
            s_condition="Nylon 12, features ≥20 mm²",
            s_confidence="datasheet",
        ),
        min_feature_size=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 engraved horizontal width "
                     "(conservative scalar).",
            s_condition="Nylon 12 (conservative scalar; see per-feature fields)",
            s_confidence="datasheet",
        ),
        min_pin_diameter=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE + ": Nylon 12 min pin 0.8 mm.",
            s_confidence="datasheet",
        ),
        min_hole_diameter=_PV(
            d_value=1.0e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE + ": Nylon 12 min hole 1.0 mm.",
            s_confidence="datasheet",
        ),
        min_embossed_width=_PV(
            d_value=0.35e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 embossed horizontal width 0.35 mm.",
            s_confidence="datasheet",
        ),
        min_engraved_width=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 engraved horizontal width 0.3 mm.",
            s_confidence="datasheet",
        ),
        min_text_height_embossed=_PV(
            d_value=4.5e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 minimum embossed text height 4.5 mm.",
            s_confidence="datasheet",
        ),
        min_text_height_engraved=_PV(
            d_value=3.0e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 minimum engraved text height 3.0 mm.",
            s_confidence="datasheet",
        ),
        max_part_size_x=_PV(
            d_value=0.1598, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 largest part X 159.8 mm (smaller than the "
                     "machine's nominal 165 mm build envelope).",
            s_condition="Nylon 12 material-specific cap",
            s_confidence="datasheet",
        ),
        max_part_size_y=_PV(
            d_value=0.1598, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 largest part Y 159.8 mm.",
            s_confidence="datasheet",
        ),
        max_part_size_z=_PV(
            d_value=0.2955, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 12 largest part Z 295.5 mm.",
            s_confidence="datasheet",
        ),
        requires_supports=False,
    ),
    noise_model=ProcessNoise(
        sigma_abs=_PV(
            d_value=0.1e-3, s_units="m",
            s_source="EmergentMatter working estimate (2026-08-05): "
                     "functional calibratable resolution for design "
                     "purposes.",
            s_condition="Nylon 12, post-PreForm-compensation, "
                        "feature-scale dimensions",
            s_confidence="estimated",
            s_notes="Absolute (NOT ratiometric): laser spot 247 um + "
                    "powder grain ~60 um + layer 110 um set a "
                    "scale-invariant floor that dominates at clearance/"
                    "tooth scale. Upgrade to 'measured' after the "
                    "volumetric calibration artifact (witness features + "
                    "gap ladders) is printed and measured.",
        ),
        scale_residual=None,  # PreForm compensates global shrinkage; the
                              # residual is uncharacterized. Do NOT
                              # pre-scale STLs (compensation is the
                              # slicer's job until a bias field exists).
        differential_sigma=None,  # nearby-feature relative error: the
                                  # number gap ladders will measure; it is
                                  # why 0.5 mm print-in-place gaps work
                                  # despite larger global tolerance.
        s_calibration_status="uncalibrated",
        s_notes="v0 statistical layer for chance-constrained SDM design. "
                "sigma(L) = sigma_abs + scale_residual*L.",
    ),
)


# ── SLS PA12 (generic) ───────────────────────────────────────────────────

sls_pa12 = Preset(
    s_id="sls_pa12",
    s_description="SLS Nylon PA12 (generic process-family default)",
    s_family="SLS",
    s_method="SLS_powder_bed",
    s_default_material="nylon12_sls",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "Generic polymer SLS defaults. Use formlabs_fuse1_pa12 (or a "
        "future eos_p_396, etc.) when you know the printer for finer "
        "granularity. PA11 vs PA12: see sls_pa11.s_notes; PA11 needs "
        "more integrated-assembly clearance in practice."
    ),
    # machine_physics intentionally None: generic
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE +
                     ": derived as a reasonable SDF grid spacing for polymer SLS.",
            s_confidence="derived",
        ),
        min_wall_thickness=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE + ": minimum 0.8 mm for PA12.",
            s_condition="vertical wall, PA12 polymer powder-bed",
            s_confidence="handbook",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE +
                     ": moving / bearing-surface clearance for SLS.",
            s_condition="moving fit, polymer powder-bed",
            s_confidence="handbook",
        ),
        min_feature_size=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE +
                     ": minimum pin / protruding feature 0.8 mm.",
            s_condition="pin or protruding feature, polymer powder-bed",
            s_confidence="handbook",
        ),
        typical_layer_height=_PV(
            d_value=0.1e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE +
                     ": industrial SLS commonly uses ~0.1 mm layers.",
            s_confidence="handbook",
        ),
        requires_supports=False,
    ),
)


# ── SLS PA11 (generic) ───────────────────────────────────────────────────
#
# v0.2.0: integrated_clearance_small=1.0 mm captures Formlabs Nylon 11
# specific guidance that PA11 integrated assemblies need >=1.0 mm vs
# Nylon 12's 0.3-0.6 mm. The conservative scalar min_clearance stays at
# 0.3 mm to match PA12 at the moving-fit level (not assembly).

sls_pa11 = Preset(
    s_id="sls_pa11",
    s_description="SLS Nylon PA11 (generic process-family default)",
    s_family="SLS",
    s_method="SLS_powder_bed",
    s_default_material="nylon11_sls",
    s_catalog_version=_S_CATALOG_VERSION,
    s_last_reviewed=_S_LAST_REVIEWED,
    s_notes=(
        "PA11 is more ductile/flexible than PA12 but ALSO more warp-prone. "
        "Per Formlabs Nylon 11 design guidance, integrated assemblies "
        "should use >=1.0 mm clearance (vs 0.3-0.6 mm for Nylon 12). "
        "The conservative scalar min_clearance stays at 0.3 mm for "
        "moving fit; use integrated_clearance_small for assembly design."
    ),
    design_rules=DesignRules(
        voxel_size=_PV(
            d_value=0.2e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE, s_confidence="derived",
        ),
        min_wall_thickness=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE,
            s_condition="vertical wall, polymer powder-bed",
            s_confidence="handbook",
        ),
        min_clearance=_PV(
            d_value=0.3e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE,
            s_condition="moving fit (running clearance)",
            s_confidence="handbook",
        ),
        integrated_clearance_small=_PV(
            d_value=1.0e-3, s_units="m",
            s_source=_FORMLABS_FUSE_DESIGN_GUIDE +
                     ": Nylon 11 integrated assemblies require >=1.0 mm "
                     "clearance (more than Nylon 12's 0.3-0.6 mm) due to "
                     "PA11's higher warping tendency.",
            s_condition="Nylon 11 integrated assembly",
            s_confidence="datasheet",
        ),
        min_feature_size=_PV(
            d_value=0.8e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE,
            s_condition="pin or protruding feature",
            s_confidence="handbook",
        ),
        typical_layer_height=_PV(
            d_value=0.1e-3, s_units="m",
            s_source=_HUBS_SLS_GUIDE,
            s_confidence="handbook",
        ),
        requires_supports=False,
    ),
)


# ── Catalog dict ─────────────────────────────────────────────────────────

CATALOG: dict[str, Preset] = {
    formlabs_fuse1_pa12.s_id: formlabs_fuse1_pa12,
    sls_pa12.s_id:            sls_pa12,
    sls_pa11.s_id:            sls_pa11,
}

# fmt: on


__all__ = [
    "CATALOG",
    "formlabs_fuse1_pa12",
    "sls_pa12",
    "sls_pa11",
]
