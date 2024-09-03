# ComfyUI with Flux.1-dev

## Update 2024-09-03
- Updated ComfyUI to latest version
- Added Realism LoRa from XLabs-AI and VideoAditor
- Custom LoRa for Valyrian Tech's virtual spokesperson (Trigger word: "GracePenelopeTargaryen")
- Added JupiterLab for easy uploading of files

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

## Note
Patience is a virtue! This template includes all the files needed to run ComfyUI with Flux.1-dev, so it is a big file. The deployment process should take about 10 minutes to complete. 

Happy creating!

## JupiterLab
You can use JupyterLab to upload files to your pod, like custom LoRa models or other files.
Click on the connect to 8888 to open JupyterLab.
You will be asked for a token, this will be different each time you deploy a new pod.
The token can be seen in the logs of the runpod template:

![JupyterLab token](https://github.com/ValyrianTech/ComfyUI_with_Flux/blob/main/JupyterLab_token.png?raw=true)

Alternatively, you can start the web terminal and connect to it and enter the command "jupyter server list" to get the token.

