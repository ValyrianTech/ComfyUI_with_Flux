import json
import re
import os
import glob

# Load the contents of defaultGraph.json
with open('/defaultGraph.json', 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# Convert the JSON data to a string
json_string = json.dumps(json_data)
print("JSON String:", json_string)  # Debug print

# Pattern to be located
pattern = r'const defaultGraph = \{.*?\};'
replacement = f'const defaultGraph = {json_string};'

# Search for JavaScript files in the directory
for filename in glob.glob('/ComfyUI/web/assets/index-*.js'):
    # Load the JavaScript file with UTF-8 encoding
    with open(filename, 'r', encoding='utf-8') as js_file:
        js_data = js_file.read()

    # Locate the defaultGraph dictionary and replace it with the JSON string
    matches = re.findall(pattern, js_data, flags=re.DOTALL)
    print("Matches found in", filename, ":", matches)  # Debug print

    if matches:
        updated_js_data = re.sub(pattern, replacement, js_data, flags=re.DOTALL)
        # Write the updated JavaScript data back to the file with UTF-8 encoding
        with open(filename, 'w', encoding='utf-8') as js_file:
            js_file.write(updated_js_data)
        print("Replacement applied successfully in", filename)
        break  # Exit the loop after finding and replacing in the correct file
    else:
        print("No matches found for the pattern in", filename)
