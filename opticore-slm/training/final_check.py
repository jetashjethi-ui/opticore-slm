"""
Final comprehensive check: validate, dedup, merge, and verify ALL training data.
Focused on the 3 newly imported files: algo_batch_07, algo_batch_09, algo_batch_10.
Also runs double validation on everything.
"""
import os, json, glob, re, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_KEYS = {"instruction", "input", "output"}
report = []

def log(msg):
    print(msg)
    report.append(msg)

def validate_and_fix(filepath):
    if not os.path.exists(filepath):
        return {"file": os.path.basename(filepath), "status": "NOT_FOUND", "total": 0, "valid": 0, "fixed": 0, "dropped": 0, "dupes": 0}

    basename = os.path.basename(filepath)
    stats = {"file": basename, "status": "OK", "total": 0, "valid": 0, "fixed": 0, "dropped": 0, "dupes": 0}
    valid_entries = []
    seen_keys = set()

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            stats["total"] += 1

            # Parse JSON
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError:
                # Try tab fix
                try:
                    obj = json.loads(stripped.replace('\t', '\\t'))
                    stats["fixed"] += 1
                except json.JSONDecodeError:
                    stats["dropped"] += 1
                    log(f"    DROPPED line {line_num} in {basename}: unparseable JSON")
                    continue

            # Validate keys
            if not isinstance(obj, dict) or not all(k in obj for k in REQUIRED_KEYS):
                stats["dropped"] += 1
                log(f"    DROPPED line {line_num} in {basename}: missing required keys")
                continue

            # Validate non-empty strings
            skip = False
            for key in REQUIRED_KEYS:
                if not isinstance(obj[key], str):
                    stats["dropped"] += 1
                    log(f"    DROPPED line {line_num} in {basename}: {key} is not a string")
                    skip = True
                    break
            if skip:
                continue

            if len(obj["instruction"].strip()) == 0 or len(obj["output"].strip()) == 0:
                stats["dropped"] += 1
                log(f"    DROPPED line {line_num} in {basename}: empty instruction or output")
                continue

            # Remove hallucinated URLs from output
            original_output = obj["output"]
            obj["output"] = re.sub(r'\[Source\]\(https?://[^\)]+\)', '', obj["output"])
            obj["output"] = re.sub(r'https?://\S+', '', obj["output"]).strip()
            if obj["output"] != original_output:
                stats["fixed"] += 1

            # Deduplicate
            dedup_key = obj["instruction"].strip() + "|||" + obj["input"].strip()
            if dedup_key in seen_keys:
                stats["dupes"] += 1
                continue
            seen_keys.add(dedup_key)

            stats["valid"] += 1
            valid_entries.append(obj)

    # Write back
    for attempt in range(3):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for entry in valid_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            break
        except PermissionError:
            if attempt < 2:
                time.sleep(1)
            else:
                log(f"  [ERR] Could not write {basename} after 3 attempts")
                stats["status"] = "WRITE_ERROR"

    if stats["dropped"] > 0 or stats["fixed"] > 0 or stats["dupes"] > 0:
        stats["status"] = "FIXED"
    return stats

# --- MAIN ---
log("=" * 65)
log("  FINAL VALIDATION - All Training Data")
log("=" * 65)

# All files
batch_files = [f"batch_{i:02d}.jsonl" for i in range(1, 11)]
algo_files = sorted([f for f in glob.glob("algo_batch_*.jsonl") if not f.endswith(".bak")])
all_files = ["sample_training_data.jsonl"] + batch_files + algo_files

log(f"\nTotal input files: {len(all_files)} ({len(algo_files)} algo batches)")
log("")

# --- PASS 1 ---
log("=" * 65)
log("  PASS 1: Validate, Fix & Deduplicate")
log("=" * 65)
pass1_total = 0
pass1_valid = 0
pass1_fixed = 0
pass1_dropped = 0
pass1_dupes = 0

new_files = {"algo_batch_07.jsonl", "algo_batch_09.jsonl", "algo_batch_10.jsonl"}

for filepath in all_files:
    stats = validate_and_fix(filepath)
    marker = " [NEW]" if stats["file"] in new_files else ""
    icon = "[OK]" if stats["status"] == "OK" else ("[FX]" if stats["status"] == "FIXED" else "[NF]")
    log(f"  {icon} {stats['file']:30s} T:{stats['total']:4d} V:{stats['valid']:4d} F:{stats['fixed']:2d} D:{stats['dropped']:2d} Dup:{stats['dupes']:2d}{marker}")
    pass1_total += stats["total"]
    pass1_valid += stats["valid"]
    pass1_fixed += stats["fixed"]
    pass1_dropped += stats["dropped"]
    pass1_dupes += stats["dupes"]

log(f"\n  PASS 1 TOTALS: {pass1_total} total | {pass1_valid} valid | {pass1_fixed} fixed | {pass1_dropped} dropped | {pass1_dupes} dupes removed")

# --- PASS 2 (verification) ---
log("")
log("=" * 65)
log("  PASS 2: Verification (should be all clean)")
log("=" * 65)
pass2_total = 0
pass2_valid = 0
pass2_issues = 0

for filepath in all_files:
    stats = validate_and_fix(filepath)
    icon = "[OK]" if stats["status"] == "OK" else "[!!]"
    log(f"  {icon} {stats['file']:30s} T:{stats['total']:4d} V:{stats['valid']:4d}")
    pass2_total += stats["total"]
    pass2_valid += stats["valid"]
    if stats["dropped"] > 0 or stats["fixed"] > 0 or stats["dupes"] > 0:
        pass2_issues += 1

log(f"\n  PASS 2 TOTALS: {pass2_total} total | {pass2_valid} valid | Issues: {pass2_issues}")

# --- MERGE ---
log("")
log("=" * 65)
log("  MERGING ALL DATA")
log("=" * 65)
total_merged = 0
with open("all_training_data.jsonl", "w", encoding="utf-8") as out:
    for filepath in all_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                    if all(k in obj for k in REQUIRED_KEYS):
                        out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        total_merged += 1
                except json.JSONDecodeError:
                    pass

merged_size = os.path.getsize("all_training_data.jsonl")
log(f"\n  Merged {total_merged} examples into all_training_data.jsonl")
log(f"  File size: {merged_size:,} bytes ({merged_size/1024/1024:.2f} MB)")

# --- SUMMARY ---
log("")
log("=" * 65)
log("  FINAL SUMMARY")
log("=" * 65)
log(f"  Pass 1: {pass1_valid} valid / {pass1_total} total ({pass1_fixed} fixed, {pass1_dropped} dropped, {pass1_dupes} dupes)")
log(f"  Pass 2: {pass2_valid} valid / {pass2_total} total (issues: {pass2_issues})")
log(f"  Merged: {total_merged} total training examples")

if pass2_issues == 0:
    log("\n  ALL FILES CLEAN - Ready for training!")
else:
    log("\n  WARNING: Issues remain - review output above")
log("")

# Write report
with open("_final_validation_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))
