#!/bin/bash

echo "Downloading Shakker-labs Controlnet"
cd /ComfyUI/models/controlnet

file="diffusion_pytorch_model.safetensors"
url="https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/diffusion_pytorch_model.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading xinsir controlnet"
cd /ComfyUI/models/controlnet

file="xinsir_controlnet_union-sdxl-1-promax.safetensors"
url="https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading 4x-UltraSharp.pth"
cd /ComfyUI/models/upscale_models
file="4x-UltraSharp.pth"
url="https://civitai.com/api/download/models/125843?type=Model&format=PickleTensor"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi