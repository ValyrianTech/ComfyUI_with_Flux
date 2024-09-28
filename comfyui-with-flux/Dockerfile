FROM valyriantech/comfyui-without-flux:latest

# Due to the fact that the models are in a gated repository, we need to download them separately BEFORE building this image and store them locally in a folder called flux
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.sft
COPY flux/ae.sft /ComfyUI/models/vae/
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/flux1-dev.sft
COPY flux/flux1-dev.sft /ComfyUI/models/diffusion_models/

# Download and move clip_l.safetensors
RUN wget -O /ComfyUI/models/clip/clip_l.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true"

# Download and move t5xxl_fp8_e4m3fn.safetensors
RUN wget -O /ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true"

# Download LoRas
RUN wget -O /ComfyUI/models/loras/GracePenelopeTargaryenV1.safetensors "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryen/resolve/main/lora.safetensors?download=true"
RUN wget -O /ComfyUI/models/loras/GracePenelopeTargaryenV2.safetensors "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryenV2/resolve/main/lora.safetensors?download=true"
RUN wget -O /ComfyUI/models/loras/VideoAditor_flux_realism_lora.safetensors "https://huggingface.co/VideoAditor/Flux-Lora-Realism/resolve/main/flux_realism_lora.safetensors?download=true"

# make the xlabs directory
RUN mkdir -p /ComfyUI/models/xlabs/loras
RUN wget -O /ComfyUI/models/xlabs/loras/Xlabs-AI_flux-RealismLora.safetensors "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors?download=true"

CMD [ "/start.sh" ]
