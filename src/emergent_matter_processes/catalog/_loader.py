"""Catalog loader: assembles per-family CATALOG dicts into PRESETS.

This is the ONLY module that knows the catalog data is stored as Python
files. Switching to YAML/TOML later means rewriting only this module.

Public API:

- :func:`load_all`: called once at package import time
  (from ``emergent_matter_processes/__init__.py``) to populate
  the runtime :data:`~emergent_matter_processes.accessors.PRESETS` dict.
"""

from __future__ import annotations

from emergent_matter_processes.accessors import register_preset


def load_all() -> None:
    """Populate the global PRESETS dict from every catalog file.

    Each catalog module exports a ``CATALOG: dict[str, Preset]``. This
    function iterates them all and registers each entry via
    :func:`~emergent_matter_processes.accessors.register_preset`,
    which also runs the s_id-vs-key validator.

    Idempotent: calling twice replaces existing entries with whatever
    the current catalog files declare.
    """
    # Lazy-import each catalog file so import failures surface here, not
    # at package load time before the loader is even defined.
    from emergent_matter_processes.catalog import (
        fdm,
        sls,
    )

    for module in (fdm, sls):
        for s_id, p in module.CATALOG.items():
            register_preset(s_id, p)


__all__ = ["load_all"]
