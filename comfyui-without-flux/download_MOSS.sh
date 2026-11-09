#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

# Download files

download_file "/ComfyUI/models/vae" "flux2-vae.safetensors" "https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/vae/flux2-vae.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "moss_image_base_bf16.safetensors" "https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/diffusion_models/moss_image_base_bf16.safetensors?download=true"
download_file "/ComfyUI/models/text_encoders" "qwen3.5_9b_w4a8_gptq.safetensors" "https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/text_encoders/qwen3.5_9b_w4a8_gptq.safetensors?download=true"
download_file "/ComfyUI/models/loras" "moss_image_edit_lora_rank_64_bf16.safetensors" "https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/loras/moss_image_edit_lora_rank_64_bf16.safetensors?download=true"

download_wait
