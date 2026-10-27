Contributing
============

Scope
-----

gouge provides formatters and filters for the Python ``logging`` module:
a coloured console formatter, machine-readable formatters, pre-formatters
and helpers for uvicorn. It stays small and depends only on ``colorama``.
Welcome contributions:

- bug fixes,
- work on open issues,
- support for new Python versions,
- security fixes,
- documentation and tooling improvements.

For a new feature, open an issue first so the design can be agreed before
the work starts. A new dependency needs a very good reason.

Changes follow the `compatibility policy
<https://exhuma.github.io/gouge/#compatibility>`_: a breaking change waits
for a major release, and a removal is deprecated with a
``DeprecationWarning`` and a changelog entry in a minor release first.

Getting started
---------------

1. Fork the repository and clone your fork.
2. Install `uv <https://docs.astral.sh/uv/>`_.
3. Install the project and its development dependencies:

   .. code-block:: console

      $ uv sync

4. Install the pre-commit hooks:

   .. code-block:: console

      $ uvx pre-commit install

Running tests
-------------

.. code-block:: console

   $ uv run pytest

The test run includes the examples in ``README.rst``, ``docs/*.rst`` and
the docstrings as doctests. ``conftest.py`` at the repository root gives
each of them a clean logging set-up, sets ``NO_COLOR`` and fixes the time
of every record, so the expected output is stable. Coverage must stay at
100% (``--cov-fail-under=100``, configured in ``pyproject.toml``).

Code style
----------

The project uses `ruff <https://docs.astral.sh/ruff/>`_ for linting and
formatting, and ``mypy`` in strict mode. The pre-commit hooks run these
checks, and check spelling with `cspell <https://cspell.org/>`_. Run them
on every file:

.. code-block:: console

   $ uvx pre-commit run --all-files

Add a real term to ``project-words.txt``; fix a typo in the text instead.
The project uses British spelling ("colour") in prose and names.

Documentation
-------------

The documentation is built with Sphinx on the ``michel-albert-sphinx``
design system. CI builds it with ``-n -W`` (unresolved references and
warnings are errors) on every push and pull request, and
``.github/workflows/docs.yml`` publishes it to GitHub Pages
(https://exhuma.github.io/gouge/) on every push to ``master``. Build it
locally with:

.. code-block:: console

   $ uv run sphinx-build -n -W --keep-going -b html docs docs/_build/html

The API reference has one hand-written page per public module in
``docs/api/``. Add a page there when you add a public module.

Submitting changes
------------------

Open a pull request with a clear description of what changed and why. If
you fix a bug, include a test that reproduces it. Commits follow
`Conventional Commits <https://www.conventionalcommits.org/>`_.

Python support policy
---------------------

gouge supports every CPython version that has not reached its end of life.
CI computes that list from `endoflife.date <https://endoflife.date/python>`_
and tests each version, plus the upcoming pre-release (informational only).
A monthly scheduled run detects breakage caused by new Python releases.

``requires-python`` is the oldest supported version at release time. When
a version reaches its end of life, CI warns, and the next minor release
raises ``requires-python``. Update the
``Programming Language :: Python :: 3.x`` classifiers at the same time.

Dependency updates
------------------

The only runtime dependency is ``colorama``. Development tools are pinned
in ``uv.lock`` and ``.pre-commit-config.yaml``, and GitHub Actions are
pinned by tag, so nothing changes unless a maintainer updates it on
purpose. There are no automated version-update pull requests: the monthly
scheduled CI run is the signal. When it fails because of an outdated tool
or action, update it then (``uv lock --upgrade``,
``uvx pre-commit autoupdate``, or bump the action).

Security fixes are the exception. When an advisory affects a locked
dependency or a workflow action, Dependabot opens one grouped
security-update pull request (see ``.github/dependabot.yml``). Merge it
once CI is green.

Release procedure
-----------------

1. Bump ``version`` in ``pyproject.toml``, add the release to
   ``docs/changelog.rst``, and update the classifiers and
   ``requires-python`` if needed.
2. Merge to ``master``.
3. Tag the merge commit as ``vX.Y.Z`` and push the tag.
4. CI builds and inspects the packages and publishes that exact build to
   PyPI through Trusted Publishing. The job fails if the tag does not
   match the package version.

One-time setup
~~~~~~~~~~~~~~

Needed only once:

- On PyPI, add a trusted publisher to the project: owner ``exhuma``,
  repository ``gouge``, workflow ``pythonpackage.yml``, environment
  ``pypi``.
- In the GitHub repository settings, create the ``pypi`` environment.
- In the GitHub repository settings, set Pages to deploy from "GitHub
  Actions".
