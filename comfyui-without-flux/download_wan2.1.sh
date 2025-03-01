#!/bin/bash

echo "Downloading umt5_xxl_fp8_e4m3fn_scaled.safetensors text encoders"
cd /ComfyUI/models/text_encoders/

file="umt5_xxl_fp8_e4m3fn_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi


echo "Downloading wan_2.1_vae.safetensors"
cd /ComfyUI/models/vae/

file="wan_2.1_vae.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.1_i2v_720p_14B_bf16.safetensors"
cd /ComfyUI/models/diffusion_models/

file="wan2.1_i2v_720p_14B_bf16.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_720p_14B_bf16.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading clip_vision_h.safetensors"
cd /ComfyUI/models/clip_vision/

file="clip_vision_h.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.1_t2v_14B_bf16.safetensors"
cd /ComfyUI/models/diffusion_models/

file="wan2.1_t2v_14B_bf16.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_t2v_14B_bf16.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi
