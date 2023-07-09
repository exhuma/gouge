Welcome to gouge's documentation!
=================================


.. figure:: _static/snapshot1.png
    :alt: Example screenshot

    Example screenshot using the ``colourcli.Simple`` formatter.


Quick Facts
-----------

What
    Canned logging setups.

Who
    http://michel.albert.lu

When
    Initial commit: 2015-09-09

Where
    * https://pypi.python.org/pypi/gouge
    * https://github.com/exhuma/gouge

Why
    Because I want to the same log behaviour across all of my applications.


Installation
------------

::

    $ pip install gouge


Background
----------

``gouge`` started off as a way to share logging formatters across all my
applications. Starting with version 1.2, it now also contains the
:py:class:`gouge.filter.ShiftingFilter <first filter>`. Again, to share the
same behaviour across applications.

It is very "thin", and has no dependencies other than :py:mod:`blessings`.
:py:mod:`blessings` is only used for formatting (colour, bold, …) and it does
not have any external dependencies itself. At least not at the time of this
writing.

I have a fair amount of applications which log to the console. While the
default formatting given by :py:func:`logging.basicConfig()` is usable, I
always end up modifying it. Mostly just adding horizontal whitespace to make it
more readable. Adding colour helps, and I've added it to some projects. My
co-workers are in the same boat, and we end up copy/pasting logging formatters
all over the place. The end-result: All projects have a slightly different
formatting.

The aims of ``gouge`` are:

* be a repository of simple drop-in (and reusable) logging formatters.
* have a more uniform looking output across multiple applications.
* make formatting of the logs a simple one-liner.
* provide additional functionality complementing the standard logging
  framework.


Why the name "gouge"?
---------------------

A "gouge_" is a type of chisel. A tool used in woodworking. And as this module
applies some style to the "logging" module, I found this an appropriate name
for the project. As "chisel" is already taken as a Python module, this was the
next best choice.

.. _gouge: https://en.wikipedia.org/wiki/Chisel#Gouge


Examples
========

Simple Usage example
--------------------

::

    import logging
    from gouge.colourcli import Simple
    Simple.basicConfig(level=logging.DEBUG)

    logging.info('Hello World!')


In this case, :py:meth:`~gouge.colourcli.Simple.basicConfig` is directly passed
on to :py:meth:`logging.basicConfig` but will pepper things up by overriding
the ``format`` argument of the defaul ``basicConfig`` implementation.


Manual Usage
------------

::

    import logging

    from gouge.colourcli import Simple


    LOG = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(Simple())

    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)
    LOG.debug('hello')
    LOG.info('hello')
    LOG.warning('hello')
    LOG.error('hello')


Usage with dictConfig
---------------------

When using ``dictConfig``, you can use the ``gouge.colourcli.Simple`` formatter as class:

.. code-block:: python

    import logging

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "myFormatter": {
                "()": "gouge.colourcli.Simple",
                "show_exc": True,
                "show_threads": True,
                "show_pid": True,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "myFormatter",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                'level": "DEBUG",
            },
        },
    }

    logging.config.dictConfig(LOGGING)
    logging.debug("hello")
    logging.info("hello")
    logging.warning("hello")
    logging.error("hello")



Caveats
=======

You should be aware, that the ``basicConfig`` methods are fairly intrusive.
They first call :py:func:`logging.basicConfig()`, then look for every
``stdout`` and every ``stderr`` handler attached to the root logger and replace
their formatter.


Themes
======

Currently I only use the :py:class:`~gouge.colourcli.Simple` theme. I may or
may not add new themes to the project. I am open for pull-requests as long as
they don't include hefty dependencies!

As sort of a "demo", I also added :py:class:`~gouge.parseable.CSVLog` and
:py:class:`~gouge.parseable.XMLLog`.


Module Contents
===============

.. toctree::
   :maxdepth: 4

   changelog
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
