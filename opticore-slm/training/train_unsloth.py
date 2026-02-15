"""
OptiCore SLM — Training Script (Unsloth accelerated)
Optimized for RTX 4050 / 5060 with 6-8GB VRAM.
Uses: unsloth + trl (SFTTrainer + SFTConfig)

Updated for trl v0.28+ API.
"""
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

# --- 1. Load base model with Unsloth (4-bit quantized) ---
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="HuggingFaceTB/SmolLM2-1.7B",
    max_seq_length=2048,
    load_in_4bit=True,
)

# --- 2. Add LoRA adapters (only trains ~1-2% of parameters) ---
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
)

# --- 3. Load training data ---
dataset = load_dataset("json", data_files="all_training_data.jsonl", split="train")
print(f"Training examples: {len(dataset)}")

def format_prompt(example):
    return {
        "text": (
            f"### Instruction:\n{example['instruction']}\n\n"
            f"### Input:\n{example['input']}\n\n"
            f"### Response:\n{example['output']}"
        )
    }

dataset = dataset.map(format_prompt)

# --- 4. SFTConfig (trl v0.28+ API) ---
sft_config = SFTConfig(
    output_dir="./opticore-finetuned",
    num_train_epochs=5,
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
    report_to="none",
    gradient_checkpointing=True,
    dataset_text_field="text",
    max_length=2048,
)

# --- 5. Create trainer and train ---
trainer = SFTTrainer(
    model=model,
    args=sft_config,
    processing_class=tokenizer,
    train_dataset=dataset,
)

print("\nStarting training...")
trainer.train()

# --- 6. Save the fine-tuned model ---
model.save_pretrained("./opticore-finetuned-final")
tokenizer.save_pretrained("./opticore-finetuned-final")

print("\nTraining complete! Model saved to ./opticore-finetuned-final")
print("Next step: Convert to GGUF format")
print("  Run: python export_gguf_manual.py")