import json
import re
import subprocess

# Load the contents of defaultGraph.json
with open('/defaultGraph.json', 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# Convert the JSON data to a string
json_string = json.dumps(json_data)
print("JSON String:", json_string)  # Debug print

# Load the JavaScript file with UTF-8 encoding
with open('/ComfyUI/web/assets/index-CI3N807S.js', 'r', encoding='utf-8') as js_file:
    js_data = js_file.read()

# Locate the defaultGraph dictionary and replace it with the JSON string
pattern = r'const defaultGraph = \{.*?\};'
replacement = f'const defaultGraph = {json_string};'
matches = re.findall(pattern, js_data, flags=re.DOTALL)
print("Matches found:", matches)  # Debug print

if matches:
    updated_js_data = re.sub(pattern, replacement, js_data, flags=re.DOTALL)
    # Write the updated JavaScript data back to the file with UTF-8 encoding
    with open('/ComfyUI/web/assets/index-CI3N807S.js', 'w', encoding='utf-8') as js_file:
        js_file.write(updated_js_data)
    print("Replacement applied successfully.")
else:
    print("No matches found for the pattern")

# Verify the replacement using grep
grep_result = subprocess.run(['grep', '-A', '20', 'const defaultGraph =', 'index-CI3N807S.js'], capture_output=True, text=True)
print("Grep result:\n", grep_result.stdout)
