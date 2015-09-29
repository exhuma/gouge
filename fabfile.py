import fabric.api as fab


@fab.task
def doc():
    fab.local('./env/bin/sphinx-build '
              'docs '
              'docs/_build/html')
