#!/bin/bash

echo "Installing SUPIR"
cd /ComfyUI/models/checkpoints

echo "Downloading SUPIR-v0Q_fp16.safetensors"
file="SUPIR-v0Q_fp16.safetensors"
url="https://huggingface.co/Kijai/SUPIR_pruned/resolve/main/SUPIR-v0Q_fp16.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi


echo "Downloading RealVisXL V5.0"
cd /ComfyUI/models/checkpoints
file="LightningBaked.safetensors"
url="https://civitai.com/api/download/models/361593?type=Model&format=SafeTensor&size=pruned&fp=fp16"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi