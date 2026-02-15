"""Fix broken JSONL lines in batch_10.jsonl by re-reading the original and 
properly escaping unescaped quotes inside JSON string values."""

import json
import re
import sys
import os

# First, restore original batch_10.jsonl if we have a backup
# (we may have partially overwritten it in a failed attempt)

INPUT_FILE = "batch_10.jsonl"
OUTPUT_FILE = "batch_10_fixed.jsonl"

def clean_urls(line):
    """Remove hallucinated Google search URLs that replaced std:: types."""
    # Replace [type](url) markdown links with just type
    line = re.sub(r'\[([^\]]*?)\]\(https?://[^\)]*?\)', r'\1', line)
    # Replace bare URLs like https://www.google.com/search?q=std::string
    line = line.replace('https://www.google.com/search?q=', '')
    return line

def fix_line(raw_line):
    """Attempt to fix a broken JSONL line."""
    line = raw_line.strip()
    if not line:
        return None
    
    # Try as-is first
    try:
        obj = json.loads(line)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
    
    # Step 1: Clean URLs
    line = clean_urls(line)
    
    # Try again after URL cleanup
    try:
        obj = json.loads(line)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
    
    # Step 2: Manual parsing - find the three key-value boundaries
    # The structure is: {"instruction": "...", "input": "...", "output": "..."}
    
    # Find the three section markers
    instr_prefix = '{"instruction": "'
    input_marker = '", "input": "'
    output_marker = '", "output": "'
    suffix = '"}'
    
    if not line.startswith(instr_prefix) or not line.endswith(suffix):
        return None
    
    # Extract instruction value
    after_instr = line[len(instr_prefix):]
    
    # Find input marker - it should be the FIRST occurrence of the pattern
    input_idx = after_instr.find(input_marker)
    if input_idx == -1:
        return None
    
    instr_val = after_instr[:input_idx]
    after_input = after_instr[input_idx + len(input_marker):]
    
    # Find output marker
    output_idx = after_input.find(output_marker)
    if output_idx == -1:
        return None
    
    input_val = after_input[:output_idx]
    output_val = after_input[output_idx + len(output_marker):-len(suffix)]
    
    # Now escape any unescaped double quotes within the values
    # But we need to preserve already-escaped sequences like \\n, \\t, etc.
    def escape_quotes(s):
        # Replace unescaped " with \"
        # A quote is unescaped if not preceded by \
        result = []
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                # Already an escape sequence, keep it
                result.append(s[i])
                result.append(s[i+1])
                i += 2
            elif s[i] == '"':
                # Unescaped quote - escape it
                result.append('\\"')
                i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)
    
    instr_escaped = escape_quotes(instr_val)
    input_escaped = escape_quotes(input_val)
    output_escaped = escape_quotes(output_val)
    
    fixed = '{"instruction": "' + instr_escaped + '", "input": "' + input_escaped + '", "output": "' + output_escaped + '"}'
    
    try:
        obj = json.loads(fixed)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError as e:
        print(f"  Still broken: {e}", file=sys.stderr)
        return None


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()
    
    fixed_lines = []
    fixed_count = 0
    failed_count = 0
    ok_count = 0
    
    for ln, raw in enumerate(raw_lines, 1):
        raw = raw.strip()
        if not raw:
            continue
        
        # Check if already valid
        try:
            json.loads(raw)
            fixed_lines.append(raw)
            ok_count += 1
            continue
        except json.JSONDecodeError:
            pass
        
        result = fix_line(raw)
        if result:
            fixed_lines.append(result)
            fixed_count += 1
            print(f"  L{ln}: FIXED")
        else:
            # Keep original (broken) line
            fixed_lines.append(raw)
            failed_count += 1
            print(f"  L{ln}: FAILED TO FIX")
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in fixed_lines:
            f.write(line + '\n')
    
    print(f"\nResults:")
    print(f"  Already valid: {ok_count}")
    print(f"  Fixed: {fixed_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total written: {len(fixed_lines)}")
    
    # Verify output
    errors = 0
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                print(f"  Verification error at L{ln}")
    
    print(f"\nVerification: {errors} errors in output file")
    
    if errors == 0:
        # Replace original with fixed version
        os.replace(OUTPUT_FILE, INPUT_FILE)
        print(f"Replaced {INPUT_FILE} with fixed version")

if __name__ == '__main__':
    main()
