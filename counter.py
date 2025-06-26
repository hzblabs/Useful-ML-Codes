import zipfile
import json
from collections import Counter

# Enter zip path
zip_path = ""
extract_path = ""

# Unzip
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Find JSON and count labels
import os
json_file = [f for f in os.listdir(extract_path) if f.endswith(".json")][0]
with open(os.path.join(extract_path, json_file), "r", encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

labels = [item['label'] for item in data]
label_counts = dict(Counter(labels))
print(label_counts)
