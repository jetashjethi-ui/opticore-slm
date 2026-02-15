"""
OptiCore SLM — Local Training Script (SFTTrainer WITHOUT Unsloth)
Optimized for RTX 4050 / RTX 5060 (6-8GB VRAM).
Uses: transformers + peft + trl + bitsandbytes (standard HuggingFace stack)

Verified against trl v0.28.0 official API docs.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

# ─── 0. Check GPU ───
if not torch.cuda.is_available():
    print("❌ CUDA not available! Make sure PyTorch is installed with CUDA support.")
    print("   Run: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126")
    exit(1)

print(f"🖥  GPU: {torch.cuda.get_device_name(0)}")
print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
print(f"🔧 PyTorch: {torch.__version__}")
print(f"🔧 CUDA: {torch.version.cuda}")
print()

# ─── 1. Set up 4-bit quantization (to fit in 6GB VRAM) ───
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# ─── 2. Load base model and tokenizer ───
MODEL_NAME = "HuggingFaceTB/SmolLM2-1.7B"

print(f"📥 Loading model: {MODEL_NAME}")
print("   (This downloads ~3.5 GB on first run, then uses cache)")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# ─── 3. LoRA config (passed to SFTTrainer, not applied manually) ───
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# ─── 4. Load and format training data ───
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

# ─── 5. SFTConfig (all training + SFT params go here) ───
sft_config = SFTConfig(
    output_dir="./opticore-finetuned",
    num_train_epochs=3,          # 3 epochs for 3000+ examples (was 5 for ~1000)
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    warmup_steps=10,
    optim="adamw_8bit",
    weight_decay=0.01,
    seed=42,
    report_to="none",
    gradient_checkpointing=True,
    dataset_text_field="text",
    max_length=2048,
)

# ─── 6. Create trainer and train ───
trainer = SFTTrainer(
    model=model,
    args=sft_config,
    processing_class=tokenizer,
    train_dataset=dataset,
    peft_config=lora_config,
)

print("\n🚀 Starting training...")
print(f"   Dataset: {len(dataset)} examples x {sft_config.num_train_epochs} epochs")
print("   This will take ~30-60 minutes on RTX 4050/5060")
print("   Watch nvidia-smi in another terminal to monitor GPU usage\n")

trainer.train()

# ─── 7. Save the fine-tuned model ───
trainer.save_model("./opticore-finetuned-final")
tokenizer.save_pretrained("./opticore-finetuned-final")

print("\n✅ Training complete!")
print("📁 Model saved to: ./opticore-finetuned-final")
print("\n👉 Next step: Convert to GGUF format")
print("   Run: python export_gguf_manual.py")
