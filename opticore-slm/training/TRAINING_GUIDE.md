# OptiCore SLM — Full Training & GGUF Guide

## Overview

```
Training Data (JSONL) → Fine-tune base model (Unsloth/SFTTrainer) → Export to GGUF → Use in server.py
```

---

## Step 1: Generate Training Data

You already have `training_data_prompt.md`. Paste the prompt into GPT-4/Claude/Gemini and save the 50 JSONL lines into `sample_training_data.jsonl`.

---

## Step 2: Choose a Base Model

| Model | Size | VRAM Needed | Recommended? |
|-------|------|-------------|--------------|
| `SmolLM2-1.7B` | 1.7B | ~6 GB | ✅ Best for your use case |
| `TinyLlama-1.1B` | 1.1B | ~4 GB | ✅ Lightweight alternative |
| `CodeLlama-7B` | 7B | ~16 GB | Only if you have a strong GPU |
| `Phi-2` | 2.7B | ~8 GB | Good middle ground |

> **SmolLM2** is HuggingFace's small model family — it's what you might be thinking of as "Smolify". There's no separate tool called Smolify you need; **SmolLM2 is just a base model** you can fine-tune with Unsloth.

---

## Step 3: Fine-Tune with Unsloth (Recommended — 2x faster, 50% less VRAM)

### Install (Google Colab or local with NVIDIA GPU)

```bash
pip install unsloth
pip install "trl>=0.7.0" transformers datasets
```

### Training Script

Save this as `train_unsloth.py`:

```python
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# ─── 1. Load base model with Unsloth (4-bit quantized) ───
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="HuggingFaceTB/SmolLM2-1.7B",  # or "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    max_seq_length=2048,
    load_in_4bit=True,      # saves VRAM
)

# ─── 2. Add LoRA adapters (only trains ~1-2% of parameters) ───
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                   # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
)

# ─── 3. Load your JSONL training data ───
dataset = load_dataset("json", data_files="sample_training_data.jsonl", split="train")

# Format each example into a prompt
def format_prompt(example):
    return {
        "text": (
            f"### Instruction:\n{example['instruction']}\n\n"
            f"### Input:\n{example['input']}\n\n"
            f"### Response:\n{example['output']}"
        )
    }

dataset = dataset.map(format_prompt)

# ─── 4. Train ───
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        output_dir="./opticore-finetuned",
        num_train_epochs=5,             # 5 epochs for small dataset
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=5,
        save_strategy="epoch",
        warmup_steps=10,
    ),
)

trainer.train()

# ─── 5. Save the fine-tuned model ───
model.save_pretrained("./opticore-finetuned-final")
tokenizer.save_pretrained("./opticore-finetuned-final")

print("✅ Training complete! Model saved to ./opticore-finetuned-final")
```

### Run Training

```bash
python train_unsloth.py
```

> **⏱ Training time**: ~10-30 minutes on a free Google Colab T4 GPU with 50 examples.

---

## Step 4: Convert to GGUF

After training, convert the model to GGUF format so `llama-cpp-python` can load it in your server.

### Option A: Using Unsloth (easiest)

Add this to the end of your training script or run separately:

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "./opticore-finetuned-final",
    max_seq_length=2048,
    load_in_4bit=True,
)

# Export as GGUF (Q4_K_M is a good balance of size vs quality)
model.save_pretrained_gguf(
    "./opticore-model-gguf",
    tokenizer,
    quantization_method="q4_k_m",   # options: q4_k_m, q5_k_m, q8_0, f16
)

print("✅ GGUF model saved to ./opticore-model-gguf/")
```

### Option B: Using llama.cpp manually

```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Convert HuggingFace model to GGUF
python convert_hf_to_gguf.py ../opticore-finetuned-final --outtype q4_k_m --outfile opticore.gguf
```

---

## Step 5: Use with Your Server

Copy the `.gguf` file into your project and start the server:

```bash
cd server
python server.py --model path/to/opticore.gguf
```

The extension will now use your fine-tuned model for real AI-powered C++ optimization! 🚀

---

## Alternative: SFTTrainer Without Unsloth

If you can't use Unsloth (e.g., no NVIDIA GPU), use HuggingFace's `SFTTrainer` directly:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer
from datasets import load_dataset

# Load model with 4-bit quantization
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-1.7B", quantization_config=bnb_config)
tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-1.7B")

# LoRA config
lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05)

# Dataset
dataset = load_dataset("json", data_files="sample_training_data.jsonl", split="train")

def format_prompt(example):
    return {"text": f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"}

dataset = dataset.map(format_prompt)

# Train
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=dataset,
    dataset_text_field="text", max_seq_length=2048, peft_config=lora_config,
    args=TrainingArguments(output_dir="./opticore-finetuned", num_train_epochs=5,
                           per_device_train_batch_size=2, learning_rate=2e-4, fp16=True),
)
trainer.train()
model.save_pretrained("./opticore-finetuned-final")
```

> Then convert to GGUF using **Option B** from Step 4.

---

## Quick Reference: What Is What?

| Term | What it is |
|------|-----------|
| **Unsloth** | Python library that speeds up fine-tuning 2x and uses 50% less VRAM |
| **SFTTrainer** | HuggingFace's Supervised Fine-Tuning trainer (from `trl` library) |
| **LoRA** | Technique to fine-tune only ~1% of model weights (saves VRAM) |
| **GGUF** | Model file format used by `llama.cpp` / `llama-cpp-python` for CPU inference |
| **SmolLM2** | HuggingFace's small (1.7B) model — good base model for your project |
| **Smolify** | Not a tool you need — "Smol" just refers to HuggingFace's small model family |
| **Quantization** | Compressing model weights (e.g., 32-bit → 4-bit) to reduce size & VRAM |

---

## Recommended Path (TL;DR)

```
1. Generate 50 JSONL examples (paste prompt into ChatGPT/Claude)
2. Open Google Colab (free T4 GPU)
3. Run train_unsloth.py with SmolLM2-1.7B
4. Export to GGUF with model.save_pretrained_gguf()
5. Download the .gguf file
6. python server.py --model opticore.gguf
7. Use in VS Code! ✅
```
