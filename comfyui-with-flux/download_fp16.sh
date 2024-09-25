#!/bin/bash

echo "Installing t5xxl_fp16.safetensors text encoders"
cd /ComfyUI/models/clip/

file="t5xxl_fp16.safetensors"
url="https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi
