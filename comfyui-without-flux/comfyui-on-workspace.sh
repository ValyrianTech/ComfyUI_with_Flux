#!/bin/bash

# Ensure we have /workspace in all scenarios
mkdir -p /workspace

if [[ ! -d /workspace/ComfyUI ]]; then
	# If we don't already have /workspace/ComfyUI, move it there
	echo "Copying ComfyUI to /workspace for persistence, this might take a while"
	mv /ComfyUI /workspace
else
	# otherwise delete the default ComfyUI folder which is always re-created on pod start from the Docker
	rm -rf /ComfyUI
fi

# Then link /ComfyUI folder to /workspace so it's available in that familiar location as well
ln -s /workspace/ComfyUI /ComfyUI
