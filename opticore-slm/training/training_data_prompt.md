# OptiCore SLM — Training Data Generation Prompt

Use the prompt below with **any capable LLM** (GPT-4, Claude, Gemini, etc.) to generate 50 high-quality JSONL fine-tuning examples.

---

## Prompt to Generate 50 JSONL Examples

```
You are a Senior C++ Performance Engineer.

Generate 50 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines).
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code.
   - A brief explanation (2-4 sentences) of WHY it is faster, referencing CPU cache, Big-O, or RAII.

Cover these categories evenly (~8-10 examples each):

Category A — Vectorization / Cache Locality
  - Replace std::list with std::vector.
  - Replace std::deque with std::vector for small types.
  - Replace std::set with sorted std::vector + binary search.
  - Prefer contiguous memory layouts (struct-of-arrays vs array-of-structs).

Category B — Lookup Optimization
  - Replace linear search (for-loop over vector) with std::unordered_map.
  - Replace std::map (O(log N)) with std::unordered_map (O(1)).
  - Replace nested O(N^2) loops with hash-based lookups.
  - Use std::unordered_set for membership checks instead of std::find.

Category C — Memory Safety / RAII
  - Replace raw new/delete with std::unique_ptr.
  - Replace raw new[]/delete[] with std::vector.
  - Replace manual resource management with RAII wrappers.
  - Fix memory leaks from early-return paths.

Category D — Algorithmic Improvements
  - Replace bubble sort with std::sort.
  - Use reserve() before push_back loops.
  - Use emplace_back instead of push_back for complex objects.
  - Use range-based for loops with const references.

Category E — Mixed / Real-World
  - Combine multiple optimizations in one snippet.
  - Optimize a small "game loop" or "data pipeline" function.
  - Fix a function that does redundant copies.

Output ONLY the 50 JSONL lines. No surrounding text, no markdown fences.
```

---

## Format Reference

Each line in the output `.jsonl` file looks like:

```json
{"instruction":"Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why.","input":"#include <list>\n\nvoid process(std::list<int>& data) {\n    for (auto it = data.begin(); it != data.end(); ++it) {\n        *it *= 2;\n    }\n}","output":"#include <vector>\n\nvoid process(std::vector<int>& data) {\n    for (auto& val : data) {\n        val *= 2;\n    }\n}\n---\nstd::vector stores elements contiguously in memory, enabling CPU cache-line prefetching. std::list allocates each node separately on the heap, causing cache misses on every traversal. For sequential iteration this swap alone can yield 5-10x speedup."}
```

## How to Use

1. Paste the prompt above into any LLM.
2. Save the raw output as `training_data.jsonl`.
3. Validate with: `python -c "import json; [json.loads(l) for l in open('training_data.jsonl')]"`
4. Fine-tune with Hugging Face `SFTTrainer` or `Unsloth`.
