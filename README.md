# ComfyUI with Flux.1-dev

## Update 2025-10-11
- Updated ComfyUI to latest version and CUDA to 12.8, so now it supports the latest GPUs like the RTX 5090 and RTX PRO 6000
- Added new workflows for Wan2.2 + InfiniteTalk and Qwen-image-edit-2509
- Added workflow for VibeVoice to generate AI voices from text
- Updated AI Toolkit to the latest version, check out the new UI! It will be started automatically on port 8675, in the environment variables you can set the password for the UI with the variable AI_TOOLKIT_AUTH (default is 'changeme')

## Update 2025-03-02
- **Added new workflows for Wan2.1 Text2Video and Image2Video**
- **Updated ComfyUI to latest version, now using the new UI, click on the Icon labeled 'Workflows' to load any of the included workflows**
- **Added Environment Variables: DOWNLOAD_WAN and DOWNLOAD_FLUX, set to true to auto-download the models**
- **Note: the Wan2.1 models will require 70GB+ of storage**
- **Note: the Flux.1-dev models will require 30GB+ of storage and also require the HF_TOKEN environment set (This is only for the ComfyUI_without_Flux template, these files are already included in the ComfyUI_with_Flux template)**

## Update 2024-10-11

- **Added AI-Toolkit to train LoRas**
    - You can now train your own LoRas with the AI-Toolkit directly in this template and try them at the same time.
    - Here is a tutorial on how to train your own LoRa: [AI-Toolkit Tutorial](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/Tutorial_how_to_train_a_LoRa.md)

- **Included workflows:**
    - AdvanceLivePortrait
    - AdvancedLivePortrait_with_ExpressionEditor
    - Controlnet
    - ExpressionEditor
    - FaceSwap
    - img2img
    - Inpainting
    - LoRa
    - Outpainting
    - txt2img
    - Upscale_LDSR
    - Upscale_SUPIR
    - Xlab-AI_Realism_LoRa

    **Note**: Some of these workflows require additional models to be downloaded, in the root folder there are some scripts starting with 'download_X.sh' that you can run to download the models in the correct folder.
    Run `bash /download_ALL.sh` to download all the models at once (this will take a while, it's about 50GB of data).
    You can also just run the scripts for the workflows you are interested in.


- **Improved support for network volumes and customization**
    - The startup script is now located in `/workspace/start_user.sh` and is persistent on the network volume. This allows you to customize the startup script to your liking.

- **New secondary template without the 20GB+ flux model for faster deploy**
    - There is now a secondary template that is identical to this template, but it does not include the 20GB+ flux model, so it would be faster to deploy. You can find it here: [ComfyUI without Flux.1 dev one-click](https://runpod.io/console/deploy?template=aomdggbx0y&ref=2vdt3dn9)
    - If you use a network volume, all the files are copied to the network volume on the first run, so the next time you deploy a pod, you can change the template to the `ComfyUI without Flux.1 dev one-click` template.

- **Fixed some issues with JupyterLab**

- **Pre-installed a bunch of popular custom nodes**

    - websocket_image_save, ComfyUI-Florence2, ComfyUI-Logic, cg-use-everywhere, comfy-plasma, cg-image-picker, ComfyUI_JPS-Nodes,
    ComfyUI_essentials, ComfyUI-Flowty-LDSR, ComfyUI-VideoHelperSuite, ComfyUI-KJNodes, ComfyUI-Custom-Scripts, ComfyUI-Manager, 
    ComfyUI_UltimateSDUpscale, ComfyUI-AdvancedLivePortrait, x-flux-comfyui, rgthree-comfy, ComfyUI-Impact-Pack, ComfyUI_ComfyRoll_CustomNodes,
    ComfyUI-SUPIR, was-node-suite-comfyui, comfyui_controlnet_aux, ComfyUI-Easy-Use, comfyui-reactor-node, ComfyUI_LayerStyle, comfyui-mixlab-nodes

    - This should make the problems with 'IMPORT FAILED' less frequent. If you still encounter this problem when restarting a pod, you can go to the manager and click on 'Custom Nodes Manager', find the one that is causing the problem and click on the 'Try fix' button. 
    - If you have a lot of custom nodes that are causing problems, there is another possible solution, but should only be use as a 'last resort', you can make a persistent venv by running the command `bash /make_venv.sh` in the terminal.
    - This will create a persistent venv on the workspace and install all the dependencies that are needed. However, this will take a long time and will require at least another 15GB of space on the network volume.



## Update 2024-09-03
- Updated ComfyUI to latest version
- Added Realism LoRa from XLabs-AI and VideoAditor
- Custom LoRa for Valyrian Tech's virtual spokesperson (Trigger word: "GracePenelopeTargaryen")
- Added JupyterLab for easy uploading of files

## Video
[![demo video](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/video_screenshot.png?raw=true)](https://youtu.be/WojIAFte-5E)

# Runpod.io template
[Link to template on Runpod.io](https://runpod.io/console/deploy?template=rzg5z3pls5&ref=2vdt3dn9)


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
There is an example python script in the 'examples' folder that demonstrates how to interact with the ComfyUI API.
It will add a new workflow to the queue, then periodically check the status of the workflow until it is completed.
When the workflow is completed, a download link will be printed to the console.

To run the example script you need to run a command like this, replacing the IP address, port, and filepath with the appropriate values:
```
python api_example.py --ip 194.68.245.38 --port 22018 --filepath workflow_api_format.json
```

Optionally, you can also specify a new prompt for the workflow:
```
python api_example.py --ip 194.68.245.38 --port 22018 --filepath workflow_api_format.json --prompt "platinum blonde woman with magenta eyes"
```

[api_example.py](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/examples/api_example.py)

You can find your IP address and port in the 'TCP Port Mappings' section when you click the 'Connect' button on the Runpod.io.
You will need the Public IP and the External Port.
![TCP Port Mappings](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/tcp_port_mappings.png?raw=true)

If you want to use a different workflow, keep in mind you must use the API format of the workflow, you can get this by clicking the 'Save (API Format)' button in the ComfyUI.

## JupyterLab
You can use JupyterLab to upload files to your pod, like custom LoRa models or other files.

Click on the "Connect to HTTP Service [Port 8888]" button to open JupyterLab.
You will be asked for a token, this will be different each time you deploy a new pod.

The token can be seen in the logs of the runpod template:

![JupyterLab token](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/JupyterLab_token.png?raw=true)

Alternatively, you can start the web terminal and connect to it and enter the command "jupyter server list" to get the token.

Note: Due to a technical peculiarity in JupyterLab, the folder /ComfyUI/models/checkpoints will not open, because 'checkpoints' is a special word in JupyterLab.
If you need to copy a file in this folder, you can still connect via the web terminal and use the 'wget' command to download your file.

## Note
Patience is a virtue! This template includes all the files needed to run ComfyUI with Flux.1-dev, so it is a big file. The deployment process should take about 15 minutes to complete. 


Update: there is also a new template now for faster deploy, the idea is to use a new and empty network volume once with the 'ComfyUI with Flux' template, this will copy all the files to the network volume and then the next time you want to deploy a new pod, you can use the same network volume but change the template to the 'ComfyUI without Flux' template. That one is much smaller as it doesn't contain the more than 20+ GB of model files so it starts up a lot faster. 
[ComfyUI without Flux.1 dev one-click](https://www.runpod.io/console/explore/aomdggbx0y)

Happy creating!