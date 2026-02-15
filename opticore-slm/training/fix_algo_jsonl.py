"""
Fix all algo_batch JSONL files — repairs common JSON errors:
1. Invalid \\escape sequences (\\s, \\i, \\p, etc.)
2. Missing commas / extra data
3. Unescaped quotes inside strings
Saves fixed files in-place with backup.
"""
import json
import os
import re
import shutil

files = sorted([f for f in os.listdir('.') if f.startswith('algo_batch_') and f.endswith('.jsonl')])
print(f"Found {len(files)} algo_batch files to fix\n")

total_fixed = 0
total_skipped = 0
total_ok = 0

for fname in files:
    # Create backup
    backup = fname + '.bak'
    shutil.copy2(fname, backup)
    
    fixed_lines = []
    fixed_count = 0
    skipped_count = 0
    ok_count = 0
    
    with open(fname, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Try parsing as-is first
            try:
                obj = json.loads(stripped)
                if all(k in obj for k in ['instruction', 'input', 'output']):
                    fixed_lines.append(json.dumps(obj, ensure_ascii=False))
                    ok_count += 1
                    continue
            except json.JSONDecodeError:
                pass
            
            # --- Attempt repairs ---
            repaired = stripped
            
            # Fix 1: Replace invalid escape sequences
            # Common: \s, \i, \p, \c, \a, \e, \d, \f (when not \n, \t, \r, \\, \", \/)
            # We need to be careful not to break valid escapes
            valid_escapes = set('ntrbu"\\/f')
            result = []
            i = 0
            while i < len(repaired):
                if repaired[i] == '\\' and i + 1 < len(repaired):
                    next_char = repaired[i + 1]
                    if next_char in valid_escapes:
                        result.append(repaired[i])
                        result.append(repaired[i + 1])
                        i += 2
                    elif next_char == '\\':
                        result.append('\\\\')
                        i += 2
                    else:
                        # Invalid escape like \s, \i, \p — replace with \\\\+char
                        result.append('\\\\')
                        result.append(next_char)
                        i += 2
                else:
                    result.append(repaired[i])
                    i += 1
            repaired = ''.join(result)
            
            # Fix 2: Try to fix "Extra data" — might be two JSON objects on one line
            try:
                obj = json.loads(repaired)
                if all(k in obj for k in ['instruction', 'input', 'output']):
                    fixed_lines.append(json.dumps(obj, ensure_ascii=False))
                    fixed_count += 1
                    continue
            except json.JSONDecodeError as e:
                if 'Extra data' in str(e):
                    # Try splitting at }{ boundary
                    parts = re.split(r'\}\s*\{', repaired)
                    for idx, part in enumerate(parts):
                        p = part
                        if not p.startswith('{'): p = '{' + p
                        if not p.endswith('}'): p = p + '}'
                        try:
                            obj = json.loads(p)
                            if all(k in obj for k in ['instruction', 'input', 'output']):
                                fixed_lines.append(json.dumps(obj, ensure_ascii=False))
                                fixed_count += 1
                        except json.JSONDecodeError:
                            pass
                    continue
            
            # Fix 3: Try to find and fix unescaped quotes in values
            # This is a more aggressive repair
            try:
                # Try wrapping problematic parts
                repaired2 = repaired
                # Fix common pattern: missing comma between key-value pairs
                repaired2 = re.sub(r'"\s*"(instruction|input|output)"', r'", "\1"', repaired2)
                obj = json.loads(repaired2)
                if all(k in obj for k in ['instruction', 'input', 'output']):
                    fixed_lines.append(json.dumps(obj, ensure_ascii=False))
                    fixed_count += 1
                    continue
            except json.JSONDecodeError:
                pass
            
            # Could not fix — skip this line
            skipped_count += 1
    
    # Write fixed file
    with open(fname, 'w', encoding='utf-8') as f:
        for line in fixed_lines:
            f.write(line + '\n')
    
    total_fixed += fixed_count
    total_skipped += skipped_count
    total_ok += ok_count
    
    print(f"  {fname}: {ok_count} OK, {fixed_count} fixed, {skipped_count} unfixable (backup: {backup})")

print(f"\n{'='*50}")
print(f"  TOTAL OK:        {total_ok}")
print(f"  TOTAL FIXED:     {total_fixed}")
print(f"  TOTAL SKIPPED:   {total_skipped}")
print(f"  TOTAL KEPT:      {total_ok + total_fixed}")
print(f"{'='*50}")
