from transformers import AutoTokenizer
import json
from collections import defaultdict
import matplotlib.pyplot as plt

# -------------------- Config --------------------
model_name = "google/bigbird-roberta-base"
input_jsonl = "uoa4_full_trainset.jsonl"
output_jsonl = "uoa4_full_trainset_chunked.jsonl"
chunk_size = 4096
stride = 512  # overlap to preserve context

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load original dataset
with open(input_jsonl, "r", encoding="utf-8") as f:
    examples = [json.loads(line) for line in f]

chunked_data = []
chunk_dist = defaultdict(int)  # e.g., {1: 103, 2: 74, 3: 6}

for entry in examples:
    text = entry["text"]
    label = str(entry["label"]).strip()
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]
    total_tokens = len(input_ids)

    # Short doc — keep as one chunk
    if total_tokens <= chunk_size:
        chunk_text = tokenizer.decode(input_ids, skip_special_tokens=True)
        chunked_data.append({"text": chunk_text, "label": label})
        chunk_dist[1] += 1
        continue

    # Long doc — chunk with stride
    count = 0
    for i in range(0, total_tokens, chunk_size - stride):
        chunk_ids = input_ids[i:i + chunk_size][:chunk_size]
        if len(chunk_ids) < 10:
            continue
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunked_data.append({"text": chunk_text, "label": label})
        count += 1

    if count > 0:
        chunk_dist[count] += 1
    else:
        chunk_dist[0] += 1  

# Save to disk
with open(output_jsonl, "w", encoding="utf-8") as out_f:
    for item in chunked_data:
        out_f.write(json.dumps(item) + "\n")

# -------------------- Print Summary --------------------
print(f"✅ Saved {len(chunked_data)} chunked examples to {output_jsonl}\n")

total_docs = sum(chunk_dist.values())
single_chunk = chunk_dist[1]
multi_chunk = sum(count for c, count in chunk_dist.items() if c > 1)
skipped = chunk_dist[0]

print("📊 Chunking Distribution:")
for c in sorted(chunk_dist):
    print(f" - {c} chunk(s): {chunk_dist[c]} docs")

print(f"\n📦 Total documents: {total_docs}")
print(f"✅ Single-chunk: {single_chunk}")
print(f"🧱 Multi-chunk: {multi_chunk}")
print(f"🚫 Skipped: {skipped}")

# -------------------- Optional: Plot --------------------
try:
    import matplotlib.pyplot as plt

    chunk_keys = sorted(k for k in chunk_dist if k > 0)
    chunk_vals = [chunk_dist[k] for k in chunk_keys]

    plt.figure(figsize=(10, 5))
    plt.bar(chunk_keys, chunk_vals)
    plt.xlabel("Chunks per Document")
    plt.ylabel("Number of Documents")
    plt.title("Chunk Distribution")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except ImportError:
    pass  
