#!/bin/bash

# The URL of the github repo
repo_url="https://raw.githubusercontent.com/ValyrianTech/ComfyUI_with_Flux/main/comfyui-without-flux/workflows"

# The local directory to store the files
local_dir="/workspace/ComfyUI/user/default/workflows"

# List of file names
file_list=(
  "AdvancedLivePortrait.json"
  "AdvancedLivePortrait_with_ExpressionEditor.json"
  "CogVideoX_img2vid.json"
  "CogVideoX_txt2vid.json"
  "Controlnet.json"
  "Controlnet2img.json"
  "EditImage_flux-kontext-dev.json"
  "ExpressionEditor.json"
  "Facedetailer.json"
  "FaceSwap.json"
  "Flux2_ImageEdit.json"
  "Flux2_Text2Image.json"
  "img2img.json"
  "img2pose.json"
  "Inpainting.json"
  "LoRa.json"
  "Outpainting.json"
  "pose2img.json"
  "qwen_image_edit_bf16.json"
  "qwen_image_edit_fp8.json"
  "qwen_image_edit_plus.json"
  "txt2img.json"
  "Upscale_LDSR.json"
  "Upscale_SUPIR.json"
  "VibeVoice_multiple_speaker.json"
  "VibeVoice_single_speaker.json"
  "wan2.1_Image2Video.json"
  "wan2.1_Text2Video.json"
  "wan2.2_Image2Video.json"
  "wan2.1_infinite-talk.json"
  "wan2.2_Text2Video.json"
  "Xlabs-AI_RealismLoRa.json"
  )

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
