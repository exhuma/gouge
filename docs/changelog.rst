Changelog
=========

Version 2.2
-----------

* Provide new keyword-argument ``highlighted_path`` to visually distinguish
  traceback elements which are path of a subtree. It defaults to
  ``<current-working-directory>/src`` if it exists.

  This helps reading tracebacks when using complex frameworks (like SQLAlchemy,
  Flask, Starlette, ...).

* [2.2.1] - fix: If the message or traceback contained Python string-template
  variables the output could either break or cause incorrect output. This is
  now fixed.

Version 2.1
-----------

* Added support for pre-formatters.
* Provide bundled pre-formatter for ``uvicorn.access`` via
  ``gouge.preformatters``

Version 2.0
-----------

* Make the ``gouge.colourcli.Simple`` constructor fully compatible with
  ``logging.Formatter``.

  This changes the order of arguments passed into ``Simple()`` which is why
  this is a major release.
* Overall modernisation of the code-base, packaging and release procedure.

Version 1.5.0
-------------

* Add ``show_pid`` option to ``gouge.colourcli.Simple`` to include process IDs
  in log output.

Version 1.4.0
-------------

* Log messages below the "ERROR" level now show exception tracebacks in cyan
  instead of red. This makes them less intrusive and improves visibility of
  error logs
* Add link to the documentation from the Readme


Version 1.3.0
-------------

* Replace ``blessings`` with ``colorama``. This will make colors work on
  Windows as well.


Version 1.2.1
-------------

* Add type-hints & fix minor typing bugs
* Add ``gouge.__version__`` attribute

Version 1.2.0
-------------

* Added :py:class:`gouge.filters.ShiftingFilter`.
* :py:meth:`gouge.colourcli.Simple.basicConfig` now returns a list of modified
  handlers.
