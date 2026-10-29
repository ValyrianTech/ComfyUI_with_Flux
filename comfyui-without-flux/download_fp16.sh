#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading t5xxl_fp16 text encoder"

download_file "/ComfyUI/models/clip" "t5xxl_fp16.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors?download=true"

download_wait
