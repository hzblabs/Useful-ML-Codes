import pandas as pd
import re
import json

# Load original dataset
input_path = 'combined_training_data.json'
df = pd.read_json(input_path)

# Clean the text column
def clean_text(text):
    if not isinstance(text, str):
        return ""

    # Extract content starting from meaningful section
    start_match = re.search(r'\b(ABSTRACT|INTRODUCTION|BACKGROUND|OBJECTIVE|AIM)\b', text, re.IGNORECASE)
    if start_match:
        text = text[start_match.start():]

    # Remove everything after REFERENCES or BIBLIOGRAPHY
    end_match = re.search(r'\b(REFERENCES|BIBLIOGRAPHY)\b', text, re.IGNORECASE)
    if end_match:
        text = text[:end_match.start()]

    # Remove noisy lines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.search(r'(copyright|doi:|pmid:|all rights reserved|terms of use)', line, re.IGNORECASE):
            continue
        cleaned_lines.append(line.strip())

    # Normalize whitespace
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)
    cleaned_text = re.sub(r' +', ' ', cleaned_text).strip()

    return cleaned_text

# Apply cleaning
df['cleaned_text'] = df['text'].apply(clean_text)

# Drop rows with short or empty cleaned_text
df = df[df['cleaned_text'].str.len() > 500]

# Convert labels like '4*' to numeric
label_map = {'4*': 4, '3*': 3, '2*': 2, '1*': 1}
df['label'] = df['label'].map(label_map)

# Drop rows with missing labels
df = df[df['label'].notnull()]

# Final columns for training
df = df[['cleaned_text', 'label']].rename(columns={'cleaned_text': 'text'})

# Save cleaned dataset as JSON Lines
output_path = 'cleaned_training_data.jsonl'
df.to_json(output_path, orient='records', lines=True, force_ascii=False)

print(f"✅ Cleaned data saved to: {output_path}")
print(f"✅ Final sample count: {len(df)}")
