#!/bin/bash
# Downloads the public models that used to be baked into the Docker image (SD 1.5, face swap and
# face detailer models). Off by default, enable with DOWNLOAD_BASE_MODELS=true (see download_selected.sh).
# Files that already exist are skipped.
# Downloads are atomic and parallel (see download_lib.sh).

source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/download_lib.sh"

download_file "/ComfyUI/models/checkpoints"      "v1-5-pruned-emaonly-fp16.safetensors" "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors?download=true"
download_file "/ComfyUI/models/insightface"      "inswapper_128.onnx"                   "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx?download=true"
download_file "/ComfyUI/models/ultralytics/bbox" "face_yolov8m.pt"                      "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt?download=true"

download_wait
echo "Base model downloads done."
