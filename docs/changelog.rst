Changelog
=========

Version 2.3.0
-------------

**Requirements**

* gouge now requires Python 3.11 or newer.
* The package is published under the MIT licence; earlier metadata named both
  MIT and BSD-3-Clause.

**New features**

* ``Simple(show_extra=...)`` shows extra record attributes, such as a
  correlation ID or the OpenTelemetry ``trace_id``/``span_id``, after the
  message.
* New ``gouge.parseable.JSONLog`` formatter: one JSON object per line,
  including extra attributes. The output is always valid JSON: non-finite
  floats are written as strings and values which cannot be serialised as
  their ``str()``.
* ``pre_formatters`` accepts dotted-path strings such as
  ``"gouge.preformatters.uvicorn_access"``, so ``dictConfig`` and YAML
  configurations no longer need a ``Simple`` subclass.
  ``Simple.basicConfig`` accepts ``pre_formatters`` and ``show_extra``.
* New ``gouge.uvicorn.capture_uvicorn()`` routes uvicorn's log records
  through the root handlers.
* The ``NO_COLOR`` and ``FORCE_COLOR`` environment variables are honoured.
* ``CSVLog`` and ``XMLLog`` accept the same constructor arguments as
  ``logging.Formatter``, so they work with ``dictConfig``.

**Fixes**

* Every line of a traceback now carries the traceback colour, and text before
  a highlighted path is no longer uncoloured (#4).
* ``record.exc_text`` no longer contains colour codes, so other handlers
  formatting the same record print a plain traceback.
* An explicitly passed ``highlighted_path`` now takes precedence over the
  ``./src`` default.
* ``Simple.basicConfig(force_styling=True)`` is passed on to the formatter.
* Extra attributes named ``f``, ``s`` or ``levelcolor`` no longer raise a
  ``TypeError``.
* ``Simple.basicConfig`` works when a root handler writes to a stream without
  a ``name``, such as ``io.StringIO`` (#2).

**Compatibility note**

* The ``exc_color`` argument of ``Simple.formatException`` is now a literal
  ANSI escape sequence (for example ``colorama.Fore.RED``) instead of a
  ``"{f.RED}"`` template placeholder, and the returned text is no longer
  brace-escaped. Subclasses overriding ``formatException`` keep working.

**Documentation**

* The documentation moved to https://exhuma.github.io/gouge/ and was
  rewritten.

Version 2.2.5
-------------

* Fix a bug causing all exception message to revert back to red, even if the
  colour was customised.

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

* [2.2.2] - fix: Correctly initialise the "highlighted_path" value

* [2.2.2post1] - fix: Corrected the "preformatters" example from the
  documentation

* [2.2.3] - fix: Path highlighting in exception messages should now work with
  absolute paths

* [2.2.4] - fix: regression introduced in 2.23

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
