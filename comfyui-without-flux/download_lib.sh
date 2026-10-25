#!/bin/bash
# Shared download helpers, sourced by the download_*.sh scripts.
#
#   download_file DIR FILE URL [HEADER]   queue a download (runs in the background)
#   download_wait                         wait for all queued downloads, fail if any failed
#
# Up to DOWNLOAD_JOBS files are downloaded at the same time, each over DOWNLOAD_CONNECTIONS
# connections when aria2c is available (plain wget otherwise). Every file is written to FILE.part
# and renamed when complete, so ComfyUI never sees a half-written model and an interrupted
# download resumes on the next run. Files that already exist are skipped.

DOWNLOAD_JOBS=${DOWNLOAD_JOBS:-4}
DOWNLOAD_CONNECTIONS=${DOWNLOAD_CONNECTIONS:-8}

_download_pids=()

_download_one() {
    local dir=$1
    local file=$2
    local url=$3
    local header=$4
    local args=()
    local rc
    local lock

    mkdir -p "$dir"
    # Several scripts share some files (e.g. the Wan VAE) and may run at the same time, so only one
    # process downloads a given file; the others wait for it and then skip it. The lock lives on
    # local disk because network volumes don't always support file locks.
    mkdir -p /tmp/download-locks
    lock=/tmp/download-locks/$(readlink -f "$dir/$file" | md5sum | cut -d' ' -f1)
    exec {lock_fd}>"$lock"
    flock "$lock_fd"
    if [ -e "$dir/$file" ]; then
        echo "$dir/$file already exists, skipping."
        return 0
    fi
    [ -n "$header" ] && args+=(--header="$header")
    echo "Downloading $file..."
    if command -v aria2c >/dev/null 2>&1; then
        aria2c "${args[@]}" --continue=true --allow-overwrite=true --auto-file-renaming=false \
            --max-connection-per-server="$DOWNLOAD_CONNECTIONS" --split="$DOWNLOAD_CONNECTIONS" \
            --min-split-size=16M --file-allocation=none --max-tries=5 --retry-wait=5 \
            --console-log-level=error --summary-interval=0 --download-result=hide \
            --dir="$dir" --out="$file.part" "$url"
    else
        wget "${args[@]}" -q -c -O "$dir/$file.part" "$url"
    fi
    rc=$?
    if [ $rc -eq 0 ] && [ -s "$dir/$file.part" ]; then
        mv "$dir/$file.part" "$dir/$file"
        rm -f "$dir/$file.part.aria2"
        echo "Finished $file."
    else
        echo "ERROR: download of $file failed, it will resume on the next run."
        [ -s "$dir/$file.part" ] || rm -f "$dir/$file.part"
        return 1
    fi
}

download_file() {
    # Keep at most DOWNLOAD_JOBS downloads running
    while [ "$(jobs -rp | wc -l)" -ge "$DOWNLOAD_JOBS" ]; do
        wait -n
    done
    _download_one "$@" &
    _download_pids+=($!)
}

download_wait() {
    local failed=0
    local pid
    for pid in "${_download_pids[@]}"; do
        wait "$pid" || failed=1
    done
    _download_pids=()
    return $failed
}

hf_auth_header() {
    # Authorization header for gated Hugging Face repos, empty when HF_TOKEN is not set
    if [[ -n "${HF_TOKEN}" && "${HF_TOKEN}" != "enter_your_huggingface_token_here" ]]; then
        echo "Authorization: Bearer ${HF_TOKEN}"
    fi
}
