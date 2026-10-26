# type: ignore
from fabric import task


@task
def doc(context):
    context.run("rm -rf docs/api", pty=True, replace_env=False)
    context.run(
        "uv run sphinx-apidoc -o docs/api src/gouge",
        pty=True,
        replace_env=False,
    )
    context.run(
        "uv run sphinx-build docs docs/_build/html",
        pty=True,
        replace_env=False,
    )


@task
def publish(context):
    context.run("./env/bin/python setup.py sdist bdist_wheel")
    context.run("./env/bin/twine upload dist/*")
    context.run("rm -rf dist")


@task
def develop(context):
    context.run("uv sync", replace_env=False, pty=True)
