import os
import argparse
from PIL import Image, UnidentifiedImageError
import torch
from transformers import AutoProcessor, AutoModelForCausalLM


CAPTION_PROMPT = '''<MORE_DETAILED_CAPTION>'''

def caption_images(directory, caption_prefix):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16

    model = AutoModelForCausalLM.from_pretrained(
        "multimodalart/Florence-2-large-no-flash-attn", torch_dtype=torch_dtype, trust_remote_code=True
    ).to(device)
    processor = AutoProcessor.from_pretrained("multimodalart/Florence-2-large-no-flash-attn", trust_remote_code=True)

    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(directory, filename)
            try:
                image = Image.open(image_path).convert("RGB")
            except (OSError, UnidentifiedImageError) as e:
                print(f"Skipping file {filename} due to error: {e}")
                continue

            inputs = processor(text=CAPTION_PROMPT, images=image, return_tensors="pt").to(device, torch_dtype)

            generated_ids = model.generate(
                input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"], max_new_tokens=1024, num_beams=3
            )

            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = processor.post_process_generation(
                generated_text, task=CAPTION_PROMPT, image_size=(image.width, image.height)
            )
            caption_text = caption_prefix + ' ' + parsed_answer[CAPTION_PROMPT]
            print(f"Image: {filename} - Caption: {caption_text}")

            # Save the caption to a .txt file with the same name as the image
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(directory, txt_filename)
            with open(txt_path, 'w') as txt_file:
                txt_file.write(caption_text)

    model.to("cpu")
    del model
    del processor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Caption images in a directory.')
    parser.add_argument('directory', type=str, help='The directory containing images to be captioned.')
    parser.add_argument('caption_prefix', type=str, help='The prefix will be prepended to the caption. For example, "A photo of [trigger]".')
    args = parser.parse_args()

    caption_images(args.directory, args.caption_prefix)
