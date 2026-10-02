"""ProcessNoise schema + provenance gates.

ProcessNoise is a THIRD provenance regime, distinct from the two the
v0.2.0 split established:

- Machine physics  -> vendor datasheet only
- Design rules     -> datasheet or handbook
- Process noise    -> ``estimated`` is ALLOWED on machine-specific presets,
  because noise values follow a calibration lifecycle: they enter as
  engineering working figures and are upgraded to ``measured`` when a
  calibration artifact (witness features + gap ladders) is printed
  and measured on the specific machine. What is NOT allowed is a value
  without a source or reasoning note: same citation discipline as
  everywhere else.
"""

from __future__ import annotations

import dataclasses

import pytest

from emergent_matter_processes import PRESETS, ProcessNoise
from emergent_matter_processes.property_value import PropertyValue
from emergent_matter_processes.units_map import expected_units_for

_PV_FIELDS = ("sigma_abs", "scale_residual", "differential_sigma")


def _noise_presets():
    return {s_id: p for s_id, p in PRESETS.items() if p.noise_model is not None}


def test_org_machines_carry_noise_models():
    """The two machines EmergentMatter actually runs must have the
    statistical layer populated (launch scope, 2026-08-05)."""
    have = _noise_presets()
    assert "formlabs_fuse1_pa12" in have
    assert "prusa_core_one" in have
    for s_id in ("formlabs_fuse1_pa12", "prusa_core_one"):
        assert have[s_id].noise_model.sigma_abs is not None, (
            f"{s_id}: sigma_abs is the minimum viable noise model"
        )


def test_process_noise_instances_reject_mutation():
    """ProcessNoise is a frozen schema dataclass like its sibling groups;
    a noise model reached through a frozen Preset must not be a mutable
    back door.
    """
    nm = ProcessNoise()
    with pytest.raises(dataclasses.FrozenInstanceError):
        nm.s_notes = "mutated"  # type: ignore[misc]  # the assignment failing is the point


def test_noise_values_cite_sources_and_units():
    for s_id, p in _noise_presets().items():
        nm = p.noise_model
        for name in _PV_FIELDS:
            pv = getattr(nm, name)
            if pv is None:
                continue
            assert pv.s_source.strip(), f"{s_id}.noise_model.{name}: no source"
            assert pv.s_units == expected_units_for(name), (
                f"{s_id}.noise_model.{name}: units {pv.s_units!r}"
            )


def test_estimated_noise_requires_reasoning_notes():
    """'estimated' is allowed (calibration pending) but never bare:
    the reasoning must live in s_notes, mirroring the Tier-4 rule."""
    for s_id, p in _noise_presets().items():
        for name in _PV_FIELDS:
            pv = getattr(p.noise_model, name)
            if pv is not None and pv.s_confidence == "estimated":
                assert pv.s_notes.strip(), f"{s_id}.noise_model.{name}: estimated without s_notes"


def test_sigma_abs_is_absolute_not_ratiometric():
    """Guard the core modeling decision: sigma_abs is a length (m), not a
    fraction. A percent-like magnitude (< 50 um or > 2 mm for the
    machines cataloged today) is almost certainly a units mistake."""
    for s_id, p in _noise_presets().items():
        pv = p.noise_model.sigma_abs
        assert 50e-6 <= pv.d_value <= 2e-3, f"{s_id}: sigma_abs={pv.d_value} m looks wrong"


def test_invalid_calibration_status_is_rejected():
    with pytest.raises(ValueError):
        ProcessNoise(s_calibration_status="vibes")


def test_wrong_units_rejected_at_construction():
    with pytest.raises(ValueError):
        ProcessNoise(
            sigma_abs=PropertyValue(
                d_value=0.1,
                s_units="mm",  # storage is SI meters
                s_source="test",
                s_confidence="estimated",
                s_notes="test",
            )
        )
