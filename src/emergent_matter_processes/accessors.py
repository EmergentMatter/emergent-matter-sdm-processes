"""Public accessor API: PRESETS dict + lookup helpers + aliases.

Backward-compatibility shim for ``em_sdm.manufacturing.PRESETS``
-----------------------------------------------------------
The old API (``em_sdm.manufacturing``) returned a plain ``dict`` per
preset with keys like ``"d_voxel_size"`` (in mm). The new API returns
a :class:`~emergent_matter_processes.preset.Preset` dataclass with
SI-meter values composed of MachinePhysics + DesignRules.

For a clean migration path, :func:`get_preset_as_legacy_dict` returns
the old ``dict`` shape, including the mm units, so consumers can
migrate at their own pace. Use :func:`get_preset` for new code.

Aliases
-------
An alias only lands if it has a single canonical interpretation OR
carries the disambiguating machine/material in the alias text itself.
"""

from __future__ import annotations

from emergent_matter_processes.preset import Preset

# ============================================================================
# PRESETS catalog: populated by catalog/_loader.py at module import
# ============================================================================

#: The full preset catalog. Populated by ``catalog/_loader.load_all()`` at
#: import time.
PRESETS: dict[str, Preset] = {}


# ============================================================================
# Aliases
# ============================================================================

#: Short-name → canonical-preset-id map.
_ALIASES: dict[str, str] = {
    # ── Machine-specific (alias carries vendor + product)
    "Formlabs_Fuse1": "formlabs_fuse1_pa12",
    "Prusa_Core_One": "prusa_core_one",
    # ── Process-family + material (alias self-disambiguating)
    "SLS_PA12": "sls_pa12",
    "SLS_PA11": "sls_pa11",
    "FDM_PLA": "fdm_pla",
    "FDM_ABS": "fdm_abs",
    "FDM_PETG": "fdm_petg",
}

# Deliberately NOT in _ALIASES (would be ambiguous):
#   "SLS":      which polymer? PA12, PA11, glass-filled?
#   "FDM":      which polymer? PLA, ABS, PETG, PEEK, Nylon?


# ============================================================================
# Accessor functions
# ============================================================================


def get_preset(s_name: str) -> Preset:
    """Resolve an alias or canonical preset ID to a Preset object.

    Args:
        s_name: Canonical preset ID, registered alias, or a case-folded
            variant of a canonical ID (spaces and hyphens fold to
            underscores).

    Returns:
        The resolved Preset.

    Raises:
        KeyError: ``s_name`` is neither a canonical key, a registered
            alias, nor a case-folded canonical ID.
    """
    if s_name in PRESETS:
        return PRESETS[s_name]
    if s_name in _ALIASES:
        return PRESETS[_ALIASES[s_name]]
    folded = s_name.lower().replace("-", "_").replace(" ", "_")
    if folded in PRESETS:
        return PRESETS[folded]
    raise KeyError(
        f"Unknown preset {s_name!r}. "
        f"Not found in PRESETS or _ALIASES. "
        f"Known canonical IDs: {sorted(PRESETS)[:8]}... "
        f"Known aliases: {sorted(_ALIASES)[:5]}..."
    )


def list_presets(s_family: str | None = None) -> list[str]:
    """Return sorted canonical preset IDs, optionally one family only.

    Args:
        s_family: Restrict the listing to one process family
            (for example ``"FDM"``). ``None`` lists everything.
    """
    if s_family is None:
        return sorted(PRESETS)
    return sorted(s_id for s_id, p in PRESETS.items() if p.s_family == s_family)


def list_aliases() -> dict[str, str]:
    """Return a copy of the alias → canonical-id map."""
    return dict(_ALIASES)


def list_machines() -> list[str]:
    """Return sorted list of machine-specific preset IDs."""
    return sorted(s_id for s_id, p in PRESETS.items() if p.b_is_machine_specific)


def preset_summary(s_name: str) -> str:
    """Return a multi-line human-readable summary of a preset."""
    p = get_preset(s_name)
    dr = p.design_rules
    mp = p.machine_physics
    lines = [
        f"Preset: {p.s_id}",
        f"  Description:    {p.s_description}",
        f"  Family:         {p.s_family}",
        f"  Method:         {p.s_method}",
    ]
    if p.b_is_machine_specific:
        lines.append(f"  Machine:        {p.s_machine_full_name}")
    if p.s_default_material:
        lines.append(f"  Default mat:    {p.s_default_material}")
    lines.append(f"  Catalog:        v{p.s_catalog_version}, reviewed {p.s_last_reviewed}")
    lines.append("  Design rules:")
    lines.append(f"    voxel_size      = {dr.d_voxel_size_mm:.3f} mm")
    lines.append(f"    min_wall        = {dr.d_min_wall_mm:.3f} mm")
    lines.append(f"    min_clearance   = {dr.d_min_clearance_mm:.3f} mm")
    lines.append(f"    min_feature     = {dr.d_min_feature_mm:.3f} mm")
    lines.append(f"    requires_supports = {dr.requires_supports}")
    if mp is not None:
        lines.append("  Machine physics:")
        # Bind locals so the None checks narrow the types for mypy.
        bvx, bvy, bvz = mp.build_volume_x, mp.build_volume_y, mp.build_volume_z
        if bvx is not None and bvy is not None and bvz is not None:
            bx, by, bz = bvx.d_value, bvy.d_value, bvz.d_value
            lines.append(
                f"    build_volume    = {bx * 1e3:.0f} x {by * 1e3:.0f} x {bz * 1e3:.0f} mm"
            )
        if mp.typical_layer_height is not None:
            lines.append(f"    layer_height    = {mp.d_typical_layer_height_um:.0f} um")
        if mp.nozzle_diameter is not None:
            lines.append(f"    nozzle_diameter = {mp.d_nozzle_diameter_mm:.2f} mm")
        if mp.laser_spot_size is not None:
            lines.append(f"    laser_spot_size = {mp.d_laser_spot_size_um:.0f} um")
    return "\n".join(lines)


def register_preset(s_name: str, p: Preset) -> None:
    """Add or update a preset in the runtime catalog.

    Args:
        s_name: Catalog key; must equal ``p.s_id``.
        p: The preset to register.

    Raises:
        ValueError: ``s_name`` does not match ``p.s_id``.
    """
    if s_name != p.s_id:
        raise ValueError(f"register_preset name {s_name!r} != Preset.s_id {p.s_id!r}")
    PRESETS[s_name] = p


# ============================================================================
# Legacy-shape accessor: returns the em_sdm.manufacturing-compatible dict
# ============================================================================


def get_preset_as_legacy_dict(s_name: str) -> dict[str, object]:
    """Return a preset in the legacy ``em_sdm.manufacturing`` dict shape.

    Use this **only** as a migration shim. The dict has:
    - ``description`` (str)
    - ``d_voxel_size`` (float, **mm**)
    - ``d_min_wall_mm`` (float, mm)
    - ``d_min_clearance_mm`` (float, mm)
    - ``d_min_feature_mm`` (float, mm)
    - ``default_material`` (str, present if populated)
    - ``notes`` (str, present if populated)

    The substrate stores in SI (m) on ``DesignRules``; this shim
    converts to mm for legacy callers.
    """
    p = get_preset(s_name)
    dr = p.design_rules
    out: dict[str, object] = {
        "description": p.s_description,
        "d_voxel_size": dr.d_voxel_size_mm,
        "d_min_wall_mm": dr.d_min_wall_mm,
        "d_min_clearance_mm": dr.d_min_clearance_mm,
        "d_min_feature_mm": dr.d_min_feature_mm,
    }
    if p.s_default_material:
        out["default_material"] = p.s_default_material
    if p.s_notes:
        out["notes"] = p.s_notes
    return out


__all__ = [
    "PRESETS",
    "get_preset",
    "get_preset_as_legacy_dict",
    "list_presets",
    "list_aliases",
    "list_machines",
    "preset_summary",
    "register_preset",
]
