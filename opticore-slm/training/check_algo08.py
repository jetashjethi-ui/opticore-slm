import json

with open("algo_batch_08.jsonl", "r", encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]

print(f"Total entries: {len(lines)}")
print()

# Quality checks
short_instr = [i for i, e in enumerate(lines) if len(e["instruction"]) < 20]
short_output = [i for i, e in enumerate(lines) if len(e["output"]) < 50]
empty_input = [i for i, e in enumerate(lines) if len(e["input"].strip()) == 0]
has_url = [i for i, e in enumerate(lines) if "http" in e["output"]]

print(f"Short instructions (<20 chars): {len(short_instr)}")
if short_instr:
    for idx in short_instr[:3]:
        print(f"  [{idx+1}] {lines[idx]['instruction']}")

print(f"Short outputs (<50 chars): {len(short_output)}")
if short_output:
    for idx in short_output[:3]:
        print(f"  [{idx+1}] {lines[idx]['output'][:80]}")

print(f"Empty inputs: {len(empty_input)}")
print(f"Outputs with URLs: {len(has_url)}")
print()

# Duplicate check
seen = set()
dupes = 0
for e in lines:
    key = e["instruction"][:80] + e["input"][:80]
    if key in seen:
        dupes += 1
    seen.add(key)
print(f"Duplicate entries: {dupes}")
print()

# First 3 entries
print("--- FIRST 3 ENTRIES (truncated) ---")
for i, e in enumerate(lines[:3]):
    print(f"[{i+1}] instr: {e['instruction'][:100]}")
    print(f"     input: {e['input'][:80]}")
    print(f"     output: {e['output'][:120]}")
    print()

# Last 2 entries
print("--- LAST 2 ENTRIES (truncated) ---")
for i, e in enumerate(lines[-2:]):
    idx = len(lines) - 2 + i
    print(f"[{idx+1}] instr: {e['instruction'][:100]}")
    print(f"     input: {e['input'][:80]}")
    print(f"     output: {e['output'][:120]}")
    print()

# Topic coverage
print("--- TOPIC COVERAGE ---")
topics = {}
keywords = [
    "prefix sum", "difference array", "sliding window", "two pointer",
    "binary search", "sort", "hash", "greedy", "dynamic", "memoiz",
    "stack", "queue", "tree", "graph", "cache", "loop", "recursion",
    "bit manipulation", "divide and conquer"
]
for e in lines:
    combined = (e["instruction"] + " " + e["output"][:300]).lower()
    for kw in keywords:
        if kw in combined:
            topics[kw] = topics.get(kw, 0) + 1
for k, v in sorted(topics.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
