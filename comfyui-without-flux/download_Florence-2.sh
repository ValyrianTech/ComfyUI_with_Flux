#!/bin/bash

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

echo "Downloading Florence 2 models"

download_file "/ComfyUI/models/LLM" "Florence-2-large-ft.bin" "https://huggingface.co/microsoft/Florence-2-large-ft/resolve/main/pytorch_model.bin?download=true"
download_file "/ComfyUI/models/LLM" "Florence-2-DocVQA.bin" "https://huggingface.co/HuggingFaceM4/Florence-2-DocVQA/resolve/main/model.safetensors?download=true"

download_wait
