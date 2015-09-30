Welcome to chisel's documentation!
==================================


.. figure:: _static/snapshot1.png
    :alt: Example screenshot

    Example screenshot using the ``colourcli.Simple`` formatter.


The What and the Why
--------------------

``chisel`` is a very simple package to simplify some logging setup. Think of it
as "Themes for the logging module". It is very "thin", and has no dependencies
other than :py:mod:`blessings`. :py:mod:`blessings` is only used for formatting
(colour, bold, …).

I have a fair amount of applications which log to the console. While the
default formatting given by :py:func:`logging.basicConfig()` is usable, I
always end up modifying it. Mostly just adding horizontal whitespace to make it
more readable. Adding colour helps, and I've added it to some projects. My
co-workers are in the same boat, and we end up copy/pasting logging formatters
all over the place. The end-result: All projects have a slightly different
formatting.

The aims of ``chisel`` are:

* be a repository of simple drop-in (and reusable) logging formatters.
* have a more uniform looking output across multiple applications.
* make formatting of the logs a simple one-liner.


Why the name "chisel"?
----------------------

A "chisel_" is a tool used in woodworking. And as this module applies some
style to the "logging" module, I found this an appropriate name for the
project.

.. _chisel: https://en.wikipedia.org/wiki/Chisel


Examples
========

Simple Usage example
--------------------

::

    from chisel.colourcli import Simple
    Simple.basicConfig(level=logging.DEBUG)


In this case, ``Simple.basicConfig`` is directly passed on to
:py:meth:`logging.basicConfig` but will pepper things up by overriding the
``format`` argument of the defaul ``basicConfig`` implementation.


Manual Usage
------------

::

    import logging

    from chisel.colourcli import Simple


    LOG = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(Simple())

    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)
    LOG.debug('hello')
    LOG.info('hello')
    LOG.warning('hello')
    LOG.error('hello')


Caveats
=======

You should be aware, that the ``basicConfig`` methods are fairly intrusive.
They first call :py:func:`logging.basicConfig()`, then look for every
``stdout`` and every ``stderr`` handler attached to the root logger and replace
their formatter.


Themes
======

Currently I only use the :py:class:`~chisel.colourcli.Simple` theme. I may or
may not add new themes to the project. I am open for pull-requests as long as
they don't include hefty dependencies!

As sort of a "demo", I also added :py:class:`~chisel.parseable.CSVLog` and
:py:class:`~chisel.parseable.XMLLog`.


Module Contents
===============

.. toctree::
   :maxdepth: 4

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

