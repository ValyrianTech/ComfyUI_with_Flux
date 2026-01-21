#!/bin/bash

# Define the download function
download_file() {
    local dir=$1
    local file=$2
    local url=$3

    mkdir -p $dir
    if [ -f "$dir/$file" ]; then
        echo "File $dir/$file already exists, skipping download."
    else
        wget -O "$dir/$file" "$url" --progress=bar:force:noscroll
    fi
}

# Download files

download_file "/ComfyUI/models/text_encoders" "qwen_3_4b.safetensors" "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors?download=true"
download_file "/ComfyUI/models/vae" "ae.safetensors" "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "z_image_turbo_bf16.safetensors" "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors?download=true"
