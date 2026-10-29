#!/bin/bash

FILE="/workspace/ComfyUI/models/diffusion_models/flux1-dev.sft"

if [ ! -f "$FILE" ] && [[ "${DOWNLOAD_FLUX,,}" =~ ^(false|0|no|off)$ ]]; then
    echo "Flux is not downloaded (DOWNLOAD_FLUX=false)"
elif [ ! -f "$FILE" ] && [[ "${DOWNLOAD_FLUX,,}" =~ ^(true|1|yes|on)$ ]] && [[ -n "${HF_TOKEN}" ]] && [[ "${HF_TOKEN}" != "enter_your_huggingface_token_here" ]]; then
    echo "Flux is being downloaded, ComfyUI starts once it is done (log: /workspace/model_downloads.log)"
elif [ ! -f "$FILE" ]; then
    echo "#################################################################"
    echo "WARNING!"
    echo "#################################################################"
    echo "File $FILE does not exist."
    echo "Some of the required files, like the flux.1 model, are not present."
    echo ""
    echo "This docker image is intended to be used in combination with a network volume that has been initialized with the 'ComfyUI WITH Flux' template first."
    echo "The 'ComfyUI WITHOUT Flux' container and 'ComfyUI WITH Flux' containers are identical, except that the 'ComfyUI WITHOUT Flux' container does not include about 20GB of model files."
    echo "Please use the 'ComfyUI WITH Flux' template first with a new and empty network volume and the environment variable COPY_BAKED_MODELS=true, this will copy all the files to the network volume so that you don't need to download them again each time you deploy a new pod."
    echo ""
    echo "Alternatively, you can download the files manually like this:"
    echo "When deploying the pod, set an environment variable HF_TOKEN with your Hugging Face token."
    echo "Make sure to check the 'Read access to contents of all public gated repos you can access' permission when creating the token."
    echo "Go to https://huggingface.co/black-forest-labs/FLUX.1-dev and click the button to request access."
    echo "Then set DOWNLOAD_FLUX=true when deploying the pod, or run the following command: bash /download_Files.sh in the terminal."
    echo ""
    echo "#################################################################"
fi
