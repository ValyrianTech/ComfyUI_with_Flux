#!/bin/bash

echo "Downloading Florence 2 models"
mkdir -p /ComfyUI/models/LLM/
cd /ComfyUI/models/LLM/

file="Florence-2-large-ft.bin"
url="https://huggingface.co/microsoft/Florence-2-large-ft/resolve/main/pytorch_model.bin?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi


file="Florence-2-DocVQA.bin"
url="https://huggingface.co/HuggingFaceM4/Florence-2-DocVQA/resolve/main/model.safetensors?download=true"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi
