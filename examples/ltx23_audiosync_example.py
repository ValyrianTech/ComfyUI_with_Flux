import argparse
import json
import os
import random
import time
from pathlib import Path
from typing import Optional

import requests


def queue_prompt(url: str, prompt: dict) -> Optional[dict]:
    """Queue a prompt to ComfyUI and return the response."""
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    prompt_url = f"{url}/prompt"
    try:
        r = requests.post(prompt_url, data=data)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as ex:
        print(f'POST {prompt_url} failed: {ex}')
        return None


def get_queue(url: str) -> Optional[dict]:
    """Get the current queue status."""
    queue_url = f"{url}/queue"
    try:
        r = requests.get(queue_url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as ex:
        print(f'GET {queue_url} failed: {ex}')
        return None


def get_history(url: str, prompt_id: str) -> Optional[dict]:
    """Get the history for a specific prompt."""
    history_url = f"{url}/history/{prompt_id}"
    try:
        r = requests.get(history_url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as ex:
        print(f'GET {history_url} failed: {ex}')
        return None


def upload_image(url: str, image_path: Path, timeout: float = 60.0) -> bool:
    """Upload an image to the ComfyUI input folder.
    
    Returns True on success, False otherwise.
    """
    upload_url = f"{url}/upload/image"

    if not image_path.exists():
        print(f"[ERROR] Image not found at: {image_path}")
        return False

    try:
        print(f"[UPLOAD] -> {upload_url} :: {image_path.name}")
        with image_path.open("rb") as f:
            mime_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
            files = {"image": (image_path.name, f, mime_type)}
            data = {"type": "input", "overwrite": "true"}
            resp = requests.post(upload_url, files=files, data=data, timeout=timeout)
        if resp.status_code == 200:
            print(f"[OK] Uploaded {image_path.name}")
            return True
        else:
            print(f"[ERROR] Upload failed for {image_path} (status {resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"[ERROR] Exception during upload for {image_path}: {e}")

    return False


def upload_audio(url: str, audio_path: Path, timeout: float = 60.0) -> bool:
    """Upload an audio file to the ComfyUI input folder.
    
    ComfyUI uses the same /upload/image endpoint for all file types.
    Returns True on success, False otherwise.
    """
    upload_url = f"{url}/upload/image"

    if not audio_path.exists():
        print(f"[ERROR] Audio not found at: {audio_path}")
        return False

    try:
        print(f"[UPLOAD] -> {upload_url} :: {audio_path.name}")
        with audio_path.open("rb") as f:
            mime_type = "audio/mpeg" if audio_path.suffix.lower() == ".mp3" else "audio/wav"
            files = {"image": (audio_path.name, f, mime_type)}
            data = {"type": "input", "overwrite": "true"}
            resp = requests.post(upload_url, files=files, data=data, timeout=timeout)
        if resp.status_code == 200:
            print(f"[OK] Uploaded {audio_path.name}")
            return True
        else:
            print(f"[ERROR] Upload failed for {audio_path} (status {resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"[ERROR] Exception during upload for {audio_path}: {e}")

    return False


def wait_for_completion(url: str, prompt_id: str) -> bool:
    """Wait for a prompt to complete. Polls every 5 seconds."""
    print(f"Waiting for prompt {prompt_id} to complete...")
    while True:
        time.sleep(5)
        queue_response = get_queue(url)
        if queue_response is None:
            continue

        queue_pending = queue_response.get('queue_pending', [])
        queue_running = queue_response.get('queue_running', [])

        # Check position in queue
        for position, item in enumerate(queue_pending):
            if item[1] == prompt_id:
                print(f'Queue running: {len(queue_running)}, Queue pending: {len(queue_pending)}, Position: {position + 1}')

        # Check if currently running
        for item in queue_running:
            if item[1] == prompt_id:
                print(f'Queue running: {len(queue_running)}, Queue pending: {len(queue_pending)}, Currently running...')
                break

        # Check if done (not in pending or running)
        if not any(prompt_id in item for item in queue_pending + queue_running):
            print("Workflow completed!")
            return True


def download_output(url: str, history_response: dict, prompt_id: str, output_dir: str, output_prefix: str = "output") -> Optional[str]:
    """Download the output video from ComfyUI.
    
    Returns the local path if successful, None otherwise.
    """
    outputs = history_response.get(prompt_id, {}).get('outputs', {})
    
    # Node 140 is VHS_VideoCombine in the LTX2.3 audiosync workflow
    output_info = outputs.get('140')
    
    if output_info is None:
        print("Failed to retrieve output. Node 140 not found in outputs.")
        print(f"Available output nodes: {list(outputs.keys())}")
        return None
    
    # VHS_VideoCombine uses 'gifs' key for video output
    video_list = output_info.get('gifs', [])
    if not video_list:
        print("No video found in output. Check history response format.")
        return None
    
    video_info = video_list[0]
    filename = video_info.get('filename', 'unknown')
    subfolder = video_info.get('subfolder', '')

    if filename == 'unknown':
        print("Failed to retrieve output filename.")
        return None

    if subfolder:
        output_url = f"{url}/output/{subfolder}/{filename}"
    else:
        output_url = f"{url}/output/{filename}"

    print(f"Output URL: {output_url}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    local_path = os.path.join(output_dir, f'{output_prefix}_{filename}')

    # Download the file
    try:
        print(f"Downloading to: {local_path}")
        with requests.get(output_url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Downloaded successfully: {local_path}")
        return local_path
    except requests.exceptions.RequestException as ex:
        print(f"Failed to download output: {ex}")
        return None


def main(ip: str, port: int, workflow_path: str, image_path: str, audio_path: str, 
         prompt: Optional[str] = None, output_dir: str = ".", length_seconds: int = 16,
         width: Optional[int] = None, height: Optional[int] = None):
    """Run the LTX2.3 Image-to-Video with AudioSync workflow.
    
    Args:
        ip: ComfyUI server IP address
        port: ComfyUI server port
        workflow_path: Path to the LTX2.3_I2V_with_audiosync_api.json workflow file
        image_path: Path to the input image (PNG or JPG)
        audio_path: Path to the input audio file (MP3 or WAV)
        prompt: Optional prompt text to override the workflow default
        output_dir: Directory to save the output video
        length_seconds: Video length in seconds (default: 16)
        width: Video width in pixels (default: workflow default 1024)
        height: Video height in pixels (default: workflow default 1024)
    """
    url = f"http://{ip}:{port}"
    image_path = Path(image_path)
    audio_path = Path(audio_path)

    # Load workflow
    print(f"Loading workflow from: {workflow_path}")
    with open(workflow_path, 'r', encoding='utf-8') as file:
        workflow = json.load(file)

    # Upload image and audio files
    print("-" * 40)
    if not upload_image(url, image_path):
        print("Failed to upload image. Aborting.")
        return
    
    if not upload_audio(url, audio_path):
        print("Failed to upload audio. Aborting.")
        return
    print("-" * 40)

    # Set the input image filename in node 167 (LoadImage)
    workflow["167"]["inputs"]["image"] = image_path.name
    print(f"Input image: {image_path.name}")

    # Set the input audio filename in node 372 (LoadAudio)
    workflow["372"]["inputs"]["audio"] = audio_path.name
    print(f"Input audio: {audio_path.name}")

    # Set the prompt in node 352 (PrimitiveStringMultiline) if provided
    if prompt is not None:
        workflow["352"]["inputs"]["value"] = prompt
    print(f"Prompt: {workflow['352']['inputs']['value'][:100]}...")

    # Set video length in seconds in node 291 (INTConstant)
    workflow["291"]["inputs"]["value"] = length_seconds
    print(f"Video length: {length_seconds} seconds")

    # Set width in node 292 and height in node 293 (INTConstant) if provided
    if width is not None:
        workflow["292"]["inputs"]["value"] = width
        print(f"Width: {width}px")
    if height is not None:
        workflow["293"]["inputs"]["value"] = height
        print(f"Height: {height}px")

    # Randomize seeds in nodes 114 and 115 (RandomNoise)
    seed_value = random.randint(0, 1000000000000000)
    workflow["114"]["inputs"]["noise_seed"] = seed_value
    workflow["115"]["inputs"]["noise_seed"] = seed_value
    print(f"Seed: {seed_value}")

    print("-" * 40)

    # Queue the prompt
    response = queue_prompt(url, workflow)
    if response is None:
        print("Failed to queue the prompt.")
        return

    prompt_id = response['prompt_id']
    print(f"Prompt ID: {prompt_id}")

    # Wait for completion
    wait_for_completion(url, prompt_id)

    # Get history and download output
    history_response = get_history(url, prompt_id)
    if history_response is None:
        print("Failed to retrieve history.")
        return

    output_prefix = image_path.stem
    result_path = download_output(url, history_response, prompt_id, output_dir, output_prefix)
    
    if result_path:
        print(f"\nSuccess! Output saved to: {result_path}")
    else:
        print("\nFailed to download output.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run LTX2.3 Image-to-Video with AudioSync workflow via ComfyUI API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python ltx23_audiosync_example.py --ip 123.45.67.89 --port 8188 \\
      --workflow LTX2.3_I2V_with_audiosync_api.json \\
      --image input_photo.png \\
      --audio speech.mp3 \\
      --prompt "A woman speaking expressively" \\
      --output ./outputs \\
      --length 16
        """
    )
    parser.add_argument('--ip', type=str, required=True,
                        help='ComfyUI server IP address (e.g., from RunPod TCP Port Mappings)')
    parser.add_argument('--port', type=int, required=True,
                        help='ComfyUI server port (e.g., from RunPod TCP Port Mappings)')
    parser.add_argument('--workflow', type=str, default='LTX2.3_I2V_with_audiosync_api.json',
                        help='Path to the workflow file (default: LTX2.3_I2V_with_audiosync_api.json)')
    parser.add_argument('--image', type=str, required=True,
                        help='Path to the input image (PNG or JPG)')
    parser.add_argument('--audio', type=str, required=True,
                        help='Path to the input audio file (MP3 or WAV)')
    parser.add_argument('--prompt', type=str, default=None, nargs='*',
                        help='Optional prompt text to override the workflow default')
    parser.add_argument('--output', type=str, default='.',
                        help='Directory to save the output video (default: current directory)')
    parser.add_argument('--length', type=int, default=16,
                        help='Video length in seconds (default: 16)')
    parser.add_argument('--width', type=int, default=None,
                        help='Video width in pixels (default: workflow default 1024)')
    parser.add_argument('--height', type=int, default=None,
                        help='Video height in pixels (default: workflow default 1024)')

    args = parser.parse_args()
    
    prompt_text = ' '.join(args.prompt) if args.prompt else None
    
    main(
        ip=args.ip,
        port=args.port,
        workflow_path=args.workflow,
        image_path=args.image,
        audio_path=args.audio,
        prompt=prompt_text,
        output_dir=args.output,
        length_seconds=args.length,
        width=args.width,
        height=args.height
    )
