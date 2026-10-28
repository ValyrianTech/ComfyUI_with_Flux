# Runtime base: "base" (cudart + compat only). The torch wheels in /opt/venv bundle cuBLAS, cuDNN
# etc., so the 2 GB "runtime" cuda-libraries layer is not needed and only slows down image pulls.
ARG DOCKER_FROM=nvidia/cuda:12.8.0-base-ubuntu22.04

###############################
# AI-Toolkit UI stage
###############################
# The UI only needs Node.js, so it is built in its own stage, which BuildKit runs at the same
# time as the much longer Python builder stage. It is built on the runtime base image so the
# natively compiled modules match the runtime's glibc.
FROM ${DOCKER_FROM} AS aitk-ui

RUN apt-get update -y && \
    apt-get install -y git curl ca-certificates openssl python3 build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm -v && node -v && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/ostris/ai-toolkit.git /ai-toolkit && \
    cd /ai-toolkit && git submodule update --init --recursive --depth 1

# Prebuild AI-Toolkit UI (install deps, init DB, and build)
# The sqlite3 npm package ships a prebuilt binary that needs glibc 2.38, but Ubuntu 22.04 has
# 2.35 ("GLIBC_2.38 not found" at build and at runtime), so compile it against this image's glibc.
RUN set -eux; cd /ai-toolkit/ui; \
    npm ci || npm install; \
    npm_config_build_from_source=true npm rebuild sqlite3; \
    npm run update_db; \
    npm run build

# Make everything users touch world-writable (dirs 777, files 666, executables stay executable) so
# JupyterLab, ComfyUI-Manager and AI-Toolkit never hit "permission denied". Done here in the builder
# because COPY --from keeps the modes, while a chmod -R in the runtime stage would duplicate every file.
RUN chmod -R a+rwX /ai-toolkit

###############################
# Builder stage
###############################
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04 AS builder

# Install Python, git, and build dependencies for compiling wheels
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv python-is-python3 git git-lfs wget zip unzip curl \
        build-essential pkg-config libcairo2-dev && \
    python3 -m pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for all Python deps
ENV VENV_PATH=/opt/venv
RUN python3 -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"

# uv installs packages with parallel downloads and is much faster than pip. Point it at the venv,
# and resolve across indexes the way pip does.
RUN pip install --no-cache-dir uv
ENV VIRTUAL_ENV=${VENV_PATH} UV_NO_CACHE=1 UV_INDEX_STRATEGY=unsafe-best-match

# Install PyTorch with CUDA 12.8 in the venv
RUN uv pip install -U torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 \
    --index-url https://download.pytorch.org/whl/cu128

# Clone ComfyUI and base requirements (shallow clones: git history only bloats the image)
RUN git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git /ComfyUI && \
    uv pip install -r /ComfyUI/requirements.txt && \
    mkdir -p /ComfyUI/pysssss-workflows

# JupyterLab (preserve original behavior)
RUN uv pip install jupyterlab

# Upgrade albumentations to latest to avoid update warnings at runtime
RUN uv pip install -U albumentations

# Pre-clone essential custom nodes (in parallel), then install their requirements in the original
# order so later nodes still override the pins of earlier ones
RUN set -eux; cd /ComfyUI/custom_nodes; \
    git clone --depth 1 --recursive --shallow-submodules https://github.com/ssitu/ComfyUI_UltimateSDUpscale & \
    printf '%s\n' \
        https://github.com/ltdrdata/ComfyUI-Manager.git \
        https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git \
        https://github.com/XLabs-AI/x-flux-comfyui.git \
        https://github.com/flowtyone/ComfyUI-Flowty-LDSR.git \
        https://github.com/kijai/ComfyUI-SUPIR.git \
        https://github.com/kijai/ComfyUI-KJNodes.git \
        https://github.com/rgthree/rgthree-comfy.git \
        https://github.com/JPS-GER/ComfyUI_JPS-Nodes.git \
        https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git \
        https://github.com/Jordach/comfy-plasma.git \
        https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git \
        https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait.git \
        https://github.com/ltdrdata/ComfyUI-Impact-Pack.git \
        https://github.com/ltdrdata/ComfyUI-Impact-Subpack \
        https://github.com/Fannovel16/comfyui_controlnet_aux.git \
        https://github.com/yolain/ComfyUI-Easy-Use.git \
        https://github.com/kijai/ComfyUI-Florence2.git \
        https://github.com/WASasquatch/was-node-suite-comfyui.git \
        https://github.com/theUpsider/ComfyUI-Logic.git \
        https://github.com/cubiq/ComfyUI_essentials.git \
        https://github.com/chrisgoringe/cg-image-picker.git \
        https://github.com/chflame163/ComfyUI_LayerStyle.git \
        https://codeberg.org/Gourieff/comfyui-reactor-node.git \
        https://github.com/chrisgoringe/cg-use-everywhere.git \
        https://github.com/kijai/ComfyUI-CogVideoXWrapper.git \
        https://github.com/kijai/ComfyUI-WanVideoWrapper.git \
        https://github.com/kijai/ComfyUI-MelBandRoFormer.git \
        https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git \
        https://github.com/Enemyx-net/VibeVoice-ComfyUI.git \
        https://github.com/kijai/ComfyUI-segment-anything-2.git \
        https://github.com/GACLove/ComfyUI-VFI.git \
        https://github.com/Lightricks/ComfyUI-LTXVideo.git \
        https://github.com/Fictiverse/ComfyUI_Fictiverse.git \
        https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git \
    | xargs -P 8 -n 1 git clone --depth 1; \
    wait; \
    python /ComfyUI/custom_nodes/x-flux-comfyui/setup.py; \
    uv pip install -r ComfyUI-Flowty-LDSR/requirements.txt; \
    uv pip install -r ComfyUI-SUPIR/requirements.txt; \
    uv pip install -r ComfyUI-KJNodes/requirements.txt; \
    uv pip install -r rgthree-comfy/requirements.txt; \
    uv pip install -r ComfyUI-VideoHelperSuite/requirements.txt; \
    uv pip install -r ComfyUI-AdvancedLivePortrait/requirements.txt; \
    uv pip install -r ComfyUI-Impact-Pack/requirements.txt; \
    python /ComfyUI/custom_nodes/ComfyUI-Impact-Pack/install.py; \
    uv pip install -r ComfyUI-Impact-Subpack/requirements.txt; \
    uv pip install -r comfyui_controlnet_aux/requirements.txt; \
    uv pip install -r ComfyUI-Easy-Use/requirements.txt; \
    uv pip install -r ComfyUI-Florence2/requirements.txt; \
    mkdir -p /ComfyUI/models/LLM; \
    uv pip install -r was-node-suite-comfyui/requirements.txt; \
    uv pip install -r ComfyUI_essentials/requirements.txt; \
    uv pip install -r ComfyUI_LayerStyle/requirements.txt; \
    uv pip install -r comfyui-reactor-node/requirements.txt; \
    uv pip install -r ComfyUI-CogVideoXWrapper/requirements.txt; \
    uv pip install -r ComfyUI-WanVideoWrapper/requirements.txt; \
    uv pip install sageattention==1.0.6; \
    uv pip install -r ComfyUI-MelBandRoFormer/requirements.txt; \
    python /ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/install.py; \
    uv pip install -r VibeVoice-ComfyUI/requirements.txt; \
    mkdir -p /ComfyUI/models/vibevoice/vvembed; \
    uv pip install -r ComfyUI-VFI/requirements.txt; \
    uv pip install -r ComfyUI-LTXVideo/requirements.txt; \
    uv pip install -r ComfyUI_Fictiverse/requirements.txt; \
    uv pip install -r ComfyUI-Inspire-Pack/requirements.txt

# Install AI-Toolkit's Python requirements (the code itself comes from the aitk-ui stage)
COPY --from=aitk-ui /ai-toolkit/requirements*.txt /tmp/ai-toolkit/
RUN uv pip install -r /tmp/ai-toolkit/requirements.txt && rm -rf /tmp/ai-toolkit

# Pin mediapipe/controlnet-aux to tested stable combo (fixes AI-Toolkit issues)
RUN uv pip uninstall mediapipe controlnet_aux && \
    uv pip install mediapipe==0.10.14 controlnet-aux==0.0.10

# mediapipe 0.10.14 keeps protobuf below 5, and onnx 1.18+ needs protobuf 5 (ReActor failed with "cannot import
# name 'runtime_version'"), so pin onnx. Some node requirements also pull the CPU onnxruntime, which shadows the
# GPU build and makes ReActor run on the CPU; keep only onnxruntime-gpu.
RUN uv pip install "onnx==1.17.0" && \
    (uv pip uninstall onnxruntime || true) && \
    uv pip install --reinstall onnxruntime-gpu

# AI-Toolkit pins av==16.0.1, but ComfyUI needs a newer PyAV (av>=17 for ColorPrimaries in
# av.video.reformatter) and fails to start without it. Both share /opt/venv, so restore
# ComfyUI's requirement after the AI-Toolkit install.
RUN uv pip install "$(grep -iE '^av([<>=~ ]|$)' /ComfyUI/requirements.txt)"

# AI-Toolkit pins scipy==1.12.0, which only works with NumPy 1.x, but the venv ends up with NumPy 2, so
# ComfyUI crashed on start (scipy.ndimage: "_ARRAY_API not found"). Install a SciPy (and CuPy, if a node
# pulled it in) built for NumPy 2, and fail the build if these imports break again.
RUN uv pip install "scipy>=1.15.3" && \
    { ! uv pip show cupy-cuda12x >/dev/null 2>&1 || uv pip install "cupy-cuda12x>=13.4"; } && \
    python -c "import numpy, scipy, scipy.ndimage, torch; print('numpy', numpy.__version__, 'scipy', scipy.__version__)"

# Same world-writable modes for the ComfyUI tree and the venv (see the aitk-ui stage)
RUN chmod -R a+rwX /ComfyUI /opt/venv

###############################
# Volume permissions shim stage
###############################
# Builds volume_perms_shim.c (see the runtime stage) on the same Ubuntu release, so it links
# against the runtime's glibc.
FROM ubuntu:22.04 AS perms-shim
RUN apt-get update -y && apt-get install -y gcc libc6-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY volume_perms_shim.c /tmp/volume_perms_shim.c
RUN gcc -O2 -Wall -shared -fPIC -o /volume_perms_shim.so /tmp/volume_perms_shim.c -ldl

###############################
# Runtime stage
###############################
FROM ${DOCKER_FROM} AS runtime

# Install Python and only runtime OS packages
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv python-is-python3 \
        openssh-server openssh-client git git-lfs wget zip unzip curl vim \
        nginx aria2 libgl1-mesa-glx libglib2.0-0 libsqlite3-0 \
        ffmpeg libavcodec-dev libavformat-dev libavutil-dev libswresample-dev && \
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

# Make JupyterLab terminals use bash (tab completion, arrow keys, history).
# Without SHELL set, jupyter_server_terminals falls back to /bin/sh, which is dash on Ubuntu.
ENV SHELL=/bin/bash

# Copy application tree and Python environment from builder
COPY --from=builder /ComfyUI /ComfyUI
COPY --from=aitk-ui /ai-toolkit /ai-toolkit
COPY --from=builder /opt/venv /opt/venv

# Startup and helper scripts
COPY --chmod=755 start-ssh-only.sh /start.sh
COPY --chmod=755 start-original.sh /start-original.sh
COPY --chmod=755 comfyui-on-workspace.sh /comfyui-on-workspace.sh
COPY --chmod=755 install_user_custom_nodes.sh /install_user_custom_nodes.sh
COPY --chmod=755 install_mixlab.sh /install_mixlab.sh
COPY --chmod=755 ai-toolkit-on-workspace.sh /ai-toolkit-on-workspace.sh
COPY --chmod=755 check_files.sh /check_files.sh
COPY --chmod=755 download_lib.sh /download_lib.sh
COPY --chmod=755 download_selected.sh /download_selected.sh
COPY --chmod=755 download_flux_extras.sh /download_flux_extras.sh
COPY --chmod=644 civitai_downloader.ipynb /civitai_downloader.ipynb

# JupyterLab: make folders named "checkpoints" (e.g. /ComfyUI/models/checkpoints) browsable.
# Jupyter Server routes ".../checkpoints" URLs to its notebook-checkpoint API, which hides such
# folders from the file browser. This small server extension routes existing folders normally.
COPY --chmod=644 jupyter_checkpoints_dir_fix.py /tmp/jupyter_checkpoints_dir_fix.py
RUN cp /tmp/jupyter_checkpoints_dir_fix.py "$(python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/" && \
    rm /tmp/jupyter_checkpoints_dir_fix.py && \
    mkdir -p /etc/jupyter/jupyter_server_config.d && \
    echo '{"ServerApp": {"jpserver_extensions": {"jupyter_checkpoints_dir_fix": true}}}' \
        > /etc/jupyter/jupyter_server_config.d/jupyter_checkpoints_dir_fix.json

# JupyterLab: default to the dark theme. overrides.json only changes the default, so users can
# still switch themes in Settings and their choice is kept in their own user settings.
RUN mkdir -p /opt/venv/share/jupyter/lab/settings && \
    echo '{"@jupyterlab/apputils-extension:themes": {"theme": "JupyterLab Dark"}}' \
        > /opt/venv/share/jupyter/lab/settings/overrides.json && \
    chmod -R a+rwX /opt/venv/share/jupyter/lab/settings

# App configuration and assets
# Loads the custom nodes you install yourself from the volume (see comfyui-on-workspace.sh)
COPY --chmod=644 extra_model_paths.yaml /ComfyUI/extra_model_paths.yaml
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
COPY --chmod=755 download_Kontext.sh /download_Kontext.sh
COPY --chmod=755 download_Flux2.sh /download_Flux2.sh
COPY --chmod=755 download_wan2.1.sh /download_wan2.1.sh
COPY --chmod=755 download_wan2.2.sh /download_wan2.2.sh
COPY --chmod=755 download_wan2.1_InfiniteTalk.sh /download_wan2.1_InfiniteTalk.sh
COPY --chmod=755 download_Qwen_bf16.sh /download_Qwen_bf16.sh
COPY --chmod=755 download_Qwen_fp8.sh /download_Qwen_fp8.sh
COPY --chmod=755 download_VibeVoice.sh /download_VibeVoice.sh
COPY --chmod=755 download_z-image.sh /download_z-image.sh
COPY --chmod=755 download_LTX2.sh /download_LTX2.sh
COPY --chmod=755 download_LTX2.3.sh /download_LTX2.3.sh

# Models the included workflows need are baked into the image, so it also works offline. They live in
# /opt/comfyui-models (same layout as ComfyUI's models folder) and are linked onto the volume by
# comfyui-on-workspace.sh instead of copied, so they cost no time or volume space on the first start.
RUN mkdir -p /ComfyUI/models/ultralytics/bbox /ComfyUI/models/insightface /ComfyUI/models/checkpoints && \
    mkdir -p /opt/comfyui-models/ultralytics/bbox /opt/comfyui-models/insightface /opt/comfyui-models/checkpoints && \
    wget -q "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt?download=true" -O /opt/comfyui-models/ultralytics/bbox/face_yolov8m.pt && \
    wget -q "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx?download=true" -O /opt/comfyui-models/insightface/inswapper_128.onnx && \
    wget -q "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors?download=true" -O /opt/comfyui-models/checkpoints/v1-5-pruned-emaonly-fp16.safetensors && \
    chmod -R a+rX /opt/comfyui-models

# VibeVoice note: to pin transformers if needed, uncomment below line
# RUN pip install transformers==4.49.0

# AI-Toolkit default config and utility
COPY --chmod=644 ai-toolkit/train_lora.yaml /ai-toolkit/config/train_lora.yaml
COPY --chmod=755 ai-toolkit/caption_images.py /caption_images.py

# COPY --chmod=644 also applies 644 to the directories it creates (no execute bit). Root gets
# past that on the image's overlay filesystem, but not on the NFS network volume. The folders that
# go to the volume are re-created there with open modes by comfyui-on-workspace.sh, which also
# fixes directories older images left on the volume; this keeps the copies in the image usable too.
RUN find /ComfyUI/user /ComfyUI/input /ComfyUI/web/templates /ai-toolkit/config -type d -exec chmod 777 {} +

# fix missing directory for old network volumes
RUN mkdir -p /opt/venv/lib/python3.10/site-packages/comfyui_workflow_templates/templates

# New files from interactive shells (JupyterLab terminals, SSH) are world-writable too
RUN echo "umask 000" >> /etc/bash.bashrc && echo "umask 000" >> /etc/profile

# Some /workspace volumes (NFS or FUSE) refuse chmod and chown even for root, which makes
# `git clone`/`git config` abort and cp -a, tar and rsync print errors there. The shim reports
# success for those calls on network filesystems only. It is off by default; start.sh preloads it
# into every process when ENABLE_VOLUME_PERMS_SHIM=true and it loads cleanly.
COPY --from=perms-shim /volume_perms_shim.so /usr/local/lib/volume_perms_shim.so

# Files on the volume can belong to another user (root squashed to nobody on NFS), which git
# refuses with "detected dubious ownership". Trust every repository.
RUN git config --system --add safe.directory '*'

CMD [ "/start.sh" ]
