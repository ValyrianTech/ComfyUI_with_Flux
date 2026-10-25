#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Installing LDSR"

download_file "/ComfyUI/models/upscale_models" "LDSR.ckpt" "https://heibox.uni-heidelberg.de/f/578df07c8fc04ffbadf3/?dl=1"

download_wait
