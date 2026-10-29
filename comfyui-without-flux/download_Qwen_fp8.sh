#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading Qwen Image Edit (fp8) models"

download_file "/ComfyUI/models/text_encoders" "qwen_2.5_vl_7b_fp8_scaled.safetensors" "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"
download_file "/ComfyUI/models/vae" "qwen_image_vae.safetensors" "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors"
download_file "/ComfyUI/models/diffusion_models" "qwen_image_fp8_e4m3fn.safetensors" "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors"
download_file "/ComfyUI/models/diffusion_models" "qwen_image_edit_2509_fp8_e4m3fn.safetensors" "https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors"
download_file "/ComfyUI/models/loras" "Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors" "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors"

download_wait
