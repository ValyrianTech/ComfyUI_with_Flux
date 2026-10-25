#!/bin/bash
# Installs the Python requirements of the custom nodes you installed yourself
# (/workspace/comfyui-data/custom_nodes). The Python environment lives in the image and starts
# fresh on every pod, so this runs on every start; requirements that are already satisfied are
# skipped quickly. Disabled nodes (*.disabled) are left alone.

NODES=/workspace/comfyui-data/custom_nodes
PYTHON=$(command -v python3)

for req in "$NODES"/*/requirements.txt; do
    [ -f "$req" ] || continue
    node=$(basename "$(dirname "$req")")
    [[ "$node" == *.disabled ]] && continue
    echo "Installing requirements of user custom node $node"
    uv pip install --python "$PYTHON" -r "$req" || pip install -r "$req" || \
        echo "WARNING: could not install the requirements of $node"
done
