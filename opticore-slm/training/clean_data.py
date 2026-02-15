"""Clean all JSONL files: remove Google URLs from content and deduplicate."""
import json
import re
import os
import hashlib

all_files = ['sample_training_data.jsonl'] + [f'batch_{i:02d}.jsonl' for i in range(1, 11)]

total_urls_cleaned = 0
total_dupes_removed = 0
seen_hashes = set()

for fname in all_files:
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        continue

    with open(fname, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    cleaned_lines = []
    urls_cleaned = 0
    dupes_removed = 0

    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            cleaned_lines.append(stripped)
            continue

        # Clean Google URLs from all values
        changed = False
        for key in ['instruction', 'input', 'output']:
            if key in obj and 'google.com/search' in obj[key]:
                # Remove markdown-style links [text](url)
                obj[key] = re.sub(r'\[([^\]]*?)\]\(https?://[^\)]*?\)', r'\1', obj[key])
                # Remove bare URLs
                obj[key] = obj[key].replace('https://www.google.com/search?q=', '')
                changed = True

        if changed:
            urls_cleaned += 1

        # Deduplicate
        h = hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()
        if h in seen_hashes:
            dupes_removed += 1
            continue
        seen_hashes.add(h)

        cleaned_lines.append(json.dumps(obj, ensure_ascii=False))

    # Write back
    with open(fname, 'w', encoding='utf-8') as f:
        for cl in cleaned_lines:
            f.write(cl + '\n')

    total_urls_cleaned += urls_cleaned
    total_dupes_removed += dupes_removed
    print(f'{fname}: {len(cleaned_lines)} examples kept, {urls_cleaned} URLs cleaned, {dupes_removed} dupes removed')

print(f'\nTOTAL: {total_urls_cleaned} URL cleanups, {total_dupes_removed} duplicates removed')
