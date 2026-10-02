"""Catalog package: per-family preset files, assembled by ``_loader.load_all``.

The catalog data lives in this package as Python source files. The
``_loader.py`` module is the **only** seam that knows the data format:
switching to YAML/TOML later is a localized change inside ``_loader.py``
with no public-API impact.

One file per process family:
- ``fdm.py``           : FDM (PLA, ABS, PETG) + Prusa Core One+
- ``sls.py``           : SLS (PA12, PA11) + Formlabs Fuse 1+

The catalog is not limited to these families. Any manufacturing or
processing method fits the schema; add a new ``<family>.py`` file here
and register it in ``_loader.py`` (see ``docs/adding-a-preset.md``).
"""
