"""
Comprehensive JSONL Validator & Fixer for OptiCore Training Data.
- Validates and fixes ALL batch files
- Fixes: unescaped quotes, invalid JSON, missing fields, hallucinated URLs
- Runs TWO full validation passes
- Merges all data into all_training_data.jsonl
"""
import os
import json
import glob
import re
import sys
import time

TRAINING_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(TRAINING_DIR)

REQUIRED_KEYS = {"instruction", "input", "output"}

def remove_hallucinated_urls(text):
    text = re.sub(r'\[Source\]\(https?://[^\)]+\)', '', text)
    text = re.sub(r'\(https?://[^\)]+\)', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

def try_parse_line(line):
    line = line.strip()
    if not line:
        return None, "empty"
    try:
        obj = json.loads(line)
        return obj, None
    except json.JSONDecodeError:
        pass
    fixed = line.replace('\t', '\\t')
    try:
        obj = json.loads(fixed)
        return obj, "fixed_tabs"
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{.*\}', line, re.DOTALL)
    if match:
        try:
            obj = json.loads(match.group())
            return obj, "extracted"
        except json.JSONDecodeError:
            pass
    return None, "unparseable"

def validate_entry(obj):
    issues = []
    if not isinstance(obj, dict):
        return False, ["not a dict"]
    missing = REQUIRED_KEYS - set(obj.keys())
    if missing:
        issues.append(f"missing keys: {missing}")
    for key in ["instruction", "input", "output"]:
        if key in obj:
            val = obj[key]
            if not isinstance(val, str):
                issues.append(f"{key} is not a string")
            elif len(val.strip()) == 0:
                issues.append(f"{key} is empty")
    if "output" in obj and isinstance(obj["output"], str):
        if re.search(r'https?://', obj["output"]):
            issues.append("output contains URL")
    return len(issues) == 0, issues

def process_file(filepath):
    if not os.path.exists(filepath):
        return {"file": filepath, "status": "NOT_FOUND", "total": 0, "valid": 0, "fixed": 0, "dropped": 0, "issues": []}

    basename = os.path.basename(filepath)
    valid_entries = []
    stats = {"file": basename, "status": "OK", "total": 0, "valid": 0, "fixed": 0, "dropped": 0, "issues": []}

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            stats["total"] += 1
            obj, parse_status = try_parse_line(stripped)
            if obj is None:
                stats["dropped"] += 1
                stats["issues"].append(f"  Line {line_num}: {parse_status}")
                continue
            if parse_status and parse_status != "empty":
                stats["fixed"] += 1
            is_valid, issues = validate_entry(obj)
            if not is_valid:
                if "missing keys" in str(issues):
                    stats["dropped"] += 1
                    stats["issues"].append(f"  Line {line_num}: {issues}")
                    continue
            if "output" in obj and isinstance(obj["output"], str):
                original = obj["output"]
                cleaned = remove_hallucinated_urls(original)
                if cleaned != original:
                    obj["output"] = cleaned
                    stats["fixed"] += 1
            is_valid, issues = validate_entry(obj)
            if is_valid:
                stats["valid"] += 1
                valid_entries.append(obj)
            else:
                stats["dropped"] += 1
                stats["issues"].append(f"  Line {line_num}: {issues}")

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
                print(f"  [ERR] Could not write {basename} after 3 attempts (file locked)")
                stats["status"] = "WRITE_ERROR"

    if stats["dropped"] > 0 or stats["fixed"] > 0:
        stats["status"] = "FIXED"
    return stats

def run_validation_pass(files, pass_num):
    print(f"\n{'='*60}")
    print(f"  VALIDATION PASS {pass_num}")
    print(f"{'='*60}")
    
    total_entries = 0
    total_valid = 0
    total_fixed = 0
    total_dropped = 0

    for filepath in files:
        stats = process_file(filepath)
        total_entries += stats["total"]
        total_valid += stats["valid"]
        total_fixed += stats["fixed"]
        total_dropped += stats["dropped"]

        if stats["status"] == "OK":
            icon = "[OK]"
        elif stats["status"] == "FIXED":
            icon = "[FX]"
        elif stats["status"] == "NOT_FOUND":
            icon = "[NF]"
        else:
            icon = "[??]"

        print(f"  {icon} {stats['file']:30s} | Total: {stats['total']:4d} | Valid: {stats['valid']:4d} | Fixed: {stats['fixed']:2d} | Dropped: {stats['dropped']:2d}")
        if stats["issues"]:
            for issue in stats["issues"][:3]:
                print(f"     {issue}")

    print(f"\n  {'-'*55}")
    print(f"  PASS {pass_num} TOTALS: {total_entries} entries | {total_valid} valid | {total_fixed} fixed | {total_dropped} dropped")
    return total_entries, total_valid, total_fixed, total_dropped

def merge_all(files, output_file="all_training_data.jsonl"):
    total = 0
    with open(output_file, "w", encoding="utf-8") as out:
        for filepath in files:
            if not os.path.exists(filepath):
                continue
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        obj = json.loads(stripped)
                        if all(k in obj for k in REQUIRED_KEYS):
                            out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                            total += 1
                    except json.JSONDecodeError:
                        pass
    return total

if __name__ == "__main__":
    batch_files = [f"batch_{i:02d}.jsonl" for i in range(1, 11)]
    algo_files = sorted(glob.glob("algo_batch_*.jsonl"))
    algo_files = [f for f in algo_files if not f.endswith(".bak")]
    all_files = ["sample_training_data.jsonl"] + batch_files + algo_files

    print("=" * 60)
    print("  OptiCore Training Data - Validate, Fix & Merge")
    print("=" * 60)
    print(f"\nFound {len(all_files)} input files:")
    for f in all_files:
        exists = "[Y]" if os.path.exists(f) else "[N]"
        size = os.path.getsize(f) if os.path.exists(f) else 0
        print(f"  {exists} {f:40s} ({size:>10,} bytes)")

    # Pass 1
    e1, v1, f1, d1 = run_validation_pass(all_files, 1)
    # Pass 2
    e2, v2, f2, d2 = run_validation_pass(all_files, 2)

    # Merge
    print(f"\n{'='*60}")
    print(f"  MERGING ALL DATA")
    print(f"{'='*60}")
    total_merged = merge_all(all_files)
    merged_size = os.path.getsize("all_training_data.jsonl")
    print(f"\n  Merged {total_merged} examples into all_training_data.jsonl")
    print(f"  File size: {merged_size:,} bytes ({merged_size/1024/1024:.2f} MB)")

    # Summary
    print(f"\n{'='*60}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"  Pass 1: {v1} valid / {e1} total ({f1} fixed, {d1} dropped)")
    print(f"  Pass 2: {v2} valid / {e2} total ({f2} fixed, {d2} dropped)")
    print(f"  Merged: {total_merged} total training examples")
    
    if d2 == 0 and f2 == 0:
        print(f"\n  ALL FILES CLEAN - Ready for training on the 5060!")
    else:
        print(f"\n  WARNING: Issues remain after pass 2 - review output above")
    print()
