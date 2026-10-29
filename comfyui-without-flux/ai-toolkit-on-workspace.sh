#!/bin/bash

# Ensure we have /workspace in all scenarios
mkdir -p /workspace

# AI-Toolkit's code (including ui/node_modules, tens of thousands of small files) stays inside the
# image, where it is fast to start. Only the user's data is persisted on the network volume:
#   /workspace/ai-toolkit-data/{config,output,datasets,aitk_db.db}
# /workspace/ai-toolkit is a symlink to /ai-toolkit so all documented paths keep working.
DATA=/workspace/ai-toolkit-data

if [[ -d /workspace/ai-toolkit && ! -L /workspace/ai-toolkit ]]; then
	# Volume initialized by an older image that copied the whole tree to /workspace: keep using it.
	echo "Found existing /workspace/ai-toolkit, using it"
	rm -rf /ai-toolkit
	ln -s /workspace/ai-toolkit /ai-toolkit
else
	mkdir -p "$DATA"
	for item in config output datasets; do
		if [[ ! -e "$DATA/$item" ]]; then
			# First run: seed the persistent folder with the image's defaults (e.g. train_lora.yaml)
			if [[ -d "/ai-toolkit/$item" ]]; then
				cp -a --no-preserve=ownership "/ai-toolkit/$item" "$DATA/$item"
			else
				mkdir -p "$DATA/$item"
			fi
		fi
		rm -rf "/ai-toolkit/$item"
		ln -s "$DATA/$item" "/ai-toolkit/$item"
	done
	# The UI's job database
	if [[ ! -e "$DATA/aitk_db.db" && -f /ai-toolkit/aitk_db.db ]]; then
		cp --no-preserve=ownership /ai-toolkit/aitk_db.db "$DATA/aitk_db.db"
	fi
	rm -f /ai-toolkit/aitk_db.db
	ln -s "$DATA/aitk_db.db" /ai-toolkit/aitk_db.db

	rm -f /workspace/ai-toolkit
	ln -s /ai-toolkit /workspace/ai-toolkit
fi

# Ensure we have /workspace/training_sets in all scenarios
mkdir -p /workspace/training_set
mkdir -p /workspace/LoRas

# when trained using the UI, the result is stored in /workspace/ai-toolkit/output
ln -sfn /workspace/ai-toolkit/output /workspace/ComfyUI/models/loras/flux_train_ui

# when trained using the CLI, the result set is stored in /workspace/LoRas (don't put it in /workspace/ai-toolkit/output because it will create a symlink loop)
ln -sfn /workspace/LoRas /workspace/ComfyUI/models/loras/ai-toolkit
