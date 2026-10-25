#!/bin/bash

echo "Installing VibeVoice"
mkdir -p /ComfyUI/models/vibevoice/tokenizer

# The model and the tokenizer are independent repos, clone them at the same time
if [ ! -d /ComfyUI/models/vibevoice/VibeVoice-Large/.git ]; then
    git clone https://huggingface.co/aoi-ot/VibeVoice-Large /ComfyUI/models/vibevoice/VibeVoice-Large &
else
    echo "VibeVoice-Large already exists, skipping."
fi
if [ ! -d /ComfyUI/models/vibevoice/tokenizer/.git ]; then
    echo "Installing Qwen tokenizer"
    git clone https://huggingface.co/Qwen/Qwen2.5-1.5B /ComfyUI/models/vibevoice/tokenizer &
else
    echo "Qwen tokenizer already exists, skipping."
fi
wait
