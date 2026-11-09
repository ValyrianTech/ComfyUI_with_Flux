#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

# Download files

download_file "/ComfyUI/models/vae" "minimax_h3_audio_vae_fp32.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors?download=true"
download_file "/ComfyUI/models/vae" "minimax_h3_video_vae_fp16.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "minimax_h3_fl2va_bf16.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_bf16.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "minimax_h3_ref2va_bf16.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_bf16.safetensors?download=true"
download_file "/ComfyUI/models/text_encoders" "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors?download=true"
download_file "/ComfyUI/models/loras" "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors?download=true"
download_file "/ComfyUI/models/loras" "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors?download=true"
download_file "/ComfyUI/models/loras" "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors" "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors?download=true"

download_wait
