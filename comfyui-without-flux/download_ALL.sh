#!/bin/bash

echo "Downloading all models"

bash download_Controlnet.sh
bash download_LDSR.sh
bash download_SUPIR.sh
bash download_fp16.sh
bash download_Florence-2.sh

echo "All models downloaded"
