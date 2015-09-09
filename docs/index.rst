Welcome to gouge's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2


``gouge`` is a very simple package to simplify some logging setup. Think of it
as "Themes for the logging module". It is very "thin", and has no dependencies
other than ``blessings``. ``blessings`` is only used for formatting (colour,
bold, ...).

This is currently refactored out into a separate module such that I can use the
same format in multiple applications.


Usage example
-------------

::

    from gouge.colourcli import Simple
    Simple.basicConfig(level=logging.DEBUG)


In this case, ``basicConfig`` is directly passed on to
:py:meth:`logging.basicConfig` but will pepper things up. For this reason, the
``format`` paramter in this call will be overridden.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

