# 0003. `ProcessNoise` as an absolute, calibration-aware statistical model

## Status

Accepted (2026-08-05)

## Context

`DesignRules` answers "what are the hard floors?" It says nothing about
the distribution around nominal once a part actually prints, which is
the input chance-constrained SDM design needs: "P(this bearing jams) <
1% under manufacturing noise," rather than a nominal clearance check
against a fixed floor.

The following modeling decisions were made and recorded on 2026-08-05.

## Decision

**Absolute, not ratiometric.** Dimensional error decomposes as
`sigma(L) = sigma_abs + scale_residual * L`. `sigma_abs` is a length,
not a percentage. At feature scale (clearances, gear teeth, bores) the
scale-invariant floor, whether that is laser spot width, nozzle width,
powder grain, or layer quantization, dominates; a ratiometric model
would be wrong exactly where the model is used most.

**Bias is not noise.** Deterministic spatial distortion is
*calibratable*: once a volumetric calibration print fits the bias
field, geometry is pre-compensated by inverse-warping the SDF query
points, not tolerated statistically. Only the residual left over after
that compensation belongs in `sigma_abs`. `s_calibration_status` tracks
the calibration program's progress through three stages:
`uncalibrated` (datasheet or rule-of-thumb figures only), `witness` (a
single witness print measured, global scalars), and `volumetric` (a
full build-volume bias field plus gap ladders fitted).

**Clearances see the gradient, not the global tolerance.** Nearby
features share the local bias field, so their *relative* error to each
other (`differential_sigma`, measured by gap-ladder artifacts) is far
smaller than the global tolerance. This is the reason tight
print-in-place gaps (on the order of 0.5 mm) work at all: a design
relying on two adjacent features staying close to each other is
protected by the shared bias, even where the part's overall dimensional
tolerance is much looser.

**A third provenance regime, distinct from `MachinePhysics` and
`DesignRules`.** Noise values on machine-specific presets may carry
confidence `"estimated"`, with a mandatory reasoning note explaining
the working figure, in addition to the confidence levels valid
elsewhere in the catalog. An `"estimated"` value is upgraded to
`"measured"` once a calibration artifact (witness features plus
gap ladders) is printed and measured on the specific machine. This is
enforced by `tests/test_process_noise_schema.py`: an `"estimated"`
value with empty `s_notes` fails the gate, and an invalid
`s_calibration_status` is rejected at construction.

## Consequences

- `ProcessNoise` is optional on `Preset` (`None` means the preset has
  not been statistically characterized yet); a caller doing a nominal
  bounds check against `DesignRules` does not need it, and a caller
  doing chance-constrained design must check for `None` before relying
  on it.
- A part declares its target preset by string ID
  (`metadata.process_profile`, e.g. `"formlabs_fuse1_pa12"`) rather
  than embedding manufacturing bounds directly; design tooling derives
  both bounds and noise priors from the preset at evaluation time. This
  mirrors the `s_default_material` handoff, which is likewise a string
  ID the consumer resolves. Swapping the declared profile
  re-evaluates every chance constraint against the new preset without
  the design itself changing.
- `sigma_abs` figures entered as `"estimated"` are working numbers, not
  measured ones, until the calibration artifact catches up. A consumer
  that treats an `"estimated"` value as equivalent to `"measured"` is
  trusting a number that has explicitly not yet been verified on
  hardware.
