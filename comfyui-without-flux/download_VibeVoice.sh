#!/bin/bash

echo "Installing VibeVoice"
VV=/ComfyUI/models/vibevoice

# Each repo is cloned to NAME.part and renamed when complete, so an interrupted clone is redone on
# the next run instead of being taken for a finished one
clone_repo() {
    local url=$1
    local dst=$2
    if [ -d "$dst/.git" ]; then
        echo "$(basename "$dst") already exists, skipping."
        return 0
    fi
    rm -rf "$dst.part"
    git clone "$url" "$dst.part" && { [ ! -e "$dst" ] || rmdir "$dst"; } && mv "$dst.part" "$dst"
}

mkdir -p "$VV"
# The model and the tokenizer are independent repos, clone them at the same time
clone_repo https://huggingface.co/aoi-ot/VibeVoice-Large "$VV/VibeVoice-Large" &
clone_repo https://huggingface.co/Qwen/Qwen2.5-1.5B "$VV/tokenizer" &
wait
