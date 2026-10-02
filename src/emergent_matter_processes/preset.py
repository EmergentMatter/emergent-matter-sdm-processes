"""Preset: the top-level catalog entry composing MachinePhysics + DesignRules.

A ``Preset`` is what consumers ask for by name: ``"formlabs_fuse1_pa12"``,
``"fdm_pla"``. It carries:

- An identifier and human-readable description
- The process family (FDM / SLS / MJF / CNC / DMLS / SLM / IM / none)
  per ISO/ASTM 52900
- A more specific method string (free-form refinement)
- Optional machine identification (vendor + model)
- A material identifier string for the typical material (resolved by
  the consumer against its own materials source)
- Catalog versioning fields
- **Two composed groups:**
  - :class:`~emergent_matter_processes.machine_physics.MachinePhysics`:
    what the vendor publishes about the hardware (build volume, layer
    height range, nozzle diameter, laser spot, operating temperatures).
    ``None`` for process-family generics.
  - :class:`~emergent_matter_processes.design_rules.DesignRules`:
    process+material printability floors (min wall, clearance, feature,
    per-type minima, support strategy, material-specific build-volume
    cap). Always present.

This is the v0.2.0 schema. v0.1.x combined both groups into a single
``Capabilities`` dataclass; the split lets each carry its own provenance
regime cleanly (machine physics: vendor datasheet only; design rules:
vendor design guide or handbook practitioner guidance).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, get_args

from emergent_matter_processes.design_rules import DesignRules
from emergent_matter_processes.machine_physics import MachinePhysics
from emergent_matter_processes.process_noise import ProcessNoise

#: ISO/ASTM 52900 process families recognized by the substrate.
ProcessFamily = Literal[
    "FDM",  # material extrusion (FFF/FDM)
    "SLS",  # powder bed fusion, polymer (laser sintering)
    "MJF",  # multi-jet fusion (HP), also powder bed
    "SLA",  # vat photopolymerisation (SLA / DLP / LCD)
    "CNC",  # subtractive machining
    "DMLS",  # powder bed fusion, metal (laser melting/sintering)
    "SLM",  # synonym alias for some vendors
    "IM",  # injection molding
    "none",  # sentinel: no manufacturing constraints
]

#: Runtime counterpart of ProcessFamily, derived so it cannot drift.
_VALID_PROCESS_FAMILIES: tuple[str, ...] = get_args(ProcessFamily)


@dataclass(frozen=True)
class Preset:
    """Top-level catalog entry: composes MachinePhysics + DesignRules."""

    s_id: str  # canonical key
    s_description: str  # human-readable
    s_family: ProcessFamily
    s_method: str  # refinement: "FFF", "SLS_powder_bed", etc.

    # ── The composed groups
    design_rules: DesignRules  # always required
    machine_physics: MachinePhysics | None = None  # None for generics
    # Statistical layer for chance-constrained design (SDM Bayesian program;
    # modeling decisions recorded in ADR 0003, 2026-08-05).
    # None = not yet characterized.
    noise_model: ProcessNoise | None = None

    # ── Machine identification (empty for generics; paired for machine-specific)
    s_machine_vendor: str = ""
    s_machine_model: str = ""

    # ── Default material (string identifier resolved by the consumer, or empty)
    s_default_material: str = ""

    # ── Catalog versioning
    s_catalog_version: str = ""
    s_last_reviewed: str = ""

    # ── Free-form
    s_notes: str = ""

    def __post_init__(self) -> None:
        if not self.s_id:
            raise ValueError("Preset.s_id must be non-empty")
        if not self.s_description:
            raise ValueError(f"Preset.s_description must be non-empty (id={self.s_id!r})")
        if self.s_family not in _VALID_PROCESS_FAMILIES:
            raise ValueError(
                f"Preset.s_family must be one of "
                f"{'/'.join(_VALID_PROCESS_FAMILIES)}, "
                f"got {self.s_family!r}"
            )

        # Machine vendor/model pairing rule
        has_vendor = bool(self.s_machine_vendor)
        has_model = bool(self.s_machine_model)
        if has_vendor != has_model:
            raise ValueError(
                f"Preset.s_machine_vendor and s_machine_model must be paired "
                f"(both empty for generics, both populated for machine-specific). "
                f"Got vendor={self.s_machine_vendor!r}, model={self.s_machine_model!r}"
            )

        # Machine-specific presets MUST have machine_physics populated
        if has_vendor and self.machine_physics is None:
            raise ValueError(
                "Preset.machine_physics is None but s_machine_vendor/model "
                "are populated. Machine-specific presets must populate "
                "machine_physics (vendor-published hardware specs)."
            )
        # And vice versa: if machine_physics is populated, vendor/model must be too
        if self.machine_physics is not None and not has_vendor:
            raise ValueError(
                "Preset.machine_physics is populated but s_machine_vendor "
                "is empty. Generic-process presets must have machine_physics=None."
            )

    @property
    def b_is_machine_specific(self) -> bool:
        return self.machine_physics is not None

    @property
    def s_machine_full_name(self) -> str:
        if not self.b_is_machine_specific:
            return ""
        return f"{self.s_machine_vendor} {self.s_machine_model}"


__all__ = ["Preset", "ProcessFamily"]
