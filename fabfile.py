import fabric.api as fab


@fab.task
def doc():
    fab.local("./env/bin/sphinx-build " "docs " "docs/_build/html")


@fab.task
def publish():
    fab.local("./env/bin/python setup.py sdist bdist_wheel")
    fab.local("./env/bin/twine upload dist/*")
    fab.local("rm -rf dist")
