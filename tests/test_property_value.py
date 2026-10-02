"""PropertyValue construction-time validation tests."""

from __future__ import annotations

import pytest

from emergent_matter_processes import PropertyValue


def test_valid_property_value_constructs():
    pv = PropertyValue(
        d_value=0.0006,
        s_units="m",
        s_source="test",
        s_confidence="datasheet",
    )
    assert pv.d_value == 0.0006
    assert pv.s_units == "m"


def test_confidence_enum_rejects_unknown():
    with pytest.raises(ValueError, match="s_confidence must be one of"):
        PropertyValue(
            d_value=1.0,
            s_units="m",
            s_source="x",
            s_confidence="bogus",  # type: ignore[arg-type]
        )


def test_source_required_unless_placeholder_or_unspecified():
    # No source + confidence="datasheet" → reject
    with pytest.raises(ValueError, match="requires non-empty s_source"):
        PropertyValue(
            d_value=1.0,
            s_units="m",
            s_source="",
            s_confidence="datasheet",
        )


def test_placeholder_without_notes_is_rejected():
    with pytest.raises(ValueError, match="placeholder.*must.*s_notes"):
        PropertyValue(
            d_value=1.0,
            s_units="m",
            s_source="",
            s_confidence="placeholder",  # empty notes
        )


def test_placeholder_with_notes_is_accepted():
    pv = PropertyValue(
        d_value=1.0,
        s_units="m",
        s_source="",
        s_confidence="placeholder",
        s_notes="awaiting vendor spec",
    )
    assert pv.s_confidence == "placeholder"


def test_unspecified_allows_empty_source():
    # Legacy ports: accept empty source with unspecified confidence.
    # (Catalog-level allowlist enforced separately.)
    pv = PropertyValue(
        d_value=1.0,
        s_units="m",
        s_source="",
        s_confidence="unspecified",
    )
    assert pv.s_confidence == "unspecified"


def test_d_value_rejects_bool():
    with pytest.raises(TypeError, match="d_value must be float or int"):
        PropertyValue(
            d_value=True,  # type: ignore[arg-type]
            s_units="m",
            s_source="x",
            s_confidence="datasheet",
        )


def test_d_value_rejects_string():
    with pytest.raises(TypeError, match="d_value must be float or int"):
        PropertyValue(
            d_value="0.6",  # type: ignore[arg-type]
            s_units="m",
            s_source="x",
            s_confidence="datasheet",
        )


def test_as_mm_converts_meters_to_millimeters():
    pv = PropertyValue(d_value=0.0006, s_units="m", s_source="x", s_confidence="datasheet")
    assert pv.as_mm() == pytest.approx(0.6)
    assert pv.as_um() == pytest.approx(600.0)


def test_as_mm_rejects_non_m_units():
    pv = PropertyValue(d_value=45.0, s_units="deg", s_source="x", s_confidence="datasheet")
    with pytest.raises(ValueError, match="expects s_units='m'"):
        pv.as_mm()
