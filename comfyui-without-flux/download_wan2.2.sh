#!/bin/bash

echo "Downloading umt5_xxl_fp8_e4m3fn_scaled.safetensors text encoders"
cd /ComfyUI/models/text_encoders/

file="umt5_xxl_fp8_e4m3fn_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi


echo "Downloading wan_2.1_vae.safetensors"
cd /ComfyUI/models/vae/

file="wan_2.1_vae.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
cd /ComfyUI/models/diffusion_models/

file="wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
cd /ComfyUI/models/diffusion_models/

file="wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
cd /ComfyUI/models/diffusion_models/

file="wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
cd /ComfyUI/models/diffusion_models/

file="wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
cd /ComfyUI/models/loras/

file="wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi

echo "Downloading wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"
cd /ComfyUI/models/loras/

file="wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"
url="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors"

if [ -f "$file" ]; then
    echo "$file already exists."
else
    echo "Downloading $file"
    wget -O $file $url --progress=bar:force:noscroll
fi
