API reference
=============

:doc:`gouge`
   The package and its version.

:doc:`colourcli`
   :class:`~gouge.colourcli.Simple`, the console formatter.

:doc:`parseable`
   :class:`~gouge.parseable.JSONLog`, :class:`~gouge.parseable.CSVLog` and
   :class:`~gouge.parseable.XMLLog`, the machine-readable formatters.

:doc:`preformatters`
   :func:`~gouge.preformatters.uvicorn_access`, the bundled pre-formatter.

:doc:`uvicorn`
   :func:`~gouge.uvicorn.capture_uvicorn`, to format uvicorn's records.

:doc:`filters`
   :class:`~gouge.filters.ShiftingFilter`, to change the level of records.

.. toctree::
   :hidden:

   gouge
   colourcli
   parseable
   preformatters
   uvicorn
   filters
