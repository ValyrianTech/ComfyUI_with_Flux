# How to Train a LoRa with AI-Toolkit using the 'ComfyUI with Flux.1 dev one-click' Template on Runpod

This tutorial will guide you through the process of training a LoRa using our 'ComfyUI with Flux.1 dev one-click' template on runpod. 

There are two options for training your LoRa:
- **flux_train_ui** (easier but limited functionalities)
- **Command Line** (more complicated but more configurable options)

## Prerequisites

- This script will need to download flux again. Unfortunately, as I'm not the author of the script, I can't change this.
- Because the Flux.1 model is in a gated repository, you will need an access token from Huggingface. This will be set as an environment variable when deploying the template.

## Setting Up Your Huggingface Token

1. Go to your Huggingface account and select 'Settings' and then 'Access Tokens'.
2. Create a new fine-grained token. The only permission that is needed is the 'Read access to contents of all public gated repos you can access' permission.
   - Optionally, if you also want to publish to Huggingface, you will also need to give write access.
   ![screenshot_1](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/images/huggingface_token.png?raw=true)

3. Set the HF_TOKEN environment variable with your new token.
![screenshot_2](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/images/environment_variables.png?raw=true)
4. Go to [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) and click the button to request access.

## Training Your LoRa

There are two options for training your LoRa:

# Option 1: flux_train_ui

This is the easiest method but has limited functionalities.

Open a terminal in JupyterLab and run the following commands:

```bash
cd /workspace/ai-toolkit
python3 flux_train_ui.py
```
![screenshot_3](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/images/start_flux_train_ui.png?raw=true)


1. Click on the gradio link to connect.
![screenshot_4](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/images/flux_train_ui_1.png?raw=true)

2. Set name and trigger word.
3. Upload images.
4. Generate captions. Click 'Add AI captions with Florence-2'
![screenshot_5](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/comfyui-without-flux/ai-toolkit/images/flux_train_ui_2.png?raw=true)
5. Set advanced options. (Change the number of steps if needed, you can also uncheck 'Low VRAM')
6. Set some test prompts.
6. Start training.
7. Check the terminal to monitor progress.


# Option 2: Command Line

This method is more complicated but offers more configurable options.

1. Open JupyterLab.
2. Copy image files to `/workspace/training_set`.
   - Tip: Zip your images before uploading and then unzip them so you don't have to upload lots of files. Use the command `unzip archive.zip -d /workspace/training_set` to extract the files.



### To automatically generate captions:

This command will generate captions for all images in the training set. It will also prepend a prefix to the caption, make sure this includes your trigger word.

```bash
cd /
python3 caption_images.py /workspace/training_set "A photo of X."
```

To configure the job:

1. Navigate to `/workspace/ai-toolkit/config`.
2. Change the `train_lora.yaml` file to suit your needs. The most important parameters are the trigger word, the name, and the number of steps.
3. You can also set some prompts that will be generated periodically to check on the progress. Change them to something relevant to what you are trying to achieve.
4. If you want, you can modify how often a save is made and how often samples are generated.

To start the training:

```bash
cd /workspace/ai-toolkit
python3 run.py config/train_lora.yaml
```

## After Training

There is a symlink in the ComfyUI loras folder. When the training is complete, you should see the safetensors file in the ComfyUI LoraLoader node automatically. 
Intermittent saves are also available and can even be tested while training is still running if you have enough VRAM (this will slow things down though).

Happy training!