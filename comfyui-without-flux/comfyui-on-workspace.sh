#!/bin/bash

# ComfyUI's code, the custom nodes that ship with the image and the Python venv stay inside the
# image, where they are fast to start and are updated with every new image. Only the user's data
# is persisted on the network volume:
#   /workspace/comfyui-data/models         models (the download scripts write here too)
#   /workspace/comfyui-data/input          ComfyUI input folder
#   /workspace/comfyui-data/output         ComfyUI output folder
#   /workspace/comfyui-data/user           workflows, settings, ComfyUI-Manager config
#   /workspace/comfyui-data/custom_nodes   custom nodes you install yourself
# The first four are symlinked into /ComfyUI; the custom_nodes folder is loaded through
# /ComfyUI/extra_model_paths.yaml. /workspace/ComfyUI is a symlink to /ComfyUI so all documented
# paths keep working.

# Ensure we have /workspace in all scenarios
mkdir -p /workspace

DATA=/workspace/comfyui-data
OLD=/workspace/ComfyUI

mkdir -p "$DATA/custom_nodes"

if [[ -d "$OLD" && ! -L "$OLD" ]]; then
	# Volume initialized by an older image that copied the whole ComfyUI tree to /workspace.
	# Move the user's data out of it (a rename on the same volume, so it is instant), then put the
	# leftover code aside instead of deleting it.
	echo "Migrating $OLD to the new volume layout in $DATA"
	for item in models input output user; do
		if [[ -e "$OLD/$item" && ! -e "$DATA/$item" ]]; then
			mv "$OLD/$item" "$DATA/$item"
		fi
	done
	# Custom nodes the user installed (anything the image doesn't ship) go to the user folder
	if [[ -d "$OLD/custom_nodes" ]]; then
		for node in "$OLD"/custom_nodes/*; do
			name=$(basename "$node")
			[[ -e "$node" ]] || continue
			[[ "$name" == "__pycache__" ]] && continue
			[[ -e "/ComfyUI/custom_nodes/$name" || -e "$DATA/custom_nodes/$name" ]] && continue
			echo "Keeping user custom node $name"
			mv "$node" "$DATA/custom_nodes/$name"
		done
	fi
	backup=/workspace/ComfyUI.old
	[[ -e "$backup" ]] && backup="/workspace/ComfyUI.old.$(date +%Y%m%d%H%M%S)"
	mv "$OLD" "$backup"
	echo "The rest of the old copy was moved to $backup. Check it for anything you still need, then delete it to free up space."
fi

# Link a folder of the image into the volume. Files the image ships (default workflows, example
# inputs) are copied to the volume when they are missing
# there; files already on the volume are never overwritten. Each file is copied to a temporary
# name first, so an interrupted copy is redone on the next start.
link_to_volume() {
	local src=/ComfyUI/$1
	local dst=$DATA/$1
	local path

	mkdir -p "$dst"
	if [[ -d "$src" && ! -L "$src" ]]; then
		(cd "$src" && find . -mindepth 1 -type d) | while IFS= read -r path; do
			mkdir -p "$dst/$path"
		done
		(cd "$src" && find . \( -type f -o -type l \)) | while IFS= read -r path; do
			if [[ ! -e "$dst/$path" && ! -L "$dst/$path" ]]; then
				echo "Copying $1/${path#./} to the volume"
				cp -P --no-preserve=ownership "$src/$path" "$dst/$path.part" && mv "$dst/$path.part" "$dst/$path"
			fi
		done
		rm -rf "$src"
	fi
	ln -sfn "$dst" "$src"
}

for item in models input output user; do
	link_to_volume "$item"
done

# The models baked into the image (/opt/comfyui-models, e.g. Flux in the with-flux image) are linked
# onto the volume rather than copied: nothing to copy on the first start, no volume space used, and
# ComfyUI and every custom node find them in the usual folders. A file of the same name already on
# the volume wins. Links left by an image that had other models are removed, so no broken entries
# show up in ComfyUI.
# COPY_BAKED_MODELS=true copies them onto the volume instead (replacing the links), e.g. to set up a
# volume with the with-flux image that later pods use with the smaller without-flux image.
BAKED=/opt/comfyui-models
find "$DATA/models" -type l -lname "$BAKED/*" ! -exec test -e {} \; -delete 2>/dev/null
if [[ -d "$BAKED" ]]; then
	copy_baked=false
	[[ "${COPY_BAKED_MODELS,,}" =~ ^(true|1|yes|on)$ ]] && copy_baked=true
	(cd "$BAKED" && find . -type f) | while IFS= read -r path; do
		path=${path#./}
		dst=$DATA/models/$path
		if [[ -e "$dst" && ! -L "$dst" ]] || [[ -L "$dst" && "$(readlink "$dst")" != "$BAKED/$path" ]]; then
			continue
		fi
		mkdir -p "$(dirname "$dst")"
		if [[ "$copy_baked" == true ]]; then
			echo "Copying models/$path to the volume"
			cp --no-preserve=ownership "$BAKED/$path" "$dst.part" && mv -f "$dst.part" "$dst"
		elif [[ ! -L "$dst" ]]; then
			ln -s "$BAKED/$path" "$dst" && echo "Linked models/$path from the image"
		fi
	done
fi

# NFS network volumes enforce a directory's execute bit even for root, and older images left some
# directories without one (e.g. user/). Fix them now, before ComfyUI starts, rather than relying on
# the background chmod in start.sh.
find "$DATA" -type d ! -perm -0111 -exec chmod a+rwx {} + 2>/dev/null

# Keep /workspace/ComfyUI working for older scripts and start_user.sh files on the volume
if [[ -L "$OLD" || ! -e "$OLD" ]]; then
	ln -sfn /ComfyUI "$OLD"
fi
