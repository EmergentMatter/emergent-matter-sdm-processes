"""ProcessNoise: the statistical layer over a preset's deterministic rules.

DesignRules answers "what are the hard floors?"; ProcessNoise answers "what
is the *distribution* around nominal once you print?" It is the input the
SDM chance-constraint machinery consumes (P(interference) < eps under
manufacturing noise). The modeling decisions below were recorded on
2026-08-05; see ``docs/adr/0003-process-noise-statistical-model.md``.

Model
-----
Dimensional error decomposes into terms with different scaling laws::

    sigma(L) = sigma_abs + scale_residual * L

- ``sigma_abs``: absolute, scale-invariant uncertainty (laser spot /
  nozzle width, powder grain, layer quantization). Dominates at feature
  scale (clearances, teeth, bores). NOT ratiometric: a 0.3 mm gap cares
  about this floor, not about a percentage of anything.
- ``scale_residual``: dimensionless fraction remaining AFTER the machine's
  own compensation (PreForm scaling, input shaper). Matters only on large
  fits; systematic, hence calibratable.
- ``differential_sigma``: relative error between NEARBY features. Close
  surfaces share the local bias field, so their relative error is far
  smaller than global tolerance: this is why print-in-place clearances
  work at all. Measured by gap-ladder artifacts.

Deterministic spatial bias (position/orientation-dependent distortion) is
deliberately NOT modeled here as noise: once a volumetric calibration print
pins it down it should be *compensated* (inverse-warp of SDF query points),
not tolerated. ``s_bias_field`` records the calibration artifact reference;
``s_calibration_status`` records how far along that program is.

Confidence discipline is the same as every other slot: initial working
figures enter as ``estimated`` and are upgraded to ``measured`` when a
calibration artifact (witness features + gap ladders) is printed and
measured on the specific machine.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Literal, get_args

from emergent_matter_processes.property_value import PropertyValue
from emergent_matter_processes.units_map import expected_units_for

CalibrationStatus = Literal[
    "uncalibrated",  # datasheet / rule-of-thumb values only
    "witness",  # single witness print measured (global scalars)
    "volumetric",  # full build-volume bias field + gap ladders fitted
]

#: Runtime counterpart of CalibrationStatus, derived so it cannot drift.
_VALID_CALIBRATION_STATUSES: tuple[str, ...] = get_args(CalibrationStatus)


@dataclass(frozen=True)
class ProcessNoise:
    """Post-compensation statistical model for a (machine, material) preset.

    All fields optional: generics may populate none of them. Units are
    validator-enforced like every other group dataclass.
    """

    # ── sigma(L) = sigma_abs + scale_residual * L
    sigma_abs: PropertyValue | None = None  # m, absolute half-width
    scale_residual: PropertyValue | None = None  # dimensionless fraction
    differential_sigma: PropertyValue | None = None  # m, nearby-feature relative

    # ── Deterministic-bias calibration program
    s_bias_field: str = ""  # artifact/ref id of fitted bias field ("" = none)
    s_calibration_status: CalibrationStatus = "uncalibrated"

    s_notes: str = ""

    def __post_init__(self) -> None:
        if self.s_calibration_status not in _VALID_CALIBRATION_STATUSES:
            raise ValueError(
                f"ProcessNoise.s_calibration_status must be one of "
                f"{'/'.join(_VALID_CALIBRATION_STATUSES)}, "
                f"got {self.s_calibration_status!r}"
            )
        for f in fields(self):
            if not f.name.startswith("s_"):
                pv = getattr(self, f.name)
                if pv is None:
                    continue
                expected = expected_units_for(f.name)
                if pv.s_units != expected:
                    raise ValueError(
                        f"ProcessNoise.{f.name}: units must be {expected!r}, got {pv.s_units!r}"
                    )
