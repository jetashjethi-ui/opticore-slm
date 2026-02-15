"""Fix all JSONL batch files by cleaning URLs and escaping unescaped quotes."""
import json
import re
import os

def clean_urls(line):
    """Remove hallucinated Google search URLs that replaced std:: types."""
    line = re.sub(r'\[([^\]]*?)\]\(https?://[^\)]*?\)', r'\1', line)
    line = line.replace('https://www.google.com/search?q=', '')
    return line

def escape_inner_quotes(s):
    """Escape unescaped double quotes inside a JSON string value."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            result.append(s[i])
            result.append(s[i+1])
            i += 2
        elif s[i] == '"':
            result.append('\\"')
            i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

def fix_line(raw_line):
    """Attempt to fix a broken JSONL line."""
    line = raw_line.strip()
    if not line:
        return None

    # Try as-is
    try:
        obj = json.loads(line)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        pass

    # Clean URLs
    line = clean_urls(line)
    try:
        obj = json.loads(line)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        pass

    # Manual key-boundary parsing - support multiple prefix formats
    prefixes = [
        '{"instruction": "',
        '{ "instruction": "',
        '{"instruction":"',
    ]
    
    matched_prefix = None
    for p in prefixes:
        if line.startswith(p):
            matched_prefix = p
            break
    
    if not matched_prefix:
        return None
    
    suffixes = ['"}', '" }']
    matched_suffix = None
    for s in suffixes:
        if line.endswith(s):
            matched_suffix = s
            break
    
    if not matched_suffix:
        return None

    input_markers = ['", "input": "', '","input":"', '", "input":"', '","input": "']
    output_markers = ['", "output": "', '","output":"', '", "output":"', '","output": "']

    after_instr = line[len(matched_prefix):]

    # Find input marker
    input_idx = -1
    used_input_marker = None
    for marker in input_markers:
        idx = after_instr.find(marker)
        if idx != -1:
            input_idx = idx
            used_input_marker = marker
            break
    
    if input_idx == -1:
        return None

    instr_val = after_instr[:input_idx]
    after_input = after_instr[input_idx + len(used_input_marker):]

    # Find output marker
    output_idx = -1
    used_output_marker = None
    for marker in output_markers:
        idx = after_input.find(marker)
        if idx != -1:
            output_idx = idx
            used_output_marker = marker
            break
    
    if output_idx == -1:
        return None

    input_val = after_input[:output_idx]
    output_val = after_input[output_idx + len(used_output_marker):-len(matched_suffix)]

    fixed = (
        '{"instruction": "' + escape_inner_quotes(instr_val) +
        '", "input": "' + escape_inner_quotes(input_val) +
        '", "output": "' + escape_inner_quotes(output_val) + '"}'
    )

    try:
        obj = json.loads(fixed)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        return None

def process_file(filepath):
    """Process a single JSONL file. Returns (ok, fixed, failed)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    output_lines = []
    ok = 0
    fixed = 0
    failed = 0

    for ln, raw in enumerate(raw_lines, 1):
        raw = raw.strip()
        if not raw:
            continue

        try:
            json.loads(raw)
            output_lines.append(raw)
            ok += 1
            continue
        except json.JSONDecodeError:
            pass

        result = fix_line(raw)
        if result:
            output_lines.append(result)
            fixed += 1
        else:
            output_lines.append(raw)
            failed += 1
            print(f"  FAILED: {os.path.basename(filepath)} L{ln}")

    with open(filepath, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')

    return ok, fixed, failed

def main():
    files = ['sample_training_data.jsonl'] + [f'batch_{i:02d}.jsonl' for i in range(1, 11)]
    
    total_fixed = 0
    total_failed = 0
    results = []

    for fname in files:
        if not os.path.exists(fname):
            results.append(f'{fname}: NOT FOUND')
            continue
        if os.path.getsize(fname) == 0:
            results.append(f'{fname}: EMPTY')
            continue
        
        ok, fixed, failed = process_file(fname)
        total_fixed += fixed
        total_failed += failed
        total = ok + fixed + failed
        status = 'ALL OK' if failed == 0 else f'{failed} STILL BROKEN'
        results.append(f'{fname}: {total} examples ({ok} ok, {fixed} fixed, {failed} failed) - {status}')

    results.append(f'\nTOTAL FIXED: {total_fixed}, STILL BROKEN: {total_failed}')
    
    report = '\n'.join(results)
    print(report)
    
    with open('fix_all_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == '__main__':
    main()
