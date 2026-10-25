#!/bin/bash

pkg_list=$(pip freeze | grep -v '^\-e')

if [ ! -d "/workspace/venv" ]
then
    python3 -m venv /workspace/venv
    source /workspace/venv/bin/activate
    if [ -n "$pkg_list" ]
    then
        # Install everything in one go (one resolve, parallel-friendly); fall back to one package at a
        # time so a single package that fails to install doesn't stop the rest.
        echo "$pkg_list" > /tmp/venv_requirements.txt
        pip install -r /tmp/venv_requirements.txt || echo "$pkg_list" | xargs -n1 pip install
    else
        echo "No packages to install from the system's Python environment."
    fi
else
    echo "venv directory already exists"
fi
