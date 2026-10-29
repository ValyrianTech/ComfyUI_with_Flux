#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading Wan 2.1 InfiniteTalk models"

download_file "/ComfyUI/models/clip_vision" "clip_vision_h.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"
download_file "/ComfyUI/models/diffusion_models" "Wan2_1-InfiniTetalk-Single_fp16.safetensors" "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors"
download_file "/ComfyUI/models/loras" "lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors" "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors"
download_file "/ComfyUI/models/diffusion_models" "MelBandRoformer_fp16.safetensors" "https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp16.safetensors"
download_file "/ComfyUI/models/wav2vec2" "wav2vec2-chinese-base_fp16.safetensors" "https://huggingface.co/Kijai/wav2vec2_safetensors/resolve/main/wav2vec2-chinese-base_fp16.safetensors"
download_file "/ComfyUI/models/text_encoders" "umt5-xxl-enc-bf16.safetensors" "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/umt5-xxl-enc-bf16.safetensors"
download_file "/ComfyUI/models/diffusion_models" "Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors" "https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors"
download_file "/ComfyUI/models/vae" "wan_2.1_vae.safetensors" "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"

download_wait
