from transformers import AutoTokenizer
import json

# -------------------- Config --------------------
model_name = "google/bigbird-roberta-base"
input_jsonl = "uoa4_training_set.jsonl"
output_jsonl = "uoa4_training_set_chunked.jsonl"
chunk_size = 4096
stride = 512  # overlap to preserve context

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load original dataset
with open(input_jsonl, "r", encoding="utf-8") as f:
    examples = [json.loads(line) for line in f]

chunked_data = []

for entry in examples:
    text = entry["text"]
    label = entry["label"].strip()
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]

    for i in range(0, len(input_ids), chunk_size - stride):
        chunk_ids = input_ids[i:i + chunk_size]
        if len(chunk_ids) < 10:
            continue  # skip tiny trailing chunks
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunked_data.append({
            "text": chunk_text,
            "label": label
        })

# Save chunked dataset
with open(output_jsonl, "w", encoding="utf-8") as out_f:
    for item in chunked_data:
        out_f.write(json.dumps(item) + "\n")

print(f"✅ Saved {len(chunked_data)} chunked examples to {output_jsonl}")
