import json

# === File paths ===
old_file = "ref_training_data.json"   # json 1
new_file = "newdata.json"             # json 2
combined_file = "combined_training_data.json"  # Output merged dataset

# === Load both datasets ===
with open(old_file, "r", encoding="utf-8") as f:
    old_data = json.load(f)

with open(new_file, "r", encoding="utf-8") as f:
    new_data = json.load(f)

# === Combine datasets ===
combined_data = old_data + new_data

# === Deduplicate based on 'text' and 'label' pairs ===
seen = set()
deduplicated = []
for item in combined_data:
    key = (item['text'], item['label'])
    if key not in seen:
        deduplicated.append(item)
        seen.add(key)

# === Save merged dataset ===
with open(combined_file, "w", encoding="utf-8") as f:
    json.dump(deduplicated, f, ensure_ascii=False, indent=2)

print(f"✅ Combined and deduplicated dataset saved as: {combined_file}")
print(f"📊 Total unique samples: {len(deduplicated)}")
