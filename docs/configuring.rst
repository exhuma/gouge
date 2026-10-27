Configuration files
===================

Every option of :class:`~gouge.colourcli.Simple` works with
:func:`logging.config.dictConfig`, and so with configuration files in YAML
or JSON. Name the formatter class with the special key ``"()"``; the other
keys of the formatter become keyword arguments.

.. note::

   Use ``"()"``, not ``"class"``. With ``"class"``, ``dictConfig`` passes
   only the standard :class:`logging.Formatter` arguments and drops the
   gouge options.

Configure with a dictionary
---------------------------

>>> import logging.config
>>> logging.config.dictConfig({
...     "version": 1,
...     "disable_existing_loggers": False,
...     "formatters": {
...         "console": {
...             "()": "gouge.colourcli.Simple",
...             "show_exc": True,
...             "show_threads": True,
...         },
...     },
...     "handlers": {
...         "console": {
...             "class": "logging.StreamHandler",
...             "formatter": "console",
...         },
...     },
...     "root": {
...         "handlers": ["console"],
...         "level": "DEBUG",
...     },
... })
>>> logging.getLogger("app").info("Ready")
MainThread 2026-10-27 13:34:48,899 INFO       [app] Ready

Configure with a YAML file
--------------------------

Pre-formatters are given as dotted paths, so a YAML file can set them too.
This file colours uvicorn's access log, shows tracebacks, and sets the
levels of the application and of uvicorn:

.. literalinclude:: examples/logging.yaml
   :language: yaml
   :caption: logging.yaml

Load it with `PyYAML <https://pypi.org/project/PyYAML/>`_ and pass the
result to :func:`~logging.config.dictConfig`:

>>> import yaml
>>> with open("examples/logging.yaml") as stream:
...     config = yaml.safe_load(stream)
>>> logging.config.dictConfig(config)
>>> logging.getLogger("app").debug("Loaded")
2026-10-27 13:34:48,899 DEBUG      [app] Loaded
>>> logging.getLogger("uvicorn.access").info(
...     '%s - "%s %s HTTP/%s" %d',
...     "127.0.0.1:52341",
...     "GET", "/", "1.1", 200,
... )
2026-10-27 13:34:48,899 INFO       [uvicorn.access] 127.0.0.1:52341 - "GET / HTTP/1.1" 200

Before 2.3, pre-formatters had to be callables, so a configuration file
needed a subclass of :class:`~gouge.colourcli.Simple` which set them in its
constructor. Dotted paths replace that subclass.

The parseable formatters work the same way, for example
``{"()": "gouge.parseable.JSONLog"}``. See :doc:`structured-output`.
