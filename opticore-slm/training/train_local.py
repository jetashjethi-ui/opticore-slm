"""
OptiCore SLM — Local Training Script (Optimized for RTX 4050 / 6GB VRAM)
Uses Unsloth for 2x faster training with 50% less VRAM.
"""
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

print(f"🖥  GPU: {torch.cuda.get_device_name(0)}")
print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")

# ─── 1. Load base model (4-bit quantized to fit in 6GB VRAM) ───
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="HuggingFaceTB/SmolLM2-1.7B",
    max_seq_length=2048,
    load_in_4bit=True,
    dtype=None,
)

# ─── 2. Add LoRA adapters (trains only ~1-2% of parameters) ───
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
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

# ─── 4. Train (optimized for RTX 4050 6GB VRAM) ───
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
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
        seed=42,
    ),
)

print("🚀 Starting training...")
trainer.train()

# ─── 5. Save the fine-tuned model ───
model.save_pretrained("./opticore-finetuned-final")
tokenizer.save_pretrained("./opticore-finetuned-final")
print("✅ Training complete! Model saved to ./opticore-finetuned-final")
