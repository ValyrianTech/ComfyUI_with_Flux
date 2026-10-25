#!/bin/bash
# Downloads the model sets chosen with environment variables (set them in the RunPod template or
# when deploying the pod). start.sh runs this in the background on every pod start, and you can
# run it again by hand. All selected sets download at the same time; files that already exist
# are skipped, so only what is missing is fetched.
#
# Pick sets either one by one, e.g. DOWNLOAD_LTX23=true, or as a list:
#   DOWNLOAD_MODELS="wan2.2,ltx2.3"      (DOWNLOAD_MODELS=all selects every set)
# By default only Flux is downloaded (DOWNLOAD_FLUX=false turns it off), together with the models
# the Flux workflows need (text encoders, LoRAs, openpose annotators) once the Flux model is present
# (DOWNLOAD_FLUX_EXTRAS=false turns those off). Every other set is off unless selected.

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" || exit 1

# name           environment variable     script
SETS=(
    "base         DOWNLOAD_BASE_MODELS     download_base_models.sh"
    "flux         DOWNLOAD_FLUX            download_Files.sh"
    "flux2        DOWNLOAD_FLUX2           download_Flux2.sh"
    "wan2.1       DOWNLOAD_WAN             download_wan2.1.sh"
    "wan2.2       DOWNLOAD_WAN22           download_wan2.2.sh"
    "infinitetalk DOWNLOAD_INFINITETALK    download_wan2.1_InfiniteTalk.sh"
    "ltx2         DOWNLOAD_LTX2            download_LTX2.sh"
    "ltx2.3       DOWNLOAD_LTX23           download_LTX2.3.sh"
    "qwen_fp8     DOWNLOAD_QWEN_FP8        download_Qwen_fp8.sh"
    "qwen_bf16    DOWNLOAD_QWEN_BF16       download_Qwen_bf16.sh"
    "z-image      DOWNLOAD_Z_IMAGE         download_z-image.sh"
    "controlnet   DOWNLOAD_CONTROLNET      download_Controlnet.sh"
    "outpainting  DOWNLOAD_OUTPAINTING     download_Outpainting.sh"
    "supir        DOWNLOAD_SUPIR           download_SUPIR.sh"
    "ldsr         DOWNLOAD_LDSR            download_LDSR.sh"
    "upscalers    DOWNLOAD_UPSCALERS       download_Upscalers.sh"
    "florence2    DOWNLOAD_FLORENCE2       download_Florence-2.sh"
    "t5_fp16      DOWNLOAD_T5_FP16         download_fp16.sh"
    "vibevoice    DOWNLOAD_VIBEVOICE       download_VibeVoice.sh"
)

is_true() {
    [[ "${1,,}" =~ ^(true|1|yes|on)$ ]]
}

is_false() {
    [[ "${1,,}" =~ ^(false|0|no|off)$ ]]
}

in_list() {
    local list=",${DOWNLOAD_MODELS,,},"
    list=${list// /,}
    [[ "$list" == *",${1},"* || "$list" == *",all,"* ]]
}

selected() {
    local name=$1
    local var=$2
    local value=${!var}
    if [[ "$name" == "flux" ]]; then
        ! is_false "$value"
    else
        is_true "$value" || in_list "$name"
    fi
}

# start.sh passes FLUX_READY_FILE and starts ComfyUI once that file exists: right after the Flux set
# (Flux, its VAE and the text encoders) is done, or right away when Flux is not selected.
flux_ready() {
    [[ -n "${FLUX_READY_FILE}" ]] && touch "${FLUX_READY_FILE}"
}

selected flux DOWNLOAD_FLUX || flux_ready

for entry in "${SETS[@]}"; do
    read -r name var script <<< "$entry"
    if selected "$name" "$var"; then
        echo "Downloading model set '$name' ($script)"
        if [[ "$name" == "flux" ]]; then
            { ./"$script"; echo "Model set 'flux' done."; flux_ready; } &
        else
            ./"$script" &
        fi
    fi
done
wait

# The Flux companion models need the Flux model, which one of the sets above may just have fetched
if [ -f /ComfyUI/models/diffusion_models/flux1-dev.sft ] && ! is_false "${DOWNLOAD_FLUX_EXTRAS}"; then
    ./download_flux_extras.sh
fi
echo "All selected model downloads done."
