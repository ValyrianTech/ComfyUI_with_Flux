#!/bin/bash

if [[ -z "${HF_TOKEN}" ]] || [[ "${HF_TOKEN}" == "enter_your_huggingface_token_here" ]]
then
    echo "HF_TOKEN is not set, can not download flux because it is a gated repository."
else
    echo "HF_TOKEN is set, checking files..."

    if [[ ! -e "/ComfyUI/models/vae/ae.sft" ]]
    then
        echo "Downloading ae.sft..."
        wget -O "/ComfyUI/models/vae/ae.sft" --header="Authorization: Bearer ${HF_TOKEN}" "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors?download=true"
    else
        echo "ae.sft already exists, skipping download."
    fi

    if [[ ! -e "/ComfyUI/models/diffusion_models/flux1-dev.sft" ]]
    then
        echo "Downloading flux1-dev.sft..."
        wget -O "/ComfyUI/models/diffusion_models/flux1-dev.sft" --header="Authorization: Bearer ${HF_TOKEN}" "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors?download=true"
    else
        echo "flux1-dev.sft already exists, skipping download."
    fi

    if [[ ! -e "/ComfyUI/models/diffusion_models/flux1-kontext-dev.safetensors" ]]
    then
        echo "Downloading flux1-kontext-dev.safetensors..."
        wget -O "/ComfyUI/models/diffusion_models/flux1-kontext-dev.safetensors" --header="Authorization: Bearer ${HF_TOKEN}" "https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/resolve/main/flux1-kontext-dev.safetensors?download=true"
    else
        echo "flux1-kontext-dev.safetensors already exists, skipping download."
    fi

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
download_file "/ComfyUI/models/clip" "clip_l.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true"
download_file "/ComfyUI/models/clip" "t5xxl_fp8_e4m3fn.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true"
download_file "/ComfyUI/models/loras" "GracePenelopeTargaryenV5.safetensors" "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryenV5/resolve/main/GracePenelopeTargaryenV5.safetensors?download=true"
download_file "/ComfyUI/models/loras" "VideoAditor_flux_realism_lora.safetensors" "https://huggingface.co/VideoAditor/Flux-Lora-Realism/resolve/main/flux_realism_lora.safetensors?download=true"
download_file "/ComfyUI/models/xlabs/loras" "Xlabs-AI_flux-RealismLora.safetensors" "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors?download=true"
