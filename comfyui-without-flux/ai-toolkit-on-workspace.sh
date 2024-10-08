#!/bin/bash

# Ensure we have /workspace in all scenarios
mkdir -p /workspace

if [[ ! -d /workspace/ai-toolkit ]]; then
	# If we don't already have /workspace/ai-toolkit, move it there
	mv /ai-toolkit /workspace
else
	# otherwise delete the default ai-toolkit folder which is always re-created on pod start from the Docker
	rm -rf /ai-toolkit
fi

# Then link /ai-toolkit folder to /workspace so it's available in that familiar location as well
ln -s /workspace/ai-toolkit /ai-toolkit

# Ensure we have /workspace/training_sets in all scenarios
mkdir -p /workspace/training_set
ln -s /workspace/ai-toolkit/output /workspace/ComfyUI/models/loras/output