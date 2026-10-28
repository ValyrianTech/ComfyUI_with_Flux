#!/bin/bash
# Downloads the public companion models for Flux (text encoders, example LoRAs and the openpose
# annotators), which the with-flux image has baked in. Runs in the background on pod start when
# DOWNLOAD_FLUX=true, once the Flux model is present (see download_selected.sh); files that already exist are skipped. Downloads are atomic and parallel
# (see download_lib.sh).

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

ANNOTATORS="/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators"

download_file "/ComfyUI/models/clip"        "clip_l.safetensors"                        "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true"
download_file "/ComfyUI/models/clip"        "t5xxl_fp8_e4m3fn.safetensors"              "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true"
download_file "/ComfyUI/models/loras"       "GracePenelopeTargaryenV5.safetensors"      "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryenV5/resolve/main/GracePenelopeTargaryenV5.safetensors?download=true"
download_file "/ComfyUI/models/loras"       "VideoAditor_flux_realism_lora.safetensors" "https://huggingface.co/VideoAditor/Flux-Lora-Realism/resolve/main/flux_realism_lora.safetensors?download=true"
download_file "/ComfyUI/models/xlabs/loras" "Xlabs-AI_flux-RealismLora.safetensors"     "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors?download=true"
download_file "$ANNOTATORS"                 "body_pose_model.pth"                       "https://huggingface.co/lllyasviel/Annotators/resolve/main/body_pose_model.pth?download=true"
download_file "$ANNOTATORS"                 "hand_pose_model.pth"                       "https://huggingface.co/lllyasviel/Annotators/resolve/main/hand_pose_model.pth?download=true"
download_file "$ANNOTATORS"                 "facenet.pth"                               "https://huggingface.co/lllyasviel/Annotators/resolve/main/facenet.pth?download=true"

download_wait
echo "Flux companion model downloads done."
