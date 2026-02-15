# OptiCore SLM — Comprehensive Training Data (1000 Examples)

## Strategy

Since LLMs have output limits, generate the data in **10 batches of 100 examples each**. Paste the corresponding prompt batch into GPT-4/Claude/Gemini, save each output, then combine them into one file.

After generating all batches, combine them:
```bash
cat batch_*.jsonl > full_training_data.jsonl
```

Validate the combined file:
```bash
python -c "import json; lines=[json.loads(l) for l in open('full_training_data.jsonl')]; print(f'{len(lines)} examples loaded successfully')"
```

---

## BATCH 1: Data Structures & Cache Locality (100 examples)

Save output as `batch_01.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique and different from all others.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster, referencing CPU cache, Big-O, memory layout, or hardware behavior.

Cover these subcategories evenly (~10 examples each):

1. Replace std::list with std::vector for iteration-heavy code
2. Replace std::deque with std::vector when only push_back is used
3. Replace std::map with std::unordered_map for key-value lookups
4. Replace std::set with std::unordered_set for membership checks
5. Replace std::map with sorted std::vector + binary_search for static data
6. Replace nested std::vector<std::vector<T>> with flat 1D vector (row-major access)
7. Struct-of-Arrays (SoA) vs Array-of-Structs (AoS) for SIMD-friendly data
8. Replace std::forward_list with std::vector
9. Replace pointer-based linked lists with std::vector
10. Use std::array instead of C-style arrays for fixed-size data

Vary the code contexts: game engines, physics simulations, data processing pipelines, network buffers, image processing, financial systems, scientific computing, embedded systems, compilers, databases.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 2: Algorithm Optimization (100 examples)

Save output as `batch_02.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster.

Cover these subcategories evenly (~10 examples each):

1. Replace bubble/selection/insertion sort with std::sort (O(N²) → O(N log N))
2. Replace linear search with std::binary_search on sorted data (O(N) → O(log N))
3. Replace O(N²) nested loops with hash-based O(N) approaches
4. Replace recursive algorithms with iterative equivalents (stack space savings)
5. Use divide-and-conquer where brute force is used
6. Replace repeated std::find with a single hash set build + lookup
7. Use prefix sums / running totals instead of recomputing sums
8. Use two-pointer technique instead of nested loops
9. Use std::nth_element instead of full sort when only partial order is needed
10. Use std::partial_sort instead of full sort when only top-K elements are needed

Use realistic contexts: searching logs, processing sensor data, game pathfinding, sorting leaderboards, finding duplicates in arrays, frequency counting, sliding window problems, matrix operations, graph traversals, string processing.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 3: Memory Management & RAII (100 examples)

Save output as `batch_03.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is safer/faster.

Cover these subcategories evenly (~10 examples each):

1. Replace raw new/delete with std::unique_ptr
2. Replace raw new[]/delete[] with std::vector
3. Replace manual resource management (FILE*, sockets) with RAII wrappers
4. Fix memory leaks from early-return or exception paths using smart pointers
5. Replace shared ownership raw pointers with std::shared_ptr
6. Use std::make_unique/std::make_shared instead of raw new in smart pointers
7. Fix double-free / dangling pointer bugs with RAII
8. Replace C-style malloc/free with C++ containers
9. Use std::string instead of char* with manual memory management
10. Implement Rule of Zero by replacing manual destructors with containers/smart pointers

Contexts: file I/O, database connections, GUI widgets, network sockets, audio buffers, texture loading, plugin systems, thread management, hardware resources, parser implementations.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 4: Move Semantics & Copy Elimination (100 examples)

Save output as `batch_04.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster.

Cover these subcategories evenly (~10 examples each):

1. Pass large objects by const reference instead of by value
2. Use std::move when transferring ownership of containers/strings
3. Use emplace_back instead of push_back to construct in-place
4. Avoid unnecessary string copies with std::string_view (C++17)
5. Return by value with RVO/NRVO instead of output parameters
6. Use reserve() before push_back loops to avoid reallocations
7. Avoid redundant temporary objects in expressions
8. Use initializer lists instead of repeated push_back
9. Use insert(range) instead of loop + push_back for bulk insertion
10. Eliminate copies in range-based for loops (auto& vs auto)

Contexts: string processing, container manipulation, matrix math, JSON parsing, configuration loading, serialization, message passing, event handling, data transformation pipelines, building trees/graphs.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 5: Concurrency & Threading (100 examples)

Save output as `batch_05.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster/safer.

Cover these subcategories evenly (~10 examples each):

1. Replace mutex-protected counter with std::atomic
2. Use std::lock_guard / std::scoped_lock instead of manual lock/unlock
3. Reduce lock scope (move work outside critical section)
4. Replace global mutex with thread-local storage
5. Use std::async / std::future for simple parallelism
6. Replace busy-wait loops with condition_variable
7. Use read-write locks (std::shared_mutex) for read-heavy data
8. Avoid false sharing with cache-line aligned data
9. Use lock-free data structures where applicable
10. Replace single-threaded loops with std::for_each(std::execution::par, ...)

Contexts: web servers, game engines, producer-consumer queues, logging systems, connection pools, task schedulers, parallel data processing, signal handling, timer systems, work stealing.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 6: I/O & String Optimization (100 examples)

Save output as `batch_06.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster.

Cover these subcategories evenly (~10 examples each):

1. Replace std::endl with '\n' (avoid unnecessary flush)
2. Use std::ios_base::sync_with_stdio(false) for faster cin/cout
3. Use string::reserve before repeated concatenation
4. Use std::ostringstream or fmt::format instead of repeated string += 
5. Use std::string_view for read-only string parameters
6. Use buffered file I/O instead of character-by-character reading
7. Use getline() + parse instead of formatted extraction for CSV/log parsing
8. Avoid substr() copies — use string_view::substr instead
9. Use printf/fmt over iostream for high-throughput logging
10. Use memory-mapped files (mmap) instead of read() for large files

Contexts: log file parsers, CSV readers, config file loaders, HTTP request parsers, serialization, template engines, report generators, command-line tools, text editors, compiler tokenizers.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 7: Loop & Computation Optimization (100 examples)

Save output as `batch_07.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster.

Cover these subcategories evenly (~10 examples each):

1. Hoist invariant computations out of loops (loop-invariant code motion)
2. Cache .size() calls in loop conditions
3. Fix column-major vs row-major matrix traversal for cache efficiency
4. Replace division with multiplication by reciprocal in hot loops
5. Use loop unrolling / strength reduction patterns
6. Avoid branching in tight loops (use branchless techniques, conditional moves)
7. Use constexpr / compile-time computation for constant expressions
8. Replace virtual function calls in hot loops with CRTP or templates
9. Use std::transform / std::accumulate instead of manual loops
10. Avoid recomputing values — use memoization or lookup tables

Contexts: physics simulations, image processing kernels, signal processing, financial calculations, Monte Carlo simulations, ray tracing, audio processing, scientific computing, pathfinding, compression algorithms.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 8: Modern C++ Patterns (100 examples)

Save output as `batch_08.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is better.

Cover these subcategories evenly (~10 examples each):

1. Replace C-style casts with static_cast/dynamic_cast for type safety
2. Use enum class instead of plain enum to prevent implicit conversions
3. Use std::optional instead of sentinel values or nullptr returns
4. Use std::variant instead of unsafe unions or type-erased void*
5. Use structured bindings (auto [k, v]) for cleaner map iteration
6. Use if-constexpr for compile-time branching instead of runtime if
7. Replace function pointer callbacks with std::function or templates
8. Use CTAD (Class Template Argument Deduction) for cleaner syntax
9. Use [[nodiscard]], [[likely]], [[unlikely]] attributes appropriately
10. Use concepts (C++20) to constrain templates instead of SFINAE

Contexts: generic libraries, type-safe APIs, configuration systems, state machines, visitor patterns, factory methods, plugin architectures, serialization frameworks, error handling, metaprogramming utilities.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 9: STL Algorithm & Container Mastery (100 examples)

Save output as `batch_09.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (5-30 lines). Each snippet MUST be unique.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code
   - A brief explanation (2-4 sentences) of WHY it is faster/cleaner.

Cover these subcategories evenly (~10 examples each):

1. Use Erase-Remove idiom instead of loop + erase
2. Use std::sort + std::unique to remove duplicates efficiently
3. Use std::lower_bound / std::upper_bound instead of manual binary search
4. Use std::partition instead of building two separate vectors
5. Use std::rotate / std::swap_ranges for in-place data rearrangement
6. Use std::inner_product / std::accumulate for numeric reductions
7. Use std::copy / std::fill / std::generate instead of manual loops
8. Use std::any_of / std::all_of / std::none_of instead of manual flag loops
9. Use std::minmax_element instead of separate min + max passes
10. Use std::priority_queue instead of repeated sorting for top-K problems

Contexts: data filtering, statistical analysis, game inventory systems, scheduling algorithms, ranking systems, batch processing, ETL pipelines, stream processing, feature engineering, caching layers.

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## BATCH 10: Real-World Mixed Optimizations (100 examples)

Save output as `batch_10.jsonl`

```
You are a Senior C++ Performance Engineer.

Generate 100 JSONL training examples for fine-tuning a Small Language Model.
Each example is a JSON object on its own line with exactly three keys:

  { "instruction": "...", "input": "...", "output": "..." }

Rules:
1. "instruction" is always: "Analyze the following C++ code for performance bottlenecks. Suggest optimized data structures and explain why."
2. "input" is a short, realistic, UNOPTIMIZED C++ snippet (10-30 lines). Each snippet MUST be unique and should contain MULTIPLE performance issues.
3. "output" contains TWO parts separated by "---":
   - The OPTIMIZED C++ code (fixing ALL issues)
   - A brief explanation (3-5 sentences) listing EACH optimization made and WHY.

Every example should combine 2-4 optimizations from this list:
- Data structure swaps (list→vector, map→unordered_map, etc.)
- Algorithm improvements (O(N²)→O(N), sort→binary_search)
- Memory management (raw pointers→smart pointers, RAII)
- Copy elimination (pass-by-reference, std::move, emplace_back)
- Loop optimization (cache .size(), hoist invariants, row-major access)
- String optimization (string_view, reserve, '\n' vs endl)
- Concurrency (atomic vs mutex, lock scope reduction)
- Modern C++ (auto&, structured bindings, optional, constexpr)

Provide realistic, multi-issue functions from these domains:
- Game engines (entity updates, collision detection, rendering pipelines)
- Web servers (request processing, response building, connection management)
- Data pipelines (CSV parsing, data transformation, aggregation)
- Scientific computing (matrix operations, simulations, numerical methods)
- Embedded systems (sensor data processing, firmware buffers, state machines)
- Compilers/interpreters (tokenizers, AST builders, symbol tables)
- Database engines (query processing, indexing, caching)
- Graphics (image processing, mesh operations, shader data)
- Networking (packet parsing, protocol handlers, message queues)
- Finance (trading systems, risk calculations, market data feeds)

Output ONLY the 100 JSONL lines. No surrounding text, no markdown fences, no numbering.
```

---

## After All Batches: Update train_unsloth.py

Since you now have ~1000 examples instead of 50, update these training parameters:

```python
# In TrainingArguments, change:
num_train_epochs=3,              # 3 epochs is enough with 1000 examples (was 5)
per_device_train_batch_size=4,   # Can increase batch size (was 2)
gradient_accumulation_steps=4,
learning_rate=1e-4,              # Slightly lower LR for larger dataset (was 2e-4)
warmup_steps=50,                 # More warmup steps (was 10)
logging_steps=10,                # Log every 10 steps (was 5)

# Also update the data file path:
dataset = load_dataset("json", data_files="full_training_data.jsonl", split="train")
```

## Quick Reference: All Categories Covered

| Batch | Category | Examples |
|-------|----------|----------|
| 1 | Data Structures & Cache Locality | 100 |
| 2 | Algorithm Optimization | 100 |
| 3 | Memory Management & RAII | 100 |
| 4 | Move Semantics & Copy Elimination | 100 |
| 5 | Concurrency & Threading | 100 |
| 6 | I/O & String Optimization | 100 |
| 7 | Loop & Computation Optimization | 100 |
| 8 | Modern C++ Patterns | 100 |
| 9 | STL Algorithm & Container Mastery | 100 |
| 10 | Real-World Mixed Optimizations | 100 |
| **Total** | | **1000** |
