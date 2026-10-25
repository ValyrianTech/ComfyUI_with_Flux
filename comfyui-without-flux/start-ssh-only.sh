#!/bin/bash

echo "pod started"

# Everything started from here (ComfyUI, JupyterLab, AI-Toolkit, model downloads) creates
# world-writable files and folders, so nothing ends up locked to one user
umask 000

# Start JupyterLab first: it doesn't depend on the volume layout or the models, so it is usable
# right away, e.g. to download LoRAs with civitai-download while the models are still downloading.
# Its URL on the RunPod proxy is public, so set JUPYTER_PASSWORD to protect it; it is used as the
# login token. Left empty, JupyterLab opens without any login.
if [[ -n "${JUPYTER_PASSWORD}" ]]; then
    JUPYTER_TOKEN="${JUPYTER_PASSWORD}" jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.allow_origin='*' &
    echo "JupyterLab started (login with JUPYTER_PASSWORD)"
else
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.allow_origin='*' --ServerApp.token='' --ServerApp.password='' &
    echo "JupyterLab started without a login (JUPYTER_PASSWORD is not set)"
fi

if [[ $PUBLIC_KEY ]]
then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    cd ~/.ssh
    echo $PUBLIC_KEY >> authorized_keys
    chmod 700 -R ~/.ssh
    cd /
    service ssh start
fi

# Start nginx as reverse proxy to enable api access
service nginx start

# Example notebook for downloading models from CivitAI (civitai-download is installed in the image)
mkdir -p /workspace/civitai
[ -f /workspace/civitai/civitai_downloader.ipynb ] || cp /civitai_downloader.ipynb /workspace/civitai/

# Keep ComfyUI's models, input, output, user folder and user-installed custom nodes on the volume
/comfyui-on-workspace.sh

# Move ai-toolkit's folder to $VOLUME so models and all config will persist
/ai-toolkit-on-workspace.sh

# Open up permissions on files already on the volume (from older images or other tools).
# Runs in the background because it can take a while on a large volume.
nice chmod -R a+rwX /workspace 2>/dev/null &

#!/bin/bash
if [[ -z "${HF_TOKEN}" ]] || [[ "${HF_TOKEN}" == "enter_your_huggingface_token_here" ]]
then
    echo "HF_TOKEN is not set"
else
    echo "HF_TOKEN is set, logging in..."
    hf auth login --token ${HF_TOKEN}
fi

# Start AI-Toolkit UI in the background (prebuilt artifacts preferred)
if [ -d "/workspace/ai-toolkit/ui" ]; then
    echo "Starting AI-Toolkit UI in background on port 8675"
    cd /workspace/ai-toolkit/ui
    if [ -d .next ] && { [ -f dist/cron/worker.js ] || [ -f dist/worker.js ]; }; then
        echo "Prebuilt artifacts found. Running: npm run start"
        nohup npm run start > /workspace/ai-toolkit/ui/server.log 2>&1 &
    else
        echo "Prebuilt artifacts not found. Falling back to: npm run build_and_start (this may take a while)"
        nohup npm run build_and_start > /workspace/ai-toolkit/ui/server.log 2>&1 &
    fi
    cd - >/dev/null 2>&1 || true
else
    echo "AI-Toolkit UI directory not found at /workspace/ai-toolkit/ui; skipping UI startup"
fi

# Fetch the selected model sets (by default Flux and what its workflows need, see
# /download_selected.sh for the DOWNLOAD_* options) straight to the volume, in the background.
# Already-present files are skipped and every file appears atomically when complete.
# /download_selected.sh creates $FLUX_READY_FILE once the Flux set (Flux, its VAE and the clip_l and
# t5xxl text encoders) is done, so ComfyUI can wait for it below.
export FLUX_READY_FILE=/tmp/flux-models-ready
rm -f "$FLUX_READY_FILE"
echo "Starting background model downloads (log: /workspace/model_downloads.log)"
/download_selected.sh > /workspace/model_downloads.log 2>&1 &
DOWNLOAD_PID=$!

# Check if the flux model is present
bash /check_files.sh

# Check if there is a venv directory, if so, activate it
if [ -d "/workspace/venv" ]; then
    echo "venv directory found, activating it"
    source /workspace/venv/bin/activate
fi

# Install the requirements of custom nodes you installed yourself (they live on the volume)
bash /install_user_custom_nodes.sh

# Check if user's script exists in /workspace
if [ ! -f /workspace/start_user.sh ]; then
    # If not, copy the original script to /workspace
    cp /start-original.sh /workspace/start_user.sh
else
    # Volumes from older images still call the removed Mixlab script
    sed -i '/disable_mixlab.sh/d' /workspace/start_user.sh
fi

# Flux workflows can't run without the Flux model and its text encoders, so ComfyUI waits for them
# (COMFYUI_WAIT_FOR_FLUX=false starts it right away). The other model sets keep downloading in the
# background. If the downloads stop without finishing the Flux set, ComfyUI starts anyway.
if [[ ! "${COMFYUI_WAIT_FOR_FLUX,,}" =~ ^(false|0|no|off)$ ]] && [ ! -e "$FLUX_READY_FILE" ]; then
    echo "Waiting for Flux and its text encoders to download before starting ComfyUI (log: /workspace/model_downloads.log)"
    while [ ! -e "$FLUX_READY_FILE" ] && kill -0 "$DOWNLOAD_PID" 2>/dev/null; do
        sleep 2
    done
    echo "Flux models are ready"
fi

# Execute the user's script
bash /workspace/start_user.sh

sleep infinity
