FROM valyriantech/comfyui-without-flux:latest

# Due to the fact that the models are in a gated repository, we need to download them separately BEFORE building this image and store them locally in a folder called flux
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.sft
COPY flux/ae.sft /ComfyUI/models/vae/
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/flux1-dev.sft
COPY flux/flux1-dev.sft /ComfyUI/models/diffusion_models/

# Download and move clip_l.safetensors
RUN wget -O /ComfyUI/models/clip/clip_l.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true" --progress=bar:force:noscroll

# Download and move t5xxl_fp8_e4m3fn.safetensors
RUN wget -O /ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true" --progress=bar:force:noscroll

# Download LoRas
RUN wget -O /ComfyUI/models/loras/GracePenelopeTargaryenV4.safetensors "https://huggingface.co/WouterGlorieux/GracePenelopeTargaryenV4/resolve/main/GracePenelopeTargaryenV4.safetensors?download=true" --progress=bar:force:noscroll
RUN wget -O /ComfyUI/models/loras/VideoAditor_flux_realism_lora.safetensors "https://huggingface.co/VideoAditor/Flux-Lora-Realism/resolve/main/flux_realism_lora.safetensors?download=true" --progress=bar:force:noscroll

# make the xlabs directory
RUN mkdir -p /ComfyUI/models/xlabs/loras
RUN wget -O /ComfyUI/models/xlabs/loras/Xlabs-AI_flux-RealismLora.safetensors "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors?download=true" --progress=bar:force:noscroll

CMD [ "/start.sh" ]
