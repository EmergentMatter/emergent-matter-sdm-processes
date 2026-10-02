"""PropertyValue: a single capability value with full provenance.

Every numeric capability in the manufacturing catalog is stored as a
``PropertyValue``, never as a bare float. The wrapper carries five
pieces of provenance metadata alongside the number.

- ``d_value``: the SI-units numeric value
- ``s_units``: the units string; validator-enforced against
  :data:`~emergent_matter_processes.units_map._PROPERTY_EXPECTED_UNITS`
- ``s_source``: citation (vendor spec sheet, NEMA standard, internal test, etc.)
- ``s_condition``: operating context (material, post-process, layer-height combo)
- ``s_confidence``: provenance grade (enum)
- ``s_notes``: free-form clarification

The s_units field is NOT decorative: the enclosing group dataclass
(``Capabilities``) validates that each PropertyValue's units match the
canonical SI unit for the slot it occupies. A wrong unit string is a
construction-time ``ValueError``.

Why this does not depend on any materials package
-------------------------------------------------
A materials catalog may use a wrapper of the same shape, but this
package stays independently installable with no required
cross-dependency. Manufacturing data may evolve faster than materials
data (new machines ship monthly) so coupling release cadence would be
the wrong tradeoff. Handoff to a materials source is by primitive
(string ID) only; see ``Preset.s_default_material``.

Confidence enum (source-priority hierarchy)
-------------------------------------------
Tier 1 (PRIMARY):
- ``measured``: direct measurement on the user's specific machine
- ``datasheet``: vendor spec sheet (Formlabs Fuse 1+ datasheet, Prusa
  Core One+ spec PDF, EOS Formiga technical data, HP MJF spec, Bambu X1
  datasheet, etc.). Authoritative for machine-specific capability values.
- ``standard``: published reference (NEMA, ISO/ASTM 52900 AM-process
  taxonomy, ANSI/ASME tolerance standards). Authoritative for
  process-family generic capability floors.

Tier 2 (AUTHORITATIVE SECONDARY):
- ``handbook``: practitioner handbooks and peer-reviewed AM-process
  capability reviews (Gibson/Rosen/Stucker "Additive Manufacturing
  Technologies", Wohlers Report, ASM HVMP). Authoritative when no
  Tier 1 datasheet says.

Tier 3 (AGGREGATOR):
- ``aggregator``: third-party comparison sites (Hubs/Protolabs design
  guides, All3DP capability tables). Use only when Tier 1+2 silent.

Tier 4 (INFERRED):
- ``derived``: computed from other capabilities, range-averaged, or
  unit-converted from a vendor figure. Must explain in ``s_notes``.
- ``estimated``: rough engineering rule-of-thumb (2× layer height for
  min wall, etc.). Must explain reasoning in ``s_notes``.

Special:
- ``placeholder``: known-bad stand-in for active migrations; requires
  non-empty ``s_notes`` explaining what real source is pending.
- ``unspecified``: legacy port without source info. Rejected by
  provenance-strength gate tests unless the preset is on the
  migration allowlist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, get_args

ConfidenceLevel = Literal[
    # Tier 1: primary
    "measured",
    "datasheet",
    "standard",
    # Tier 2: authoritative secondary
    "handbook",
    # Tier 3: aggregator
    "aggregator",
    # Tier 4: inferred
    "derived",
    "estimated",
    # Special
    "placeholder",
    "unspecified",
]

#: Runtime counterpart of ConfidenceLevel, derived so it cannot drift.
_VALID_CONFIDENCE_LEVELS: frozenset[str] = frozenset(get_args(ConfidenceLevel))


@dataclass(frozen=True)
class PropertyValue:
    """A single capability value with full provenance.

    See module docstring for the design philosophy. ``__post_init__``
    validates field shapes (confidence enum, source-non-empty rules);
    the *units* validation is done by the enclosing group dataclass
    because only it knows which property slot this value occupies.
    """

    d_value: float
    s_units: str
    s_source: str
    s_condition: str = ""
    s_confidence: ConfidenceLevel = "unspecified"
    s_notes: str = ""

    def __post_init__(self) -> None:
        # Type-check d_value defensively.
        if not isinstance(self.d_value, (int, float)) or isinstance(self.d_value, bool):
            raise TypeError(
                f"PropertyValue.d_value must be float or int, "
                f"got {type(self.d_value).__name__}: {self.d_value!r}"
            )

        # Confidence enum.
        if self.s_confidence not in _VALID_CONFIDENCE_LEVELS:
            raise ValueError(
                f"PropertyValue.s_confidence must be one of "
                f"{sorted(_VALID_CONFIDENCE_LEVELS)}, "
                f"got {self.s_confidence!r}"
            )

        # Source-non-empty rule, with two exceptions:
        #   - "placeholder" requires non-empty s_notes
        #   - "unspecified" allowed (legacy port allowlist enforced at catalog level)
        if not self.s_source:
            if self.s_confidence == "placeholder":
                if not self.s_notes:
                    raise ValueError(
                        "PropertyValue with confidence='placeholder' must "
                        "have non-empty s_notes explaining what real source "
                        "is pending"
                    )
            elif self.s_confidence != "unspecified":
                raise ValueError(
                    f"PropertyValue requires non-empty s_source unless "
                    f"s_confidence='placeholder' (with explanatory s_notes) "
                    f"or s_confidence='unspecified'; got s_source='', "
                    f"s_confidence={self.s_confidence!r}"
                )

    # ── Display-unit conveniences (additive; storage stays SI in m)

    def as_mm(self) -> float:
        """For m-stored values (lengths), return the value in millimeters."""
        if self.s_units != "m":
            raise ValueError(f"as_mm() expects s_units='m', got {self.s_units!r}")
        return self.d_value * 1e3

    def as_um(self) -> float:
        """For m-stored values (lengths), return the value in micrometers."""
        if self.s_units != "m":
            raise ValueError(f"as_um() expects s_units='m', got {self.s_units!r}")
        return self.d_value * 1e6


__all__ = [
    "ConfidenceLevel",
    "PropertyValue",
]
