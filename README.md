# ComfyUI with Flux.1-dev

## Update 2026-10-22
- **Faster deployment on RunPod**: ComfyUI is ready about 1 minute after the container starts on a fresh volume instead of about 4.5 minutes, and restarts take about half as long.
    - **ComfyUI is no longer copied to the network volume.** Its code, the bundled custom nodes and the Python environment stay in the image, on the pod's fast local disk, so nothing is copied on the first start, Python doesn't import thousands of files over the network volume, and image updates actually take effect. Only your data lives on the volume, see [What is stored on the network volume](#what-is-stored-on-the-network-volume).
    - **The models baked into the image are linked onto the volume instead of copied**, so the 'with Flux' image no longer spends the first start copying ~30 GB, and the volume only holds your own models. Both images still work offline. Set `COPY_BAKED_MODELS=true` to copy them instead, see [Using the 'without Flux' image on a volume set up with the 'with Flux' image](#using-the-without-flux-image-on-a-volume-set-up-with-the-with-flux-image).
    - JupyterLab is the first thing to start and the AI-Toolkit UI comes up right away too.
    - Smaller and faster image builds: the unused CUDA runtime libraries are gone (PyTorch ships its own), custom nodes are cloned without their git history, the AI-Toolkit UI builds in its own stage and Python packages are installed with `uv`.
    - AI-Toolkit's code now stays inside the image; only your configs, datasets, outputs and the UI database are persisted on the volume in `/workspace/ai-toolkit-data`. `/workspace/ai-toolkit` still works as before.
    - Removed the Mixlab nodes from the image (they were disabled at startup anyway). Set `ENABLE_MIXLAB=true` to have them downloaded to the network volume and loaded on pod start; with it off they are not downloaded.
- **Optional model downloads**: more models can be downloaded on pod start with environment variables, in the background, several files at a time and resumable, see [Downloading more models on pod start](#downloading-more-models-on-pod-start). Everything is off by default, so a pod doesn't touch the network for models unless you ask for it.
- **JupyterLab always needs a login**: set it with the new `JUPYTER_PASSWORD` environment variable. If it's left empty, a random token is created and a login link is printed to the pod's logs. Once a browser has logged in it stays logged in, also after the pod restarts.
- **CivitAI downloader included**: `civitai-download` ([civitai-bulk-downloader](https://github.com/deepratna-awale/civitai-bulk-downloader), a copy pinned to one version is in `comfyui-without-flux/vendor`) is installed, with an example notebook in `/workspace/civitai`. Set your CivitAI API key in the new `CAI_API_KEY` environment variable, see [Downloading models from CivitAI](#downloading-models-from-civitai).
- **Relaxed file permissions**: files and folders in the image and on `/workspace` can be written by every user and tool, so JupyterLab, ComfyUI-Manager and AI-Toolkit no longer hit permission errors. If your network volume refuses `chmod`/`chown` (e.g. `git clone` into `/workspace` fails with "chmod on .git/config.lock failed"), set `ENABLE_VOLUME_PERMS_SHIM=true`.

## Downloading more models on pod start

The images come with the models their workflows need. On every pod start, the extra model sets you select are downloaded straight to the network volume in the background, all at the same time (log: `/workspace/model_downloads.log`). Files that are already on the volume are skipped, so after the first start only new selections are downloaded. Their models show up as each file finishes (refresh the model list in the UI to see them).

Set these as environment variables in the RunPod template, or when deploying a pod:

| Environment variable | Default | Downloads |
|---|---|---|
| `DOWNLOAD_FLUX` | `false` | Flux.1-dev (needs `HF_TOKEN`, gated repo), its VAE, the clip_l and t5xxl fp8 text encoders, the example LoRAs and the openpose annotators. Use it with the 'without Flux' image; the 'with Flux' image has all of these built in. ComfyUI then waits for Flux, its VAE and the text encoders before it starts (`COMFYUI_WAIT_FOR_FLUX=false` starts it right away) |
| `DOWNLOAD_FLUX_KONTEXT` | `false` | Flux.1-Kontext-dev (needs `HF_TOKEN`), for the `EditImage_flux-kontext-dev` workflow |
| `DOWNLOAD_FLUX2` | `false` | Flux.2-dev fp8, its VAE and text encoder |
| `DOWNLOAD_WAN` | `false` | Wan 2.1 text2video and image2video |
| `DOWNLOAD_WAN22` | `false` | Wan 2.2 text2video and image2video |
| `DOWNLOAD_INFINITETALK` | `false` | Wan 2.1 InfiniteTalk |
| `DOWNLOAD_LTX2` | `false` | LTX2 |
| `DOWNLOAD_LTX23` | `false` | LTX2.3 |
| `DOWNLOAD_QWEN_FP8` | `false` | Qwen Image Edit (fp8) |
| `DOWNLOAD_QWEN_BF16` | `false` | Qwen Image Edit (bf16) |
| `DOWNLOAD_Z_IMAGE` | `false` | Z-Image Turbo |
| `DOWNLOAD_CONTROLNET` | `false` | Flux and SDXL ControlNets, 4x-UltraSharp |
| `DOWNLOAD_OUTPAINTING` | `false` | Outpainting models |
| `DOWNLOAD_SUPIR` | `false` | SUPIR upscaler |
| `DOWNLOAD_LDSR` | `false` | LDSR upscaler |
| `DOWNLOAD_UPSCALERS` | `false` | 4x-UltraSharp |
| `DOWNLOAD_FLORENCE2` | `false` | Florence-2 |
| `DOWNLOAD_T5_FP16` | `false` | t5xxl fp16 text encoder |
| `DOWNLOAD_VIBEVOICE` | `false` | VibeVoice Large and its tokenizer |

Instead of one variable per set you can also list them in `DOWNLOAD_MODELS`, for example `DOWNLOAD_MODELS=wan2.2,ltx2.3`. The names are `flux`, `kontext`, `flux2`, `wan2.1`, `wan2.2`, `infinitetalk`, `ltx2`, `ltx2.3`, `qwen_fp8`, `qwen_bf16`, `z-image`, `controlnet`, `outpainting`, `supir`, `ldsr`, `upscalers`, `florence2`, `t5_fp16` and `vibevoice`; `all` selects every set.

You can also download a set later from the terminal, e.g. `bash /download_LTX2.3.sh`, or run `DOWNLOAD_MODELS=ltx2.3 /download_selected.sh`. `DOWNLOAD_JOBS` (default 4) sets how many files download at once in total, across all selected sets, and `DOWNLOAD_CONNECTIONS` (default 8) how many connections each file uses.

## What is stored on the network volume

Only your own data is kept on the network volume. Everything else (ComfyUI's code, the custom nodes that come with the image, the Python environment, AI-Toolkit's code and UI, and caches like Hugging Face, torch hub and `__pycache__`) stays inside the image on the pod's local disk. It is faster there than on a network volume, and it is updated whenever you deploy a newer image.

| On the volume | What it holds |
|---|---|
| `/workspace/comfyui-data/models` | Your models. The download scripts and ComfyUI-Manager save here. The models built into the image show up here as links (see below). |
| `/workspace/comfyui-data/input` | ComfyUI's input folder (uploaded images, audio, video) |
| `/workspace/comfyui-data/output` | ComfyUI's output folder |
| `/workspace/comfyui-data/user` | Your workflows, ComfyUI settings and the ComfyUI-Manager config |
| `/workspace/comfyui-data/custom_nodes` | Custom nodes you install yourself, e.g. with ComfyUI-Manager |
| `/workspace/ai-toolkit-data` | AI-Toolkit configs, datasets, outputs and the UI database |
| `/workspace/start_user.sh`, `/workspace/model_downloads.log` | Your startup script and the model download log |

The old paths still work: `/ComfyUI/models`, `/ComfyUI/input`, `/ComfyUI/output` and `/ComfyUI/user` are links to the folders above, and `/workspace/ComfyUI` is a link to `/ComfyUI`. So `/workspace/ComfyUI/models/loras` is still where your LoRAs go.

Custom nodes you install with ComfyUI-Manager are put in `/workspace/comfyui-data/custom_nodes`, and ComfyUI loads them next to the bundled ones (configured in `/ComfyUI/extra_model_paths.yaml`). Because the Python environment comes fresh with each pod, their `requirements.txt` is installed again on every start, before ComfyUI starts. If you update one of the bundled custom nodes, that update lasts until the pod is replaced; the next image brings its own version.

The default workflows and example inputs that come with the image are added to the volume when they are missing. Files that are already there are never overwritten, so your edits are kept.

The models built into the image (in `/opt/comfyui-models`, for example Flux and its text encoders in the 'with Flux' image) are linked into `/workspace/comfyui-data/models`, so ComfyUI and every custom node find them in the usual folders without them being copied. A file of the same name that is already on the volume is used instead. Links to models that the current image doesn't have (e.g. after switching from the 'with Flux' to the 'without Flux' image) are removed on start.

### Using the 'without Flux' image on a volume set up with the 'with Flux' image

To set up a volume once with the 'with Flux' image and then deploy the smaller 'without Flux' image on it, deploy the 'with Flux' image the first time with `COPY_BAKED_MODELS=true`. The built-in models are then copied onto the volume (once, about 30 GB) instead of linked, so they are still there with the 'without Flux' image. Alternatively, use the 'without Flux' image with `DOWNLOAD_FLUX=true` and `HF_TOKEN` set to download them.

**Volumes from older versions** that hold a full copy of ComfyUI in `/workspace/ComfyUI` are moved over automatically on the first start: `models`, `input`, `output` and `user` are moved into `/workspace/comfyui-data` (a quick rename, nothing is copied), and custom nodes you installed yourself go to `/workspace/comfyui-data/custom_nodes`. The rest of the old copy, the ComfyUI code and the bundled custom nodes, is moved to `/workspace/ComfyUI.old` and not deleted. Check it for anything you still need, then delete it to free up space. Once a volume has been moved over, don't use it with an older version of this image.

## Update 2026-04-05
- Added LTX2.3 workflows: I2V and FL2V
- Updated ComfyUI to latest version

## Update 2026-01-25
- Updated ComfyUI and AI-Toolkit to latest version
- Supports LTX2, Z-Image, Flux2

## Update 2025-11-26
- Updated ComfyUI and AI-Toolkit to latest version to support Flux.2 (You will need a GPU with at least 96GB of VRAM like the RTX PRO 6000 to run this)


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
    ComfyUI-SUPIR, was-node-suite-comfyui, comfyui_controlnet_aux, ComfyUI-Easy-Use, comfyui-reactor-node, ComfyUI_LayerStyle

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
JupyterLab always asks for a login, because the pod's proxy URL is public and JupyterLab gives full access to the pod, including your HF_TOKEN and your files.
Set the `JUPYTER_PASSWORD` environment variable in the template and enter it when you are asked for a token, or open `https://<pod id>-8888.proxy.runpod.net/lab?token=<your password>` to skip the login page. If `JUPYTER_PASSWORD` is left empty, a random token is created on every start and a ready-to-click login link is printed to the pod's logs.
You only log in once per browser: the login cookie is kept valid across pod restarts and redeploys on the same network volume (the key is stored in `/workspace/.jupyter`).

JupyterLab is started first, before the volume setup and the model downloads, so you can use it while the models are still downloading.

### Downloading models from CivitAI
[civitai-bulk-downloader](https://github.com/deepratna-awale/civitai-bulk-downloader) is installed in the image, both as the `civitai-download` command and as the `civitai_downloader` Python package. Set the `CAI_API_KEY` environment variable in the template to your CivitAI API key (create one at https://civitai.com/user/account), then open `/workspace/civitai/civitai_downloader.ipynb` in JupyterLab, or run it from a terminal:

```bash
civitai-download --sd /ComfyUI --ui comfyui --url "https://civitai.com/models/4201?modelVersionId=130072"
```

Each model is saved into the matching ComfyUI folder (LoRAs in `models/loras`, checkpoints in `models/checkpoints`, ...) on the network volume.

Note: JupyterLab normally cannot open folders named 'checkpoints' (such as /ComfyUI/models/checkpoints), because that word is reserved by its notebook-checkpoint API. This image includes a small server extension that works around it, so the folder opens like any other.

## Note
Patience is a virtue! This template includes all the files needed to run ComfyUI with Flux.1-dev, so it is a big file. The deployment process should take about 15 minutes to complete. 


Update: there is also a new template now for faster deploy, the idea is to use a new and empty network volume once with the 'ComfyUI with Flux' template, set `COPY_BAKED_MODELS=true`, this will copy all the model files to the network volume and then the next time you want to deploy a new pod, you can use the same network volume but change the template to the 'ComfyUI without Flux' template. That one is much smaller as it doesn't contain the more than 20+ GB of model files so it starts up a lot faster. 
[ComfyUI without Flux.1 dev one-click](https://www.runpod.io/console/explore/aomdggbx0y)

Happy creating!