#!/bin/bash

pkg_list=$(pip freeze | grep -v '^\-e')

if [ ! -d "/workspace/venv" ]
then
    python3 -m venv /workspace/venv
    source /workspace/venv/bin/activate
    if [ -n "$pkg_list" ]
    then
        echo $pkg_list | xargs -n1 pip install
    else
        echo "No packages to install from the system's Python environment."
    fi
else
    echo "venv directory already exists"
fi
