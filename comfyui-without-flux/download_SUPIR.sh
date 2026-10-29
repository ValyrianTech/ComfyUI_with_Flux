#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Installing SUPIR"

download_file "/ComfyUI/models/checkpoints" "SUPIR-v0Q_fp16.safetensors" "https://huggingface.co/Kijai/SUPIR_pruned/resolve/main/SUPIR-v0Q_fp16.safetensors?download=true"
download_file "/ComfyUI/models/checkpoints" "LightningBaked.safetensors" "https://civitai.com/api/download/models/361593?type=Model&format=SafeTensor&size=pruned&fp=fp16"

download_wait
