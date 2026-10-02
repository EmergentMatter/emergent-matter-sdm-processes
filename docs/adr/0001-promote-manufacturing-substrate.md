# 0001. Promote manufacturing constraints into a dedicated substrate

## Status

Accepted (2026-05-24)

## Context

Manufacturing constraint data was scattered across several
EmergentMatter repositories, with no single source of truth:

- The internal SDM library's `em_sdm.manufacturing` module held the
  working catalog: a `TypedDict`-shaped dict, no provenance on any
  value, and mm units throughout.
- A gear-design repo's manufacturing module extended it: a
  gear-specific layer that imported `em_sdm.manufacturing` and merged
  optimizer-bound fields on top.
- Other repos consumed both of the above but did not define catalog
  data of their own.

An earlier materials-properties catalog had already set the
architectural bar for this kind of data: `PropertyValue` wrappers
carrying provenance, units enforcement at construction, provenance
gates in the test suite, and frozen dataclasses. Manufacturing data had
none of that, and every consumer paid for it differently: no citation
to check a floor against, no unit safety, and drift between the two
existing copies with nothing to catch it.

## Decision

Promote `em_sdm.manufacturing.PRESETS` into `emergent-matter-sdm-processes`,
a dedicated Layer-0 substrate built to that same standard:

- **Per-value provenance.** Every numeric capability cites its source
  (vendor datasheet, handbook, or an explicit placeholder marker), so a
  downstream optimization run can record exactly which spec a bound
  came from.
- **SI internally.** Values are stored in meters (and other SI units),
  not mm. Display accessors convert to mm/um at read time.
- **The extension-layer pattern is preserved, not flattened.** The
  gear-design consumer keeps its gear-specific merge layer where it
  lives; it imports this substrate in place of `em_sdm.manufacturing`
  rather than folding gear-specific logic in here.
- **A back-compat shim ships alongside the new API.**
  `get_preset_as_legacy_dict(name)` returns the exact
  `em_sdm.manufacturing` dict shape, mm units included, so existing
  consumers migrate at their own pace instead of on a hard cutover.

## Consequences

- This repo is now the source of truth for manufacturing-process and
  machine-capability data at EmergentMatter; `em_sdm.manufacturing` is
  no longer where that data is edited.
- New code reaches for `get_preset(name)` and the typed `Preset`
  attributes; `get_preset_as_legacy_dict` exists only for consumers
  that have not migrated, and is documented as a migration aid, not a
  permanent API.
- Every value entering the catalog now needs a citation or an explicit
  placeholder marker, which is a real cost on the first pass of adding
  a preset, paid once per value rather than never.
