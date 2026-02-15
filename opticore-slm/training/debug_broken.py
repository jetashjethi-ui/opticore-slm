import json

# Look at broken lines to understand formatting patterns
files_lines = [('batch_01.jsonl', 34), ('batch_06.jsonl', 1), ('batch_03.jsonl', 4)]
with open('broken_samples.txt', 'w', encoding='utf-8') as out:
    for fname, target_ln in files_lines:
        with open(fname, 'r', encoding='utf-8') as f:
            for ln, line in enumerate(f, 1):
                if ln == target_ln:
                    s = line.strip()
                    out.write(f'=== {fname} L{ln} (len={len(s)}) ===\n')
                    out.write(f'FIRST 500: {repr(s[:500])}\n\n')
                    # Check various key patterns
                    patterns = [
                        '"instruction": "',
                        '"instruction":"',
                        '", "input": "',
                        '","input":"',
                        '","input": "',
                        '", "input":"',
                        '", "output": "',
                        '","output":"',
                        '","output": "',
                        '", "output":"',
                    ]
                    for pat in patterns:
                        if pat in s:
                            out.write(f'  FOUND: {repr(pat)}\n')
                    out.write('\n')
                    break

print('done')
