"""Validate all algo_batch JSONL files — check JSON syntax, required keys, duplicates."""
import json, os, hashlib

files = sorted([f for f in os.listdir('.') if f.startswith('algo_batch_') and f.endswith('.jsonl')])
print(f"Found {len(files)} algo_batch files\n")

all_hashes = set()
duplicates = 0
total_examples = 0
total_errors = 0
error_details = []

for fname in files:
    count = 0
    file_errors = 0
    with open(fname, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
                missing = [k for k in ['instruction', 'input', 'output'] if k not in obj]
                if missing:
                    error_details.append(f"  {fname}:L{line_num} - Missing keys: {missing}")
                    file_errors += 1
                    continue
                for k in ['input', 'output']:
                    if not obj[k].strip():
                        error_details.append(f"  {fname}:L{line_num} - Empty '{k}' field")
                        file_errors += 1
                h = hashlib.md5(stripped.encode()).hexdigest()
                if h in all_hashes:
                    duplicates += 1
                else:
                    all_hashes.add(h)
                count += 1
            except json.JSONDecodeError as e:
                error_details.append(f"  {fname}:L{line_num} - JSON ERROR: {str(e)[:80]}")
                file_errors += 1

    size = os.path.getsize(fname)
    status = "OK" if file_errors == 0 else f"{file_errors} ERRORS"
    print(f"  {fname}: {count} examples, {size:,} bytes - {status}")
    total_examples += count
    total_errors += file_errors

print(f"\n{'='*50}")
print(f"  TOTAL EXAMPLES: {total_examples}")
print(f"  TOTAL ERRORS:   {total_errors}")
print(f"  DUPLICATES:     {duplicates}")
print(f"  READY: {'YES' if total_errors == 0 else 'NO - FIX ERRORS FIRST'}")
print(f"{'='*50}")

if error_details:
    print(f"\nError details:")
    for e in error_details[:30]:
        print(e)
