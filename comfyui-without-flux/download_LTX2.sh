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
# 27GB model
#download_file "/ComfyUI/models/checkpoints" "ltx-2-19b-dev-fp8.safetensors" "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev-fp8.safetensors?download=true"

# 40GB model
download_file "/ComfyUI/models/checkpoints" "ltx-2-19b-dev.safetensors" "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors?download=true"

download_file "/ComfyUI/models/loras" "ltx-2-19b-distilled-lora-384.safetensors" "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-ic-lora-detailer.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Detailer/resolve/main/ltx-2-19b-ic-lora-detailer.safetensors?download=true"
download_file "/ComfyUI/models/latent_upscale_models" "ltx-2-spatial-upscaler-x2-1.0.safetensors" "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "MelBandRoformer_fp32.safetensors" "https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp32.safetensors?download=true"
download_file "/ComfyUI/models/text_encoders" "gemma_3_12B_it_fp8_e4m3fn.safetensors" "https://huggingface.co/GitMylo/LTX-2-comfy_gemma_fp8_e4m3fn/resolve/main/gemma_3_12B_it_fp8_e4m3fn.safetensors?download=true"
download_file "/ComfyUI/models/checkpoints/audio_vae" "diffusion_pytorch_model.safetensors" "https://huggingface.co/Lightricks/LTX-2/resolve/main/audio_vae/diffusion_pytorch_model.safetensors?download=true"
download_file "/ComfyUI/models/checkpoints/audio_vae" "config.json" "https://huggingface.co/Lightricks/LTX-2/resolve/main/audio_vae/config.json?download=true"

download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-static.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Static/resolve/main/ltx-2-19b-lora-camera-control-static.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-left.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Left/resolve/main/ltx-2-19b-lora-camera-control-dolly-left.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-right" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Right/resolve/main/ltx-2-19b-lora-camera-control-dolly-right.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-in.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-In/resolve/main/ltx-2-19b-lora-camera-control-dolly-in.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-out.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Out/resolve/main/ltx-2-19b-lora-camera-control-dolly-out.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-jib-down.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Jib-Down/resolve/main/ltx-2-19b-lora-camera-control-jib-down.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-jib-up.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Jib-Up/resolve/main/ltx-2-19b-lora-camera-control-jib-up.safetensors?download=true"
