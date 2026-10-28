FROM valyriantech/comfyui-without-flux:latest

# Models are baked into /opt/comfyui-models (same layout as ComfyUI's models folder), so this image
# works offline. comfyui-on-workspace.sh links them onto the network volume instead of copying them,
# so the first start doesn't spend time copying ~30 GB and the volume holds only your own models.

# Due to the fact that the models are in a gated repository, we need to download them separately BEFORE building this image and store them locally in a folder called flux
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.sft
COPY --chmod=644 flux/ae.sft /opt/comfyui-models/vae/
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/flux1-dev.sft
COPY --chmod=644 flux/flux1-dev.sft /opt/comfyui-models/diffusion_models/

# Text encoders and example LoRAs
RUN mkdir -p /opt/comfyui-models/clip /opt/comfyui-models/loras /opt/comfyui-models/xlabs/loras && \
    wget -q -O /opt/comfyui-models/clip/clip_l.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true" && \
    wget -q -O /opt/comfyui-models/clip/t5xxl_fp8_e4m3fn.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true" && \
    wget -q -O /opt/comfyui-models/loras/GracePenelopeTargaryenV5.safetensors "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryenV5/resolve/main/GracePenelopeTargaryenV5.safetensors?download=true" && \
    wget -q -O /opt/comfyui-models/loras/VideoAditor_flux_realism_lora.safetensors "https://huggingface.co/VideoAditor/Flux-Lora-Realism/resolve/main/flux_realism_lora.safetensors?download=true" && \
    wget -q -O /opt/comfyui-models/xlabs/loras/Xlabs-AI_flux-RealismLora.safetensors "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors?download=true"

# This step is optional, the reActor node will download these models automatically on first launch if they are not present
# To include then in the docker image we need to download them manually and copy them to a folder called facerestore_models
COPY facerestore_models /opt/comfyui-models/facerestore_models/

# The openpose annotators live with the custom node, which stays in the image
RUN mkdir -p /ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && \
    cd /ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && \
    wget -q "https://huggingface.co/lllyasviel/Annotators/resolve/main/body_pose_model.pth?download=true" -O body_pose_model.pth && \
    wget -q "https://huggingface.co/lllyasviel/Annotators/resolve/main/hand_pose_model.pth?download=true" -O hand_pose_model.pth && \
    wget -q "https://huggingface.co/lllyasviel/Annotators/resolve/main/facenet.pth?download=true" -O facenet.pth && \
    rm -f /opt/comfyui-models/facerestore_models/.gitkeep && chmod -R a+rX /opt/comfyui-models

CMD [ "/start.sh" ]
