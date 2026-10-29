#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

HF_AUTH=$(hf_auth_header)
if [[ -z "${HF_AUTH}" ]]
then
    echo "HF_TOKEN is not set, can not download flux because it is a gated repository."
else
    echo "HF_TOKEN is set, checking files..."
    download_file "/ComfyUI/models/vae" "ae.sft" "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors?download=true" "${HF_AUTH}"
    download_file "/ComfyUI/models/diffusion_models" "flux1-dev.sft" "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors?download=true" "${HF_AUTH}"
fi

# Download files
download_file "/ComfyUI/models/clip" "clip_l.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true"
download_file "/ComfyUI/models/clip" "t5xxl_fp8_e4m3fn.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true"
download_file "/ComfyUI/models/loras" "GracePenelopeTargaryenV5.safetensors" "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryenV5/resolve/main/GracePenelopeTargaryenV5.safetensors?download=true"
download_file "/ComfyUI/models/loras" "VideoAditor_flux_realism_lora.safetensors" "https://huggingface.co/VideoAditor/Flux-Lora-Realism/resolve/main/flux_realism_lora.safetensors?download=true"
download_file "/ComfyUI/models/xlabs/loras" "Xlabs-AI_flux-RealismLora.safetensors" "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors?download=true"

download_wait
