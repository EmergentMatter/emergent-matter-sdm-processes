"""Unified manufacturing-process / machine-capability substrate.

This is the Layer-0 substrate for manufacturing-process and machine-
capability data across the Software Defined Matter ecosystem. One repo,
one schema, one merged catalog of process-family generics and
machine-specific presets, with per-property provenance enforced
by validators.

Public API surface assembled here for one-stop import. See
``docs/architecture.md`` for the schema diagram and
``docs/adr/0001-promote-manufacturing-substrate.md`` for the
consolidation history.

No materials data ships here. ``Preset.s_default_material`` is a plain
string identifier that the consumer resolves against whatever materials
source it uses.
"""

from __future__ import annotations

__version__ = "0.0.0"

# Data semver, bumps independently of package semver:
#   MAJOR: schema break or preset removal (downstream pinning breaks)
#   MINOR: add presets / add new fields / add new aliases
#   PATCH: correct values / update citations / refine conditions
#
# Release history lives in CHANGELOG.md.
__catalog_version__ = "0.3.0"


# ── Core wrapper
# ── Accessor API
from emergent_matter_processes.accessors import (
    PRESETS,
    get_preset,
    get_preset_as_legacy_dict,
    list_aliases,
    list_machines,
    list_presets,
    preset_summary,
    register_preset,
)

# ── Auto-load catalog at import time so PRESETS is ready for consumers
from emergent_matter_processes.catalog._loader import load_all as _load_catalog
from emergent_matter_processes.design_rules import DesignRules

# ── Group dataclasses
from emergent_matter_processes.machine_physics import MachinePhysics

# ── Composite type
from emergent_matter_processes.preset import Preset, ProcessFamily
from emergent_matter_processes.process_noise import CalibrationStatus, ProcessNoise
from emergent_matter_processes.property_value import (
    ConfidenceLevel,
    PropertyValue,
)

# ── Units-map helpers (occasionally useful for downstream validators)
from emergent_matter_processes.units_map import expected_units_for

_load_catalog()
del _load_catalog


__all__ = [
    "__version__",
    "__catalog_version__",
    # Core
    "ConfidenceLevel",
    "PropertyValue",
    # Groups
    "MachinePhysics",
    "DesignRules",
    "ProcessNoise",
    "CalibrationStatus",
    # Composite
    "Preset",
    "ProcessFamily",
    # Accessors
    "PRESETS",
    "get_preset",
    "get_preset_as_legacy_dict",
    "list_presets",
    "list_aliases",
    "list_machines",
    "preset_summary",
    "register_preset",
    # Helpers
    "expected_units_for",
]
