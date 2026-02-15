import json

with open('batch_06.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if not stripped:
        new_lines.append(line)
        continue
    try:
        json.loads(stripped)
        new_lines.append(line)
    except json.JSONDecodeError:
        print(f'Broken at line {i+1}')
        # Build correct JSON
        obj = {
            "instruction": "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why.",
            "input": "#include <fstream>\n#include <string>\n\nvoid read_word_by_word() {\n    std::ifstream in(\"text.txt\");\n    std::string s;\n    while(in >> s) {\n        // process\n    }\n}",
            "output": "#include <fstream>\n#include <string>\n#include <vector>\n\nvoid read_word_by_word() {\n    std::ifstream in(\"text.txt\", std::ios::binary | std::ios::ate);\n    size_t sz = in.tellg();\n    in.seekg(0);\n    std::string content(sz, '\\0');\n    in.read(&content[0], sz);\n}\n---Formatted extraction (>>) mixes I/O with parsing. Reading the whole file into memory and then parsing avoids stalling the CPU on disk reads."
        }
        new_lines.append(json.dumps(obj, ensure_ascii=False) + '\n')
        print('Fixed!')

with open('batch_06.jsonl', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Saved')
