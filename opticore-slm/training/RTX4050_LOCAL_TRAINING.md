# OptiCore SLM — Local Training on RTX 4050 Laptop (Step-by-Step)

> **Your GPU**: NVIDIA RTX 4050 Laptop (~6 GB VRAM)
> **Base Model**: SmolLM2-1.7B (4-bit quantized → ~3 GB VRAM)
> **Training Method**: LoRA fine-tuning via Unsloth (fastest option for your hardware)
> **Estimated Training Time**: ~15–30 minutes for ~500 examples

---

## Prerequisites Checklist

Before starting, make sure the other laptop has:

- [ ] Windows 10/11 (or Linux)
- [ ] NVIDIA RTX 4050 driver installed (latest from [nvidia.com/drivers](https://www.nvidia.com/drivers))
- [ ] Python 3.10 or 3.11 installed (NOT 3.12 — some packages don't support it yet)
- [ ] Git installed
- [ ] At least 20 GB free disk space
- [ ] Internet connection (to download the base model ~3.5 GB)

---

## Step 1: Verify NVIDIA GPU & CUDA

Open a terminal (PowerShell or CMD) and run:

```bash
nvidia-smi
```

You should see your **RTX 4050** listed with the driver version and CUDA version. Make note of the CUDA version (likely **12.x**).

> [!IMPORTANT]
> If `nvidia-smi` doesn't work, you need to install NVIDIA drivers first from https://www.nvidia.com/drivers

---

## Step 2: CUDA Toolkit (Optional)

> [!NOTE]
> Your `nvidia-smi` shows **CUDA 13.1** — this means your driver *supports up to* CUDA 13.1.
> **You do NOT need to install CUDA 13.1 separately.** PyTorch ships with its own CUDA runtime.
> You only need the NVIDIA driver (which you already have ✅).

If you want to install the CUDA toolkit anyway (for `nvcc` compiler), go to:
https://developer.nvidia.com/cuda-downloads and install **CUDA 12.6** (most stable).

---

## Step 3: Create a Python Virtual Environment

```bash
# Navigate to where you want to set up training
cd C:\Users\YourName\Desktop

# Create a folder for training
mkdir opticore-training
cd opticore-training

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

> [!TIP]
> Always activate the venv before running any commands. You'll see `(venv)` in your terminal prompt.

---

## Step 4: Install PyTorch with CUDA Support

This is the **most important step** — you must install PyTorch with CUDA, not the CPU version.

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

> Since your driver supports CUDA 13.1, you can use any PyTorch CUDA build ≤ 13.1.
> **`cu126` (CUDA 12.6) is recommended** — it's the most stable and well-tested.

### Verify PyTorch sees your GPU:

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
VRAM: 6.0 GB
```

> [!CAUTION]
> If `CUDA available: False`, PyTorch was installed without CUDA support. Uninstall and reinstall with the correct `--index-url`.

---

## Step 5: Install Training Dependencies

```bash
# Install Unsloth (the fast fine-tuning library)
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Install other training dependencies
pip install --no-deps trl peft accelerate bitsandbytes
pip install transformers datasets tokenizers sentencepiece protobuf
```

> [!NOTE]
> If `unsloth` installation fails on Windows, try the alternative approach:
> ```bash
> pip install unsloth
> ```
> Or use the **SFTTrainer-only method** (Step 5b below).

### Step 5b: Alternative — Install WITHOUT Unsloth (if it fails)

```bash
pip install transformers datasets trl peft accelerate
pip install bitsandbytes
pip install sentencepiece protobuf
```

---

## Step 6: Copy Your Project Files

Copy the entire `training` folder from this project to the other laptop. You need these files:

```
opticore-training/
├── venv/                         ← already created
├── train_unsloth.py              ← copy from this project
├── sample_training_data.jsonl    ← copy from this project
├── batch_01.jsonl                ← copy from this project
├── batch_02.jsonl                ← copy from this project
├── ...
├── batch_10.jsonl                ← copy from this project
└── merge_data.py            ← we'll create this below
```

### Easy way to copy:
1. Zip the `training` folder on this PC
2. Transfer via USB drive / Google Drive / OneDrive
3. Extract into `opticore-training` on the other laptop

---

## Step 7: Merge All Training Data

Create this script to merge all your JSONL batch files into one:

**`merge_data.py`**:

```python
"""Merge all JSONL batch files into one training file."""
import os
import json

output_file = "all_training_data.jsonl"
input_files = ["sample_training_data.jsonl"] + [f"batch_{i:02d}.jsonl" for i in range(1, 11)]

total = 0
with open(output_file, "w", encoding="utf-8") as out:
    for fname in input_files:
        if not os.path.exists(fname):
            print(f"  ⚠ Skipping {fname} (not found)")
            continue
        with open(fname, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                    # Verify it has the required fields
                    if all(k in obj for k in ["instruction", "input", "output"]):
                        out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        total += 1
                except json.JSONDecodeError:
                    pass

print(f"\n✅ Merged {total} examples into {output_file}")
```

Run it:
```bash
python merge_data.py
```

---

## Step 8: Train the Model 🚀

### Option A: Using Unsloth (RECOMMENDED — 2x faster, 50% less VRAM)

**`train_local.py`**:

```python
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

print(f"🖥 GPU: {torch.cuda.get_device_name(0)}")
print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")

# ─── 1. Load base model (4-bit quantized to fit in 6GB VRAM) ───
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="HuggingFaceTB/SmolLM2-1.7B",
    max_seq_length=2048,
    load_in_4bit=True,       # Critical for RTX 4050's 6GB VRAM
    dtype=None,              # Auto-detect (will use float16)
)

# ─── 2. Add LoRA adapters (trains only ~1-2% of parameters) ───
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                    # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
)

# ─── 3. Load merged training data ───
dataset = load_dataset("json", data_files="all_training_data.jsonl", split="train")
print(f"📊 Training examples: {len(dataset)}")

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
# Settings optimized for RTX 4050 (6GB VRAM)
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        output_dir="./opticore-finetuned",
        num_train_epochs=3,                 # 3 epochs is good for ~500 examples
        per_device_train_batch_size=2,      # 2 fits in 6GB with 4-bit
        gradient_accumulation_steps=4,      # Effective batch size = 2 * 4 = 8
        learning_rate=2e-4,
        fp16=True,                          # Use float16 for speed
        logging_steps=10,
        save_strategy="epoch",
        warmup_steps=10,
        optim="adamw_8bit",                 # 8-bit optimizer saves VRAM
        weight_decay=0.01,
        seed=42,
    ),
)

print("🚀 Starting training...")
trainer.train()

# ─── 5. Save the fine-tuned model ───
model.save_pretrained("./opticore-finetuned-final")
tokenizer.save_pretrained("./opticore-finetuned-final")
print("✅ Training complete! Model saved to ./opticore-finetuned-final")
```

Run training:
```bash
python train_local.py
```

### Option B: WITHOUT Unsloth (if Unsloth doesn't install)

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer
from datasets import load_dataset

print(f"🖥 GPU: {torch.cuda.get_device_name(0)}")
print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    "HuggingFaceTB/SmolLM2-1.7B",
    quantization_config=bnb_config,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-1.7B")
tokenizer.pad_token = tokenizer.eos_token

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Dataset
dataset = load_dataset("json", data_files="all_training_data.jsonl", split="train")
print(f"📊 Training examples: {len(dataset)}")

def format_prompt(example):
    return {
        "text": (
            f"### Instruction:\n{example['instruction']}\n\n"
            f"### Input:\n{example['input']}\n\n"
            f"### Response:\n{example['output']}"
        )
    }

dataset = dataset.map(format_prompt)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    peft_config=lora_config,
    args=TrainingArguments(
        output_dir="./opticore-finetuned",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        warmup_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
    ),
)

print("🚀 Starting training...")
trainer.train()

model.save_pretrained("./opticore-finetuned-final")
tokenizer.save_pretrained("./opticore-finetuned-final")
print("✅ Training complete!")
```

---

## Step 9: Convert to GGUF Format

After training completes, convert the model to GGUF so your server can use it.

### Option A: Using Unsloth (easiest)

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "./opticore-finetuned-final",
    max_seq_length=2048,
    load_in_4bit=True,
)

# Export as GGUF (Q4_K_M = good balance of size vs quality)
model.save_pretrained_gguf(
    "./opticore-model-gguf",
    tokenizer,
    quantization_method="q4_k_m",
)

print("✅ GGUF model exported to ./opticore-model-gguf/")
```

Save as `export_gguf.py` and run:
```bash
python export_gguf.py
```

### Option B: Using llama.cpp (if Unsloth export fails)

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
pip install -r requirements.txt

python convert_hf_to_gguf.py ../opticore-finetuned-final --outtype q4_k_m --outfile ../opticore.gguf
```

---

## Step 10: Test the Model

Copy the `.gguf` file back into your project's `server` folder and test:

```bash
cd server
pip install llama-cpp-python flask

python server.py --model path/to/opticore.gguf
```

---

## Step 11: Copy the GGUF Back to Your Main PC

1. Find the `.gguf` file in `opticore-model-gguf/` folder (usually named something like `unsloth.Q4_K_M.gguf`)
2. Transfer it back to your main PC via USB/cloud
3. Place it in `opticore-slm/server/`
4. Update `server.py` to point to the new model file
5. Run the server and test with your VS Code extension! 🎉

---

## Troubleshooting

### ❌ "CUDA out of memory"
- Reduce `per_device_train_batch_size` from `2` to `1`
- Reduce `max_seq_length` from `2048` to `1024`
- Make sure no other GPU-heavy apps are running (close browsers, games, etc.)

### ❌ "Unsloth not found" or install errors
- Use **Option B** (SFTTrainer without Unsloth) — it works the same, just ~2x slower

### ❌ PyTorch doesn't see the GPU
- Reinstall PyTorch with the correct CUDA version:
  ```bash
  pip uninstall torch torchvision torchaudio
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
  ```

### ❌ "bitsandbytes" errors on Windows
- Install the Windows-compatible version:
  ```bash
  pip install bitsandbytes-windows
  ```
  or
  ```bash
  pip install bitsandbytes --prefer-binary
  ```

### ❌ Training is very slow
- Make sure PyTorch is using the GPU (check `nvidia-smi` during training — GPU utilization should be >50%)
- Close other applications using the GPU

---

## VRAM Budget for RTX 4050 (6 GB)

| Component | VRAM Usage |
|-----------|-----------|
| SmolLM2-1.7B (4-bit) | ~1.5 GB |
| LoRA adapters | ~0.3 GB |
| Optimizer states (8-bit) | ~0.5 GB |
| Activations (batch=2, seq=2048) | ~2.0 GB |
| PyTorch overhead | ~0.5 GB |
| **Total** | **~4.8 GB** ✅ |

> You have ~1.2 GB headroom. If you hit OOM errors, reduce batch size to 1.

---

## Quick Command Summary

```bash
# 1. Setup
python -m venv venv && .\venv\Scripts\activate

# 2. Install
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps trl peft accelerate bitsandbytes
pip install transformers datasets tokenizers sentencepiece protobuf

# 3. Merge data
python merge_data.py

# 4. Train (~15-30 min)
python train_local.py

# 5. Export GGUF
python export_gguf.py

# 6. Done! Copy the .gguf file to your server
```
