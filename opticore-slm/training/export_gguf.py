"""
Export fine-tuned model to GGUF format for use with llama-cpp-python server.
Run this AFTER training completes successfully.
"""
from unsloth import FastLanguageModel

print("Loading fine-tuned model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    "./opticore-finetuned-final",
    max_seq_length=2048,
    load_in_4bit=True,
)

print("Exporting to GGUF (Q4_K_M quantization)...")
model.save_pretrained_gguf(
    "./opticore-model-gguf",
    tokenizer,
    quantization_method="q4_k_m",
)

print("✅ GGUF model exported to ./opticore-model-gguf/")
print("   Copy the .gguf file to your server folder to use it.")
