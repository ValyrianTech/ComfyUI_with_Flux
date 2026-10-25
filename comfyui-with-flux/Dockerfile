FROM valyriantech/comfyui-without-flux:latest

# Only the gated Flux files are baked into this image. Every byte in the image is pulled and
# unpacked by RunPod and then copied to the network volume on first boot, so the public companion
# models (text encoders, LoRAs, openpose annotators) are downloaded straight to the volume by
# /download_flux_extras.sh on first boot instead (see start.sh). The ReActor face-restore models
# are downloaded automatically by the node on first use.
#
# Due to the fact that the models are in a gated repository, we need to download them separately BEFORE building this image and store them locally in a folder called flux
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.sft
COPY --chmod=666 flux/ae.sft /ComfyUI/models/vae/
# https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/flux1-dev.sft
COPY --chmod=666 flux/flux1-dev.sft /ComfyUI/models/diffusion_models/

CMD [ "/start.sh" ]
