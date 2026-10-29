#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading Wan 2.2 models"

download_file "/ComfyUI/models/text_encoders" "umt5_xxl_fp8_e4m3fn_scaled.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
download_file "/ComfyUI/models/vae" "wan_2.1_vae.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"
download_file "/ComfyUI/models/diffusion_models" "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
download_file "/ComfyUI/models/diffusion_models" "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
download_file "/ComfyUI/models/diffusion_models" "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
download_file "/ComfyUI/models/diffusion_models" "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
download_file "/ComfyUI/models/loras" "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
download_file "/ComfyUI/models/loras" "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"

download_wait
