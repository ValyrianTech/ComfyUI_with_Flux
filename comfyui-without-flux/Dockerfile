ARG DOCKER_FROM=nvidia/cuda:12.8.0-runtime-ubuntu22.04

###############################
# Builder stage
###############################
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04 AS builder

# Install Python, git, and build dependencies for compiling wheels
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv python-is-python3 git git-lfs wget zip unzip curl \
        build-essential pkg-config libcairo2-dev libsqlite3-dev && \
    python3 -m pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js 22 LTS for AI-Toolkit build-time needs
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get update -y && apt-get install -y nodejs && \
    npm -v && node -v && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for all Python deps
ENV VENV_PATH=/opt/venv
RUN python3 -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"

# Install PyTorch with CUDA 12.8 in the venv
RUN pip install --no-cache-dir -U torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 \
    --index-url https://download.pytorch.org/whl/cu128

# Clone ComfyUI and base requirements
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /ComfyUI && \
    pip install --no-cache-dir -r /ComfyUI/requirements.txt && \
    mkdir -p /ComfyUI/pysssss-workflows

# JupyterLab (preserve original behavior)
RUN pip install --no-cache-dir jupyterlab

# Upgrade albumentations to latest to avoid update warnings at runtime
RUN pip install --no-cache-dir -U albumentations

# Pre-clone essential custom nodes and install their requirements
RUN set -eux; cd /ComfyUI/custom_nodes; \
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git; \
    git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git; \
    git clone https://github.com/XLabs-AI/x-flux-comfyui.git; \
    python /ComfyUI/custom_nodes/x-flux-comfyui/setup.py; \
    git clone https://github.com/flowtyone/ComfyUI-Flowty-LDSR.git; \
    pip install --no-cache-dir -r ComfyUI-Flowty-LDSR/requirements.txt; \
    git clone https://github.com/kijai/ComfyUI-SUPIR.git; \
    pip install --no-cache-dir -r ComfyUI-SUPIR/requirements.txt; \
    git clone https://github.com/kijai/ComfyUI-KJNodes.git; \
    pip install --no-cache-dir -r ComfyUI-KJNodes/requirements.txt; \
    git clone https://github.com/rgthree/rgthree-comfy.git; \
    pip install --no-cache-dir -r rgthree-comfy/requirements.txt; \
    git clone https://github.com/JPS-GER/ComfyUI_JPS-Nodes.git; \
    git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git; \
    git clone https://github.com/Jordach/comfy-plasma.git; \
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git; \
    pip install --no-cache-dir -r ComfyUI-VideoHelperSuite/requirements.txt; \
    git clone https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait.git; \
    pip install --no-cache-dir -r ComfyUI-AdvancedLivePortrait/requirements.txt; \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git; \
    pip install --no-cache-dir -r ComfyUI-Impact-Pack/requirements.txt; \
    python /ComfyUI/custom_nodes/ComfyUI-Impact-Pack/install.py; \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack; \
    pip install --no-cache-dir -r ComfyUI-Impact-Subpack/requirements.txt; \
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git; \
    pip install --no-cache-dir -r comfyui_controlnet_aux/requirements.txt; \
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale --recursive; \
    git clone https://github.com/yolain/ComfyUI-Easy-Use.git; \
    pip install --no-cache-dir -r ComfyUI-Easy-Use/requirements.txt; \
    git clone https://github.com/kijai/ComfyUI-Florence2.git; \
    pip install --no-cache-dir -r ComfyUI-Florence2/requirements.txt; \
    mkdir -p /ComfyUI/models/LLM; \
    git clone https://github.com/WASasquatch/was-node-suite-comfyui.git; \
    pip install --no-cache-dir -r was-node-suite-comfyui/requirements.txt; \
    git clone https://github.com/theUpsider/ComfyUI-Logic.git; \
    git clone https://github.com/cubiq/ComfyUI_essentials.git; \
    pip install --no-cache-dir -r ComfyUI_essentials/requirements.txt; \
    git clone https://github.com/chrisgoringe/cg-image-picker.git; \
    git clone https://github.com/chflame163/ComfyUI_LayerStyle.git; \
    pip install --no-cache-dir -r ComfyUI_LayerStyle/requirements.txt; \
    git clone https://github.com/shadowcz007/comfyui-mixlab-nodes.git; \
    pip install --no-cache-dir -r comfyui-mixlab-nodes/requirements.txt; \
    git clone https://codeberg.org/Gourieff/comfyui-reactor-node.git; \
    pip install --no-cache-dir -r comfyui-reactor-node/requirements.txt; \
    git clone https://github.com/chrisgoringe/cg-use-everywhere.git; \
    git clone https://github.com/kijai/ComfyUI-CogVideoXWrapper.git; \
    pip install --no-cache-dir -r ComfyUI-CogVideoXWrapper/requirements.txt; \
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git; \
    pip install --no-cache-dir -r ComfyUI-WanVideoWrapper/requirements.txt; \
    pip install --no-cache-dir sageattention==1.0.6; \
    git clone https://github.com/kijai/ComfyUI-MelBandRoFormer.git; \
    pip install --no-cache-dir -r ComfyUI-MelBandRoFormer/requirements.txt; \
    git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git; \
    python /ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/install.py; \
    git clone https://github.com/Enemyx-net/VibeVoice-ComfyUI.git; \
    pip install --no-cache-dir -r VibeVoice-ComfyUI/requirements.txt && \
    mkdir -p /ComfyUI/models/vibevoice/vvembed; \
    git clone https://github.com/kijai/ComfyUI-segment-anything-2.git; \
    git clone https://github.com/GACLove/ComfyUI-VFI.git; \
    pip install --no-cache-dir -r ComfyUI-VFI/requirements.txt

# Clone and install AI-Toolkit
RUN git clone https://github.com/ostris/ai-toolkit.git /ai-toolkit && \
    cd /ai-toolkit && git submodule update --init --recursive && \
    pip install --no-cache-dir -r requirements.txt

# Prebuild AI-Toolkit UI (install deps, init DB, and build)
RUN set -eux; cd /ai-toolkit/ui; \
    npm ci || npm install; \
    npm run update_db; \
    npm run build

# Prune git histories to reduce copy size
RUN find /ComfyUI -name .git -type d -prune -exec rm -rf {} + && \
    find /ai-toolkit -name .git -type d -prune -exec rm -rf {} +

###############################
# Runtime stage
###############################
FROM ${DOCKER_FROM} AS runtime

# Install Python and only runtime OS packages
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv python-is-python3 \
        openssh-server openssh-client git git-lfs wget zip unzip curl vim \
        nginx libgl1-mesa-glx libglib2.0-0 libsqlite3-0 && \
    python3 -m pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js 22 LTS for AI-Toolkit runtime needs
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get update -y && apt-get install -y nodejs && \
    npm -v && node -v && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager) for ComfyUI-Manager compatibility
RUN curl -fsSL https://astral.sh/uv/install.sh | sh && \
    if [ -f "/root/.local/bin/uv" ]; then ln -sf /root/.local/bin/uv /usr/local/bin/uv; fi && \
    if [ -f "/root/.cargo/bin/uv" ]; then ln -sf /root/.cargo/bin/uv /usr/local/bin/uv; fi && \
    uv --version || true

# Nginx config
COPY default /etc/nginx/sites-available/default

# CUDA path and ensure venv binaries are preferred
ENV PATH="/opt/venv/bin:/usr/local/cuda/bin:${PATH}"

# Copy application tree and Python environment from builder
COPY --from=builder /ComfyUI /ComfyUI
COPY --from=builder /ai-toolkit /ai-toolkit
COPY --from=builder /opt/venv /opt/venv

# Startup and helper scripts
COPY --chmod=755 start-ssh-only.sh /start.sh
COPY --chmod=755 start-original.sh /start-original.sh
COPY --chmod=755 comfyui-on-workspace.sh /comfyui-on-workspace.sh
COPY --chmod=755 ai-toolkit-on-workspace.sh /ai-toolkit-on-workspace.sh
COPY --chmod=755 check_files.sh /check_files.sh

# App configuration and assets
COPY --chmod=644 workflows/ /ComfyUI/user/default/workflows/
COPY --chmod=644 comfy.settings.json /ComfyUI/user/default/comfy.settings.json
COPY --chmod=644 character_sheet_example.png /ComfyUI/input/character_sheet_example.png
COPY --chmod=644 example_photo.png /ComfyUI/input/example_photo.png
COPY --chmod=644 example_photo_small.png /ComfyUI/input/example_photo_small.png
COPY --chmod=644 example_pose.png /ComfyUI/input/example_pose.png
COPY --chmod=644 example2.png /ComfyUI/input/example2.png
COPY --chmod=644 driving_video.mp4 /ComfyUI/input/driving_video.mp4
COPY --chmod=644 GracePenelopeTargaryen.mp3 /ComfyUI/input/GracePenelopeTargaryen.mp3
COPY --chmod=644 Male-MiddleAged_American.mp3 /ComfyUI/input/Male-MiddleAged_American.mp3

WORKDIR /workspace

# Service ports
EXPOSE 8188
EXPOSE 8888
EXPOSE 7860
EXPOSE 8675

# Downloads and runtime-only adjustments
RUN wget "https://github.com/comfyanonymous/ComfyUI_examples/blob/master/flux/flux_dev_example.png" -P /ComfyUI

 

# Default graph handling
COPY --chmod=644 defaultGraph.json /defaultGraph.json
COPY --chmod=755 replaceDefaultGraph.py /replaceDefaultGraph.py
RUN python3 /replaceDefaultGraph.py
COPY --chmod=644 defaultGraph.json /ComfyUI/web/templates/default.json

# Download scripts for additional models
COPY --chmod=755 download_Controlnet.sh /download_Controlnet.sh
COPY --chmod=755 download_fp16.sh /download_fp16.sh
COPY --chmod=755 download_LDSR.sh /download_LDSR.sh
COPY --chmod=755 download_SUPIR.sh /download_SUPIR.sh
COPY --chmod=755 download_Florence-2.sh /download_Florence-2.sh
COPY --chmod=755 download_Upscalers.sh /download_Upscalers.sh
COPY --chmod=755 download_Outpainting.sh /download_Outpainting.sh
COPY --chmod=755 download_Workflows.sh /download_Workflows.sh
COPY --chmod=755 update_Workflows.sh /update_Workflows.sh
COPY --chmod=755 download_ALL.sh /download_ALL.sh
COPY --chmod=755 make_venv.sh /make_venv.sh
COPY --chmod=755 download_Files.sh /download_Files.sh
COPY --chmod=755 download_Flux2.sh /download_Flux2.sh
COPY --chmod=755 download_wan2.1.sh /download_wan2.1.sh
COPY --chmod=755 download_wan2.2.sh /download_wan2.2.sh
COPY --chmod=755 download_wan2.1_InfiniteTalk.sh /download_wan2.1_InfiniteTalk.sh
COPY --chmod=755 download_Qwen_bf16.sh /download_Qwen_bf16.sh
COPY --chmod=755 download_Qwen_fp8.sh /download_Qwen_fp8.sh
COPY --chmod=755 download_VibeVoice.sh /download_VibeVoice.sh
COPY --chmod=755 disable_mixlab.sh /disable_mixlab.sh

# Runtime model downloads (keep large assets out of builder to avoid duplication)
RUN mkdir -p /ComfyUI/models/ultralytics/bbox && \
    wget "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt?download=true" -O /ComfyUI/models/ultralytics/bbox/face_yolov8m.pt

RUN mkdir -p /ComfyUI/models/insightface && \
    wget "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx?download=true" -O /ComfyUI/models/insightface/inswapper_128.onnx

# VibeVoice note: to pin transformers if needed, uncomment below line
# RUN pip install transformers==4.49.0

# Tutorial workflow model
RUN mkdir -p /ComfyUI/models/checkpoints && \
    wget "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors?download=true" -O /ComfyUI/models/checkpoints/v1-5-pruned-emaonly-fp16.safetensors

# AI-Toolkit default config and utility
COPY --chmod=644 ai-toolkit/train_lora.yaml /ai-toolkit/config/train_lora.yaml
COPY --chmod=755 ai-toolkit/caption_images.py /caption_images.py

CMD [ "/start.sh" ]
