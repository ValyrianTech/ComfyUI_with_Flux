#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

# Download files

download_file "/ComfyUI/models/text_encoders" "qwen_3_4b.safetensors" "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors?download=true"
download_file "/ComfyUI/models/vae" "ae.safetensors" "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "z_image_turbo_bf16.safetensors" "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors?download=true"

download_wait
