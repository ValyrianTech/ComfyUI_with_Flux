#!/bin/bash

if [[ -z "${HF_TOKEN}" ]] || [[ "${HF_TOKEN}" == "enter_your_huggingface_token_here" ]]
then
    echo "HF_TOKEN is not set, can not download flux because it is a gated repository."
else
    echo "HF_TOKEN is set, checking files..."
fi

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

download_file "/ComfyUI/models/vae" "flux2-vae.safetensors" "https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "flux2_dev_fp8mixed.safetensors" "https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/diffusion_models/flux2_dev_fp8mixed.safetensors?download=true"
download_file "/ComfyUI/models/text_encoders" "mistral_3_small_flux2_bf16.safetensors" "https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/text_encoders/mistral_3_small_flux2_bf16.safetensors?download=true"
