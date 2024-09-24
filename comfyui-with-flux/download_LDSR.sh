#!/bin/bash

echo "Installing LDSR"
cd /ComfyUI/models/upscale_models

file="LDSR.ckpt"
url="https://heibox.uni-heidelberg.de/f/578df07c8fc04ffbadf3/?dl=1"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi
