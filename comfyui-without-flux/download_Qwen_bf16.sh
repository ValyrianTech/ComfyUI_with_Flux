#!/bin/bash

echo "Downloading qwen_2.5_vl_7b_fp8_scaled.safetensors text encoders"
cd /ComfyUI/models/text_encoders/

file="qwen_2.5_vl_7b_fp8_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi


echo "Downloading qwen_image_vae.safetensors"
cd /ComfyUI/models/vae/

file="qwen_image_vae.safetensors"
url="https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading qwen_image_fp8_e4m3fn.safetensors"
cd /ComfyUI/models/diffusion_models/

file="qwen_image_fp8_e4m3fn.safetensors"
url="https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading qwen_image_edit_2509_bf16.safetensors"
cd /ComfyUI/models/diffusion_models/

file="qwen_image_edit_2509_bf16.safetensors"
url="https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_bf16.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors"
cd /ComfyUI/models/loras/

file="Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors"
url="https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi
