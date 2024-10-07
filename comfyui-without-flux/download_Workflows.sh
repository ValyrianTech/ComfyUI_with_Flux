#!/bin/bash

# The URL of the github repo
repo_url="https://raw.githubusercontent.com/ValyrianTech/ComfyUI_with_Flux/main/comfyui-without-flux/workflows"

# The local directory to store the files
local_dir="/workspace/ComfyUI/pysssss-workflows"

# List of file names
file_list=("AdvancedLivePortrait.json" "AdvancedLivePortrait_with_ExpressionEditor.json" "Controlnet.json" "ExpressionEditor.json" "FaceSwap.json" "img2img.json" "Inpainting.json" "LoRa.json" "Outpainting.json" "txt2img.json" "Upscale_LDSR.json" "Upscale_SUPIR.json" "Xlabs-AI_RealismLoRa.json")

# Change to the local directory
cd $local_dir

# Loop over the list of files
for file in "${file_list[@]}"
do
    # If the file does not exist
    if [ ! -f $file ]; then
        # Download the file
        echo "Downloading $file..."
        curl -O $repo_url/$file
    else
        echo "$file already exists."
    fi
done
