#!/bin/bash

FILE="/workspace/ComfyUI/models/diffusion_models/flux1-dev.sft"

if [ ! -f "$FILE" ]; then
    echo "#################################################################"
    echo "WARNING!"
    echo "#################################################################"
    echo "File $FILE does not exist."
    echo "Some of the required files, like the flux.1 model, are not present."
    echo ""
    echo "This docker image is intended to be used in combination with a network volume that has been initialized with the 'ComfyUI WITH Flux' template first."
    echo "The 'ComfyUI WITHOUT Flux' container and 'ComfyUI WITH Flux' containers are identical, except that the 'ComfyUI WITHOUT Flux' container does not include about 20GB of model files."
    echo "Please use the 'ComfyUI WITH Flux' template first with a new and empty network volume, this will copy all the files to the network volume so that you don't need to download them again each time you deploy a new pod."
    echo ""
    echo "Alternatively, you can download the files manually like this:"
    echo "When deploying the pod, set an environment variable HF_TOKEN with your Hugging Face token."
    echo "Make sure to check the 'Read access to contents of all public gated repos you can access' permission when creating the token."
    echo "Go to https://huggingface.co/black-forest-labs/FLUX.1-dev and click the button to request access."
    echo "Then run the following command: bash /download_Files.sh in the terminal."
    echo ""
    echo "#################################################################"
fi
