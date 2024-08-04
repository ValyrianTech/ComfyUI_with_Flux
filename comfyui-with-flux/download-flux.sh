#!/bin/bash

# Variables for paths
vae_path="/workspace/ComfyUI/models/vae/"
unet_path="/workspace/ComfyUI/models/unet/"
clip_path="/workspace/ComfyUI/models/clip/"

echo "Downloading Flux files..."

# Download and move clip_l.safetensors
wget -O clip_l.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true -P $clip_path

# Download and move t5xxl_fp8_e4m3fn.safetensors
wget -O t5xxl_fp8_e4m3fn.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true -P $clip_path

# Download and move flux_dev_example.png
wget https://github.com/comfyanonymous/ComfyUI_examples/blob/master/flux/flux_dev_example.png -P /workspace/ComfyUI

# Download and move ae.sft
# wget https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.sft -P $vae_path

# Download and move flux1-dev-fp8.safetensors
# wget https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/flux1-dev.sft -P $unet_path

echo "All files have been downloaded and moved to the correct directories."
