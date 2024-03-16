#!/bin/bash

mkdir -p ~/opt/python-tools
python3 -m venv ~/opt/python-tools
~/opt/python-tools/bin/pip install -U pip
~/opt/python-tools/bin/pip install pipx
~/opt/python-tools/bin/pipx install fabric

grep -qxF '~/opt/python-tools/bin/pip' ~/.bashrc || \
    echo 'export PATH=~/opt/python-tools/bin:${PATH}' \
    >> ~/.bashrc

fab develop
