#!/bin/bash

echo "Installing VibeVoice"
mkdir -p /ComfyUI/models/vibevoice
cd /ComfyUI/models/vibevoice
git clone https://huggingface.co/aoi-ot/VibeVoice-Large VibeVoice-Large


echo "Installing Qwen tokenizer"
mkdir -p /ComfyUI/models/vibevoice/tokenizer
cd /ComfyUI/models/vibevoice/tokenizer
git clone https://huggingface.co/Qwen/Qwen2.5-1.5B .