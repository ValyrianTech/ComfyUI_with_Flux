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

# A node's requirements can downgrade packages the bundled nodes need (e.g. numpy<2 or an old
# scipy/av), which made ComfyUI crash on import before. Check the core imports after installing.
if compgen -G "$NODES/*/requirements.txt" >/dev/null; then
    if ! "$PYTHON" -c "import numpy, scipy, scipy.ndimage, torch, av" 2>/tmp/user_nodes_import_check.log; then
        echo "WARNING: after installing the requirements of your custom nodes, numpy/scipy/torch/av no longer import"
        echo "WARNING: ComfyUI will probably fail to start. Error (also in /tmp/user_nodes_import_check.log):"
        tail -5 /tmp/user_nodes_import_check.log
        echo "WARNING: disable the node that caused it by renaming its folder in $NODES to NAME.disabled"
    fi
fi
