Changelog
=========

Version 1.4.0
-------------

* Log messages below the "ERROR" level now show exception tracebacks in cyan
  instead of red. This makes them less intrusive and improves visibility of
  error logs


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
