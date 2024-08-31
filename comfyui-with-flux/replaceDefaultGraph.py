import json
import re

# Load the contents of defaultGraph.json
with open('/defaultGraph.json', 'r') as json_file:
    json_data = json.load(json_file)

# Convert the JSON data to a string
json_string = json.dumps(json_data)

# Load the JavaScript file
with open('/ComfyUI/assets/index-CI3N807S.js', 'r') as js_file:
    js_data = js_file.read()

# Locate the defaultGraph dictionary and replace it with the JSON string
updated_js_data = re.sub(r'(?<=const defaultGraph = ).*?(?=;\nwindow\.comfyAPI)', json_string, js_data, flags=re.DOTALL)

# Write the updated JavaScript data back to the file
with open('/ComfyUI/assets/index-CI3N807S.js', 'w') as js_file:
    js_file.write(updated_js_data)
