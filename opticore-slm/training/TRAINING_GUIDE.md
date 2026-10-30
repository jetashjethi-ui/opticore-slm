# Training notes

This folder contains research scripts and JSONL examples for fine-tuning and exporting the optional model. It is not a pinned, cross-platform training environment.

## Data flow

The scripts expect records with instruction, input, and output fields. merge_data.py combines the sample file, batch_01.jsonl through batch_10.jsonl, and algo_batch_01.jsonl through algo_batch_10.jsonl into all_training_data.jsonl.

Run data preparation from this folder:

    python merge_data.py

## Training and export scripts

- train_local.py uses Unsloth and targets HuggingFaceTB/SmolLM2-1.7B.
- train_unsloth.py is an alternate Unsloth SFT script using the same base model.
- train_sft.py uses Transformers, PEFT, TRL, and bitsandbytes.
- export_gguf.py exports the saved fine-tuned model through Unsloth.
- export_gguf_manual.py merges a PEFT adapter and invokes llama.cpp conversion tools.

The scripts use different framework APIs and GPU settings. Their Python dependencies are not pinned in a training lockfile, so create a compatible CUDA/PyTorch environment and review the selected script before starting a run. Training is not required to use the prebuilt extension or the hosted GGUF model.

## Evaluation

The repository does not include a standardized held-out evaluation or repeatable performance benchmark for the model. Treat training examples and generated rewrites as experimental. Do not describe them as measured speedups or validated optimization quality without a separate benchmark that checks correctness and performance.