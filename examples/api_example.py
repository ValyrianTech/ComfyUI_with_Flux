import argparse
import json
import random
import time
import requests


def queue_prompt(url, prompt):
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

def get_queue(url):
    queue_url = f"{url}/queue"
    try:
        r = requests.get(queue_url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as ex:
        print(f'GET {queue_url} failed: {ex}')
        return None


def get_history(url, prompt_id):
    history_url = f"{url}/history/{prompt_id}"
    try:
        r = requests.get(history_url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as ex:
        print(f'GET {history_url} failed: {ex}')
        return None


def main(ip, port, filepath, prompt=None):
    url = f"http://{ip}:{port}"

    with open(filepath, 'r') as file:
        prompt_text = json.load(file)

    # Print the prompt text, either change the text here or in the JSON file
    if prompt is not None:
        prompt_text["6"]["inputs"]["text"] = prompt
    print(f'Prompt: {prompt_text["6"]["inputs"]["text"]}')

    # Set the seed for our KSampler node, always generate a new seed
    prompt_text["25"]["inputs"]["noise_seed"] = random.randint(0, 1000000000000000)
    print(f'Seed: {prompt_text["25"]["inputs"]["noise_seed"]}')

    response1 = queue_prompt(url, prompt_text)
    if response1 is None:
        print("Failed to queue the prompt.")
        return

    prompt_id = response1['prompt_id']
    print(f'Prompt ID: {prompt_id}')
    print('-' * 20)

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
                print(f'Queue running: {len(queue_running)}, Queue pending: {len(queue_pending)}, Workflow is in position {position + 1} in the queue.')

        # Check if the prompt is currently running
        for item in queue_running:
            if item[1] == prompt_id:
                print(f'Queue running: {len(queue_running)}, Queue pending: {len(queue_pending)}, Workflow is currently running.')
                break

        if not any(prompt_id in item for item in queue_pending + queue_running):
            break

    history_response = get_history(url, prompt_id)
    if history_response is None:
        print("Failed to retrieve history.")
        return

    output_info = history_response.get(prompt_id, {}).get('outputs', {}).get('9', {}).get('images', [{}])[0]
    filename = output_info.get('filename', 'unknown.png')
    output_url = f"{url}/output/{filename}"

    print(f"Output URL: {output_url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a prompt to the queue and wait for the output.')
    parser.add_argument('--ip', type=str, required=True, help='The public IP address of the pod (you can see this in the "TCP Port Mappings" tab when you click the "connect" button on Runpod.io)')
    parser.add_argument('--port', type=int, required=True, help='The external port of the pod (you can see this in the "TCP Port Mappings" tab when you click the "connect" button on Runpod.io)')
    parser.add_argument('--filepath', type=str, required=True, help='The path to the JSON file containing the workflow in api format')
    parser.add_argument('--prompt', type=str, required=False, help='The prompt to use for the workflow', default=None, nargs='*')

    args = parser.parse_args()
    main(args.ip, args.port, args.filepath, ' '.join(args.prompt) if args.prompt is not None else None)
