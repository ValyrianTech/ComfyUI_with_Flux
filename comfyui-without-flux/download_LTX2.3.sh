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

# 40GB model
#download_file "/ComfyUI/models/checkpoints" "ltx-2.3-22b-dev.safetensors" "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-22b-dev.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "ltx-2.3-22b-dev_transformer_only_bf16.safetensors" "https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/diffusion_models/ltx-2.3-22b-dev_transformer_only_bf16.safetensors?download=true"
download_file "/ComfyUI/models/text_encoders" "gemma_3_12B_it_fp8_e4m3fn.safetensors" "https://huggingface.co/GitMylo/LTX-2-comfy_gemma_fp8_e4m3fn/resolve/main/gemma_3_12B_it_fp8_e4m3fn.safetensors?download=true"
download_file "/ComfyUI/models/text_encoders" "ltx-2.3_text_projection_bf16.safetensors" "https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/text_encoders/ltx-2.3_text_projection_bf16.safetensors?download=true"
download_file "/ComfyUI/models/diffusion_models" "MelBandRoformer_fp32.safetensors" "https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp32.safetensors?download=true"
download_file "/ComfyUI/models/latent_upscale_models" "ltx-2.3-spatial-upscaler-x2-1.0.safetensors" "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-spatial-upscaler-x2-1.0.safetensors?download=true"
download_file "/ComfyUI/models/latent_upscale_models" "ltx-2.3-spatial-upscaler-x1.5-1.0.safetensors" "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-spatial-upscaler-x1.5-1.0.safetensors?download=true"
download_file "/ComfyUI/models/latent_upscale_models" "ltx-2.3-temporal-upscaler-x2-1.0.safetensors" "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-temporal-upscaler-x2-1.0.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors" "https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Union-Control/resolve/main/ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2.3-22b-ic-lora-motion-track-control-ref0.5.safetensors" "https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Motion-Track-Control/resolve/main/ltx-2.3-22b-ic-lora-motion-track-control-ref0.5.safetensors?download=true"
download_file "/ComfyUI/models/vae" "LTX23_audio_vae_bf16.safetensors" "https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/vae/LTX23_audio_vae_bf16.safetensors?download=true"
download_file "/ComfyUI/models/vae" "LTX23_video_vae_bf16.safetensors" "https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/vae/LTX23_video_vae_bf16.safetensors?download=true"
download_file "/ComfyUI/models/vae" "taeltx2_3.safetensors" "https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/vae/taeltx2_3.safetensors?download=true"
download_file "/ComfyUI/models/loras" "ltx-2.3-22b-distilled-lora-384.safetensors" "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-22b-distilled-lora-384.safetensors?download=true"


#
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-static.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Static/resolve/main/ltx-2-19b-lora-camera-control-static.safetensors?download=true"
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-left.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Left/resolve/main/ltx-2-19b-lora-camera-control-dolly-left.safetensors?download=true"
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-right" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Right/resolve/main/ltx-2-19b-lora-camera-control-dolly-right.safetensors?download=true"
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-in.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-In/resolve/main/ltx-2-19b-lora-camera-control-dolly-in.safetensors?download=true"
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-dolly-out.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Out/resolve/main/ltx-2-19b-lora-camera-control-dolly-out.safetensors?download=true"
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-jib-down.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Jib-Down/resolve/main/ltx-2-19b-lora-camera-control-jib-down.safetensors?download=true"
#download_file "/ComfyUI/models/loras" "ltx-2-19b-lora-camera-control-jib-up.safetensors" "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Jib-Up/resolve/main/ltx-2-19b-lora-camera-control-jib-up.safetensors?download=true"
