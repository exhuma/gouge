#!/bin/sh -l

sh -c "python3 -m venv env"
sh -c "./env/bin/pip install -e ."
sh -c "./env/bin/pip install -e pytest"
