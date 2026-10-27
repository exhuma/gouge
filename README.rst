gouge
=====

.. image:: https://github.com/exhuma/gouge/actions/workflows/pythonpackage.yml/badge.svg
   :target: https://github.com/exhuma/gouge/actions/workflows/pythonpackage.yml
   :alt: CI status

.. image:: https://img.shields.io/pypi/v/gouge.svg
   :target: https://pypi.org/project/gouge/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/gouge.svg
   :target: https://pypi.org/project/gouge/
   :alt: Supported Python versions

.. image:: https://github.com/exhuma/gouge/actions/workflows/docs.yml/badge.svg
   :target: https://exhuma.github.io/gouge/
   :alt: Documentation

Formatters for the Python ``logging`` module. gouge gives console output a
uniform, coloured layout that is easy to scan, and writes the same records
as JSON Lines, CSV or XML for machines. It works with the standard library
alone: no wrapper API, no new logger class.

Documentation: https://exhuma.github.io/gouge/

.. image:: https://raw.githubusercontent.com/exhuma/gouge/master/docs/_static/snapshot1.png
   :alt: Console output of gouge: coloured level names, logger names in
      bold, and a red traceback.

Installation
------------

gouge needs Python 3.11 or newer::

    pip install gouge

Example
-------

::

    >>> import logging
    >>> from gouge.colourcli import Simple
    >>> handlers = Simple.basicConfig(
    ...     level=logging.INFO
    ... )
    >>> log = logging.getLogger("app")
    >>> log.info("Server started")
    2026-10-27 13:34:48,899 INFO       [app] Server started
    >>> log.warning("Disk 91% full")
    2026-10-27 13:34:48,899 WARNING    [app] Disk 91% full

On a terminal, the time, level and logger name are coloured.

The documentation covers `console output
<https://exhuma.github.io/gouge/getting-started.html>`_, `configuration
files <https://exhuma.github.io/gouge/configuring.html>`_, `extra
attributes and correlation IDs
<https://exhuma.github.io/gouge/extra-attributes.html>`_, `JSON output
<https://exhuma.github.io/gouge/structured-output.html>`_, `uvicorn
<https://exhuma.github.io/gouge/uvicorn.html>`_ and `colour control
<https://exhuma.github.io/gouge/colour.html>`_. The `changelog
<https://exhuma.github.io/gouge/changelog.html>`_ lists the changes in
every release.

Project status
--------------

gouge is actively maintained and stable (Production/Stable). It follows
Semantic Versioning; the `compatibility policy
<https://exhuma.github.io/gouge/#compatibility>`_ defines what counts as a
breaking change and how deprecation works.
