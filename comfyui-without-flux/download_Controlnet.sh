#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading Controlnet models"

download_file "/ComfyUI/models/controlnet" "diffusion_pytorch_model.safetensors" "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/diffusion_pytorch_model.safetensors?download=true"
download_file "/ComfyUI/models/controlnet" "xinsir_controlnet_union-sdxl-1-promax.safetensors" "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors?download=true"
download_file "/ComfyUI/models/upscale_models" "4x-UltraSharp.pth" "https://civitai.com/api/download/models/125843?type=Model&format=PickleTensor"

download_wait
