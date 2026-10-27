Controlling colour
==================

:class:`~gouge.colourcli.Simple` colours its output with ANSI escape codes.
gouge follows the `NO_COLOR <https://no-color.org>`_ convention and the
``FORCE_COLOR`` variable used by many tools, and strips colour when the
output is not a terminal.

Precedence
----------

The decision is taken when the formatter is created, in this order. The
first rule that applies wins:

.. list-table::
   :header-rows: 1

   * - Setting
     - Created directly
     - With ``basicConfig``
   * - ``force_styling=True``
     - colour
     - colour
   * - ``FORCE_COLOR`` set
     - colour
     - colour
   * - ``NO_COLOR`` set
     - no colour
     - no colour
   * - none of these
     - colour
     - colour on a terminal

An environment variable counts as set when it is not empty. ``FORCE_COLOR``
wins over ``NO_COLOR``.

:meth:`~gouge.colourcli.Simple.basicConfig` lets
`colorama <https://pypi.org/project/colorama/>`_ remove the codes when the
stream is not a terminal, for example when the output is piped into a file.
A formatter created directly cannot know where its output goes and emits
colour codes unless ``NO_COLOR`` is set.

Switch colour off
-----------------

Set ``NO_COLOR`` in the environment. The output then holds no escape codes
at all, including those added by pre-formatters:

>>> import logging
>>> import os
>>> from gouge.colourcli import Simple
>>> record = logging.makeLogRecord({
...     "name": "app",
...     "levelno": logging.INFO,
...     "levelname": "INFO",
...     "msg": "Ready",
... })
>>> os.environ["NO_COLOR"] = "1"
>>> Simple().format(record)
'2026-10-27 13:34:48,899 INFO       [app] Ready'

.. code-block:: console

   $ NO_COLOR=1 python app.py

Switch colour on
----------------

Set ``FORCE_COLOR``, or pass ``force_styling=True``, to keep the colour
codes when the output is not a terminal, for example in a CI log viewer
that renders them:

>>> formatter = Simple(force_styling=True)
>>> formatter.format(record)
'\x1b[32m2026-10-27 13:34:48,899\x1b[0m \x1b[36mINFO      \x1b[0m \x1b[1m[app]\x1b[0m Ready'

``force_styling`` also works in :meth:`~gouge.colourcli.Simple.basicConfig`
and in configuration files.

.. note::

   The environment is read when the formatter is created. Changing
   ``NO_COLOR`` or ``FORCE_COLOR`` later has no effect on existing
   formatters.

Other formatters
----------------

The formatters in :mod:`gouge.parseable` never emit colour. A
pre-formatter which adds colour codes, such as
:func:`~gouge.preformatters.uvicorn_access`, is covered by the rules above:
its codes are removed with all the others when colour is off.
