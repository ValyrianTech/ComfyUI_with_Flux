#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

# Download files

download_file "/ComfyUI/models/checkpoints" "yue2_3b_int8_convrot.safetensors" "https://huggingface.co/Comfy-Org/YuE2/resolve/main/checkpoints/yue2_3b_int8_convrot.safetensors?download=true"

download_wait
