# ComfyUI with Flux.1-dev

This is a shortened version of the README, read the full version here: [ComfyUI with Flux.1-dev README](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/README.md)

## Update 2025-11-26
- Updated ComfyUI and AI-Toolkit to latest version to support Flux.2 (You will need a GPU with at least 96GB of VRAM like the RTX PRO 6000 to run this)

## Update 2025-10-11
- Updated ComfyUI to latest version and CUDA to 12.8, so now it supports the latest GPUs like the RTX 5090 and RTX PRO 6000
- Added new workflows for Wan2.2 + InfiniteTalk and Qwen-image-edit-2509
- Added workflow for VibeVoice to generate AI voices from text
- Updated AI Toolkit to the latest version, check out the new UI! It will be started automatically on port 8675, in the environment variables you can set the password for the UI with the variable AI_TOOLKIT_AUTH (default is 'changeme')_

## Update 2025-03-02
- **Added new workflows for Wan2.1 Text2Video and Image2Video**
- **Updated ComfyUI to latest version, now using the new UI, click on the Icon labeled 'Workflows' to load any of the included workflows**
- **Added Environment Variables: DOWNLOAD_WAN and DOWNLOAD_FLUX, set to true to auto-download the models**
- **Note: the Wan2.1 models will require 70GB+ of storage**
- **Note: the Flux.1-dev models will require 30GB+ of storage and also require the HF_TOKEN environment set (This is only for the ComfyUI_without_Flux template, these files are already included in the ComfyUI_with_Flux template)**

## Update 2024-10-11

- **Added AI-Toolkit to train LoRas:  [AI-Toolkit Tutorial](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/Tutorial_how_to_train_a_LoRa.md)**
- **New workflows**
- **Improved support for network volumes and customization**
- **New secondary template without the 20GB+ flux model for faster deploy**
    - There is now a secondary template that is identical to this template, but it does not include the 20GB+ flux model, so it would be faster to deploy. You can find it here: [ComfyUI without Flux.1 dev one-click](https://runpod.io/console/deploy?template=aomdggbx0y&ref=2vdt3dn9)
    - If you use a network volume, all the files are copied to the network volume on the first run, so the next time you deploy a pod, you can change the template to the `ComfyUI without Flux.1 dev one-click` template.
- **Fixed some issues with JupyterLab**
- **Pre-installed a bunch of popular custom nodes**

## Video
[![demo video](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/video_screenshot.png?raw=true)](https://youtu.be/WojIAFte-5E)


## Overview
Welcome to the one-click deployment template of ComfyUI with Flux.1-dev. This template is designed to help you kickstart your journey with text-to-image conversions and more, without the hassle of extensive setup. 

## Features
- **ComfyUI**: An intuitive interface that makes interacting with your workflows a breeze.
- **Flux.1-dev**: An open-source text-to-image model that powers your conversions.
- **ComfyUI Manager and Custom-Scripts**: These tools come pre-installed to enhance the functionality and customization of your applications.
- **Default Workflows**: Jumpstart your tasks with pre-configured workflows for common tasks such as converting text to image (txt2img) and image to image (img2img).

## Getting Started
Ready to dive in? Simply click on the 'Deploy' button. This will automatically set up ComfyUI with Flux.1-dev on your Runpod.io account, along with the default workflows, ComfyUI Manager, and Custom-Scripts.

## API
See full README for more info on how to use the API: [ComfyUI with Flux.1-dev README](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/README.md)

## JupyterLab
See full README for more info on how to use JupyterLab: [ComfyUI with Flux.1-dev README](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/README.md)

## Note
Patience is a virtue! This template includes all the files needed to run ComfyUI with Flux.1-dev, so it is a big file. The deployment process should take about 15 minutes to complete. 

## Deploy faster
There is also a new template now for faster deploy, the idea is to use a new and empty network volume once with the 'ComfyUI with Flux' template, this will copy all the files to the network volume and then the next time you want to deploy a new pod, you can use the same network volume but change the template to the 'ComfyUI without Flux' template. That one is much smaller as it doesn't contain the more than 20+ GB of model files so it starts up a lot faster. 
Link: [ComfyUI without Flux.1 dev one-click](https://www.runpod.io/console/explore/aomdggbx0y)

Happy creating!