#!/bin/bash
dir="/workspace/ComfyUI/custom_nodes/comfyui-mixlab-nodes"

if [ -d "$dir" ]
then
    mv "$dir" "$dir.disabled"
    echo "Mixlab nodes has been disabled successfully."
else
    echo "Mixlab nodes not found."
fi
