# Adding a preset

1. Decide whether it's a **process-family generic** (for example
   `fdm_pa12_carbon`) or a **machine-specific preset** (for example
   `bambu_x1_carbon_pla`). A generic carries `design_rules` only,
   `machine_physics=None`; a machine-specific preset populates both, and
   pairs `s_machine_vendor` with `s_machine_model`.
2. Add it to the family's file under
   [`src/emergent_matter_processes/catalog/`](../src/emergent_matter_processes/catalog/),
   following the existing pattern in that file. Catalog files are keyed
   by process family, not by machine, so a new machine in an existing
   family (a second FDM printer, say) goes into the existing family
   file rather than a new one.
3. If it's a new family, drop a new `<family>.py` file in `catalog/` and
   import it in `catalog/_loader.py`. `_loader.py` is the only module
   that knows the catalog is stored as Python files; switching to
   YAML or TOML later, if the catalog outgrows hand-written Python or
   needs to be editable by non-coders, is a change localized to that
   one module.
4. Cite the source. Tier 1 (vendor datasheet, measured) for
   machine-specific presets; Tier 2 (a practitioner handbook) is
   acceptable for process-family generics, since there is rarely a
   vendor-published figure for a generic process floor.
5. Add an alias to `_ALIASES` in `accessors.py` if the canonical ID is
   awkward to type or recall.
6. Run tests. `uv run pytest` runs the full suite, including the
   catalog-wide provenance and units gates described in
   [`CLAUDE.md`](../CLAUDE.md)'s Provenance gates section; a units
   mismatch or a missing citation fails at construction time, before
   the test suite even needs to check it.
