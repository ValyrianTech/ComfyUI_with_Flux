#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading Upscale models"

download_file "/ComfyUI/models/upscale_models" "4x-UltraSharp.pth" "https://civitai.com/api/download/models/125843?type=Model&format=PickleTensor"

download_wait
