"""Merge all JSONL batch files into one training file."""
import os
import json
import glob

output_file = "all_training_data.jsonl"

# Original data files
input_files = ["sample_training_data.jsonl"] + [f"batch_{i:02d}.jsonl" for i in range(1, 11)]

# Algorithm-focused data files (01-10)
algo_files = sorted(glob.glob("algo_batch_*.jsonl"))
algo_files = [f for f in algo_files if not f.endswith(".bak")]
input_files.extend(algo_files)

print(f"[Merge] Found {len(input_files)} input files ({len(algo_files)} algorithm batches)")

total = 0
with open(output_file, "w", encoding="utf-8") as out:
    for fname in input_files:
        if not os.path.exists(fname):
            print(f"  ⚠ Skipping {fname} (not found)")
            continue
        with open(fname, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                    if all(k in obj for k in ["instruction", "input", "output"]):
                        out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        total += 1
                except json.JSONDecodeError:
                    pass

print(f"\n[OK] Merged {total} examples into {output_file}")
