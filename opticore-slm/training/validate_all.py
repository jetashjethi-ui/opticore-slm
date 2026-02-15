import json, os

results = []
all_files = ['sample_training_data.jsonl'] + [f'batch_{i:02d}.jsonl' for i in range(1, 11)]
total_examples = 0
total_errors = 0

for fname in all_files:
    if not os.path.exists(fname):
        results.append(f'{fname}: FILE NOT FOUND')
        continue
    sz = os.path.getsize(fname)
    count = 0
    errs = []
    with open(fname, 'r', encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                obj = json.loads(line)
                for k in ['instruction', 'input', 'output']:
                    if k not in obj:
                        errs.append(f'L{ln}: Missing key "{k}"')
            except json.JSONDecodeError as e:
                errs.append(f'L{ln} col{e.colno}: {e.msg}')
    total_examples += count
    total_errors += len(errs)
    status = 'OK' if not errs else f'{len(errs)} ERRORS'
    if count == 0:
        status = 'EMPTY'
    results.append(f'{fname}: {count} examples, {sz} bytes - {status}')
    for err in errs:
        results.append(f'  {err}')

results.append('')
results.append(f'TOTAL: {total_examples} examples, {total_errors} errors')

report = '\n'.join(results)
with open('full_validation.txt', 'w', encoding='utf-8') as f:
    f.write(report)
print(report)
