import os, json

files = sorted([f for f in os.listdir('.') if f.startswith('algo_batch') and f.endswith('.jsonl') and not f.endswith('.bak')])
for f in files:
    count = 0
    with open(f, 'r', encoding='utf-8') as fh:
        for line in fh:
            if line.strip():
                count += 1
    print(f"{f:30s}  size={os.path.getsize(f):>8,}  lines={count}")
