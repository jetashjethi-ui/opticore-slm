# OptiCore SLM — Algorithm Optimization Training Data Prompt

Use this prompt **separately for EACH category** below. Run it with GPT-4 / Claude / Gemini.
Generate **50 examples per run × 60 runs = 3,000 examples**.

---

## Master Prompt (copy-paste into any LLM)

Replace `[CATEGORY_BLOCK]` with ONE category section at a time from below.

```
You are a Senior C++ Algorithm & Performance Engineer.

Generate 50 JSONL training examples for fine-tuning a code optimization model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

STRICT RULES:
1. "instruction" must be EXACTLY: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a COMPLETE, compilable C++ snippet (10-40 lines) showing an UNOPTIMIZED approach.
3. "output" contains TWO parts separated by "---":
   - Part 1: The COMPLETE, CORRECT, COMPILABLE optimized C++ code. NO pseudocode. NO placeholders.
   - Part 2: A 2-4 sentence explanation of WHY it is faster, with Big-O improvement and technical reason.

CODE QUALITY RULES:
- All code MUST compile with g++ -std=c++17
- Include necessary #include headers
- Use proper variable names (not just a,b,c)
- Show realistic function signatures
- The optimized code MUST be CORRECT — same output as the original
- DO NOT invent fake functions or libraries
- DO NOT use "..." or "// rest of code" placeholders

JSON RULES:
- Use \n for newlines inside strings, \t for tabs
- Escape all quotes inside strings with \"
- Each line must be valid JSON — no trailing commas
- No markdown fences — output RAW JSONL only

[CATEGORY_BLOCK]

Output ONLY the 50 JSONL lines. No other text.
```

---

## Category Blocks (replace [CATEGORY_BLOCK] with ONE of these)

### Category 1 — Sorting Algorithm Optimization (run 6 times = 300 examples)

```
Cover these sorting optimizations, ~8-10 each sub-type:

1a. Bubble Sort → std::sort or std::stable_sort
1b. Selection Sort → std::partial_sort or nth_element
1c. Counting Sort approach for small-range integers (0-2 range → Dutch National Flag / 3-way partition)
1d. Sort 0s, 1s, 2s → Dutch National Flag algorithm (three pointers: low, mid, high)
1e. Custom comparator sorts (sorting structs/objects by multiple fields)
1f. Insertion sort on nearly-sorted data → Tim Sort awareness / std::sort

IMPORTANT for 1c and 1d: The Dutch National Flag algorithm uses THREE pointers (low=0, mid=0, high=n-1):
- If arr[mid]==0: swap(arr[low], arr[mid]), low++, mid++
- If arr[mid]==1: mid++
- If arr[mid]==2: swap(arr[mid], arr[high]), high--
Show this EXACT algorithm in the optimized output. It achieves O(n) single-pass sorting.
```

### Category 2 — Two-Pointer & Binary Search (run 6 times = 300 examples)

```
Cover these search/pointer optimizations:

2a. Linear search → Binary search (sorted arrays)
2b. Two nested loops finding pairs → Two-pointer technique
2c. Finding duplicates with O(n²) → hash set O(n) or sorting + adjacent check
2d. Merging two sorted arrays with extra space → in-place two-pointer merge
2e. Removing duplicates from sorted array → two-pointer in-place
2f. Finding target sum pair → sort + two-pointer O(n log n) or hash O(n)
```

### Category 3 — Sliding Window (run 6 times = 300 examples)

```
Cover these sliding window patterns:

3a. Max/min subarray sum of size K → fixed-size sliding window
3b. Longest substring without repeating chars → variable sliding window with hash set
3c. Brute force all subarrays → sliding window O(n)
3d. Count subarrays with sum ≤ target → sliding window with running sum
3e. Maximum of all windows of size K → deque-based sliding window
3f. Smallest subarray with sum ≥ target → variable window shrinking
```

### Category 4 — Dynamic Programming (run 6 times = 300 examples)

```
Cover these DP optimizations:

4a. Recursive Fibonacci → Memoized → Tabulated O(n)
4b. Recursive coin change → DP table
4c. Brute force longest common subsequence → DP table
4d. Recursive knapsack → DP with 2D/1D table
4e. Recursive path counting (grid) → DP table
4f. Recursive edit distance → DP optimization
```

### Category 5 — Graph Algorithms (run 6 times = 300 examples)

```
Cover these graph optimizations:

5a. Adjacency matrix → Adjacency list for sparse graphs
5b. Recursive DFS without visited check → proper DFS with visited set
5c. Naive shortest path → BFS for unweighted / Dijkstra for weighted
5d. Detecting cycles with brute force → DFS coloring / Union-Find
5e. Naive connected components → BFS/DFS-based component finding
5f. All-pairs brute force → Floyd-Warshall or batch-Dijkstra
```

### Category 6 — String Algorithms (run 4 times = 200 examples)

```
Cover these string optimizations:

6a. Brute force substring search O(n*m) → KMP O(n+m) or find()
6b. Checking anagrams with sorting → frequency array comparison
6c. Brute force palindrome check → two-pointer from ends
6d. Repeated string concatenation with + → std::ostringstream or reserve()
6e. Character frequency counting with map → array[26] for lowercase
```

### Category 7 — Tree & Heap Patterns (run 6 times = 300 examples)

```
Cover these tree/heap optimizations:

7a. Finding Kth largest with full sort → std::nth_element or min-heap of size K
7b. Naive BST operations without balancing awareness → std::set/std::map
7c. Linear scan for min/max repeatedly → priority_queue (heap)
7d. Building BST from sorted array → balanced BST construction
7e. Repeated find-min + delete → std::priority_queue
7f. Level-order traversal with recursion → BFS with queue
```

### Category 8 — Prefix Sum & Range Queries (run 4 times = 200 examples)

```
Cover these optimizations:

8a. Repeated subarray sum queries O(n) each → prefix sum array O(1) per query
8b. 2D submatrix sum → 2D prefix sum
8c. Count elements in range with loop → prefix count array
8d. Running average calculation → cumulative sum approach
8e. Difference array for range update operations
```

### Category 9 — Greedy Algorithms (run 4 times = 200 examples)

```
Cover these greedy optimizations:

9a. Brute force activity selection → greedy sort-by-end
9b. Making change with brute force → greedy coin selection (when valid)
9c. Brute force interval scheduling → greedy interval merging
9d. Huffman encoding vs fixed-length encoding
9e. Minimum platforms/rooms → event sorting with greedy scan
```

### Category 10 — Bit Manipulation & Math (run 4 times = 200 examples)

```
Cover these optimizations:

10a. Checking power of 2 with loop → n & (n-1) == 0
10b. Counting set bits with loop → __builtin_popcount
10c. Multiply/divide by powers of 2 → bit shift
10d. Finding single non-duplicate → XOR all elements
10e. Checking even/odd with modulo → & 1
10f. Swapping without temp → XOR swap or std::swap
```

---

## Workflow

1. Copy the Master Prompt
2. Replace `[CATEGORY_BLOCK]` with Category 1 block
3. Paste into GPT-4/Claude → save output as `algo_batch_01.jsonl`
4. Repeat for ALL 60 runs (6 per category for 300-example categories, 4 per for 200-example categories)
5. Validate: `python validate_all.py`
6. Merge: Update `merge_data.py` to include `algo_batch_*.jsonl`
7. Retrain: `python train_sft.py`
8. Export: `python export_gguf_manual.py`
