#!/bin/bash
# The Mixlab nodes are not in the image: they take a long time to load and none of the included
# workflows need them. Set ENABLE_MIXLAB=true to have them downloaded to the volume on pod start
# (their requirements are installed by /install_user_custom_nodes.sh). When ENABLE_MIXLAB is off,
# nothing is downloaded and a copy left on the volume by an earlier pod is disabled.

NODES=/workspace/comfyui-data/custom_nodes
dir="$NODES/comfyui-mixlab-nodes"

if [[ "${ENABLE_MIXLAB,,}" =~ ^(true|1|yes|on)$ ]]; then
    if [ -d "$dir.disabled" ] && [ ! -d "$dir" ]; then
        mv "$dir.disabled" "$dir"
        echo "Mixlab nodes enabled"
    elif [ ! -d "$dir" ]; then
        echo "Downloading the Mixlab nodes (ENABLE_MIXLAB=true)"
        mkdir -p "$NODES"
        git clone --depth 1 https://github.com/shadowcz007/comfyui-mixlab-nodes.git "$dir" || \
            echo "WARNING: could not download the Mixlab nodes"
    fi
elif [ -d "$dir" ]; then
    rm -rf "$dir.disabled"
    mv "$dir" "$dir.disabled"
    echo "Mixlab nodes disabled (set ENABLE_MIXLAB=true to use them)"
fi
