#!/bin/bash

echo "Downloading clip_vision_h.safetensors"
cd /ComfyUI/models/clip_vision/

file="clip_vision_h.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading Wan2_1-InfiniTetalk-Single_fp16.safetensors"
cd /ComfyUI/models/diffusion_models/

file="Wan2_1-InfiniTetalk-Single_fp16.safetensors"
url="https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors"
cd /ComfyUI/models/loras/

file="lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors"
url="https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi


echo "Downloading MelBandRoformer_fp16.safetensors"
cd /ComfyUI/models/diffusion_models/

file="MelBandRoformer_fp16.safetensors"
url="https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp16.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wav2vec2-chinese-base_fp16.safetensors"
mkdir -p /ComfyUI/models/wav2vec2/
cd /ComfyUI/models/wav2vec2/

file="wav2vec2-chinese-base_fp16.safetensors"
url="https://huggingface.co/Kijai/wav2vec2_safetensors/resolve/main/wav2vec2-chinese-base_fp16.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading umt5-xxl-enc-bf16.safetensors"
cd /ComfyUI/models/text_encoders/

file="umt5-xxl-enc-bf16.safetensors"
url="https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/umt5-xxl-enc-bf16.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors"
cd /ComfyUI/models/diffusion_models/

file="Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors"
url="https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan_2.1_vae.safetensors"
cd /ComfyUI/models/vae/

file="wan_2.1_vae.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi