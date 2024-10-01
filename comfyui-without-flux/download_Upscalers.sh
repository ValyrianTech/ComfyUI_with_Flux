#!/bin/bash

echo "Donwloading Upscale models"

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