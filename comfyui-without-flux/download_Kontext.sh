#!/bin/bash
# Flux.1-Kontext-dev (image editing, ~24 GB). Its own set so that ComfyUI doesn't wait for it:
# DOWNLOAD_FLUX_KONTEXT=true (see download_selected.sh). Needs HF_TOKEN, it is a gated repository.

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

HF_AUTH=$(hf_auth_header)
if [[ -z "${HF_AUTH}" ]]
then
    echo "HF_TOKEN is not set, can not download Flux.1-Kontext because it is a gated repository."
else
    download_file "/ComfyUI/models/diffusion_models" "flux1-kontext-dev.safetensors" "https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/resolve/main/flux1-kontext-dev.safetensors?download=true" "${HF_AUTH}"
fi

download_wait
