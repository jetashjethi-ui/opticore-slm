"""
Export fine-tuned LoRA model to GGUF format (WITHOUT Unsloth).
Uses llama.cpp's convert script.

Steps:
  1. Merge LoRA adapters back into the base model
  2. Save the full merged model
  3. Convert to GGUF using llama.cpp

Run this AFTER training completes successfully.
"""
import torch
import os
import subprocess
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

LORA_PATH = "./opticore-finetuned-final"
BASE_MODEL = "HuggingFaceTB/SmolLM2-1.7B"
MERGED_PATH = "./opticore-merged-full"
GGUF_OUTPUT = "./opticore.gguf"

# ─── Step 1: Load base model + LoRA adapters ───
print("📥 Loading base model (on CPU for merging — avoids GPU OOM)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="cpu",
)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("🔗 Loading LoRA adapters...")
model = PeftModel.from_pretrained(base_model, LORA_PATH)

# ─── Step 2: Merge LoRA into base model ───
print("🔀 Merging LoRA weights into base model...")
model = model.merge_and_unload()

# ─── Step 3: Save merged model ───
print(f"💾 Saving merged model to {MERGED_PATH}...")
model.save_pretrained(MERGED_PATH)
tokenizer.save_pretrained(MERGED_PATH)
print(f"✅ Merged model saved!")

# ─── Step 4: Convert to GGUF (two-step: f16 then quantize to q4_k_m) ───
print("\n" + "=" * 60)
print("GGUF CONVERSION")
print("=" * 60)

GGUF_F16 = "./opticore-f16.gguf"   # intermediate full-precision GGUF

# Check if llama.cpp exists
if not os.path.exists("llama.cpp"):
    print("\n📥 llama.cpp not found. Cloning automatically...")
    try:
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp"], check=True)
        print("✅ Cloned successfully.")

        print("📦 Installing llama.cpp requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "llama.cpp/requirements.txt"], check=True)
        print("✅ Requirements installed.")
    except Exception as e:
        print(f"❌ Auto-setup failed: {e}")
        print("   Run these commands manually:\n")
        print("   git clone https://github.com/ggerganov/llama.cpp")
        print("   pip install -r llama.cpp/requirements.txt")
        exit(1)

# Determine the conversion script location
convert_script = os.path.join("llama.cpp", "convert_hf_to_gguf.py")
if not os.path.exists(convert_script):
    convert_script = os.path.join("llama.cpp", "convert.py")

# ── Step 4a: Convert HF model → f16 GGUF ──
print(f"\n🔄 Step 4a: Converting to f16 GGUF using {convert_script}...")
result = subprocess.run(
    [sys.executable, convert_script, MERGED_PATH,
        "--outtype", "f16", "--outfile", GGUF_F16],
    capture_output=True, text=True,
)

if result.returncode != 0:
    print(f"❌ f16 conversion failed:")
    print(result.stderr)
    print(f"\nTry running manually:")
    print(f"   python {convert_script} {MERGED_PATH} --outtype f16 --outfile {GGUF_F16}")
    exit(1)

f16_size = os.path.getsize(GGUF_F16) / (1024 * 1024)
print(f"✅ f16 GGUF created: {GGUF_F16} ({f16_size:.0f} MB)")

# ── Step 4b: Quantize f16 → q4_k_m ──
# Find the llama-quantize binary
quantize_bin = None
for candidate in [
    os.path.join("llama.cpp", "build", "bin", "llama-quantize"),
    os.path.join("llama.cpp", "build", "bin", "llama-quantize.exe"),
    os.path.join("llama.cpp", "build", "bin", "Release", "llama-quantize.exe"),
    os.path.join("llama.cpp", "llama-quantize"),
    os.path.join("llama.cpp", "llama-quantize.exe"),
    os.path.join("llama.cpp", "quantize"),
    os.path.join("llama.cpp", "quantize.exe"),
]:
    if os.path.exists(candidate):
        quantize_bin = candidate
        break

if quantize_bin:
    print(f"\n🔄 Step 4b: Quantizing f16 → q4_k_m using {quantize_bin}...")
    result = subprocess.run(
        [quantize_bin, GGUF_F16, GGUF_OUTPUT, "Q4_K_M"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        size_mb = os.path.getsize(GGUF_OUTPUT) / (1024 * 1024)
        print(f"\n✅ Quantized GGUF model created: {GGUF_OUTPUT} ({size_mb:.0f} MB)")
        print(f"\n👉 Copy this file to your server folder and run:")
        print(f"   python server.py --model {GGUF_OUTPUT}")
        # Clean up the intermediate f16 file
        os.remove(GGUF_F16)
        print(f"🗑️  Removed intermediate f16 file.")
    else:
        print(f"❌ Quantization failed:")
        print(result.stderr)
        print(f"\nTry running manually:")
        print(f"   {quantize_bin} {GGUF_F16} {GGUF_OUTPUT} Q4_K_M")
else:
    print(f"\n⚠️  llama-quantize binary not found!")
    print(f"   The f16 GGUF is ready at: {GGUF_F16}")
    print(f"\n   To get q4_k_m, you need to build llama.cpp first:")
    print(f"   cd llama.cpp")
    print(f"   cmake -B build")
    print(f"   cmake --build build --config Release")
    print(f"\n   Then quantize:")
    print(f"   .\\build\\bin\\Release\\llama-quantize.exe ../{GGUF_F16} ../{GGUF_OUTPUT} Q4_K_M")
    print(f"\n   OR just use the f16 GGUF directly (larger but works):")
    print(f"   python server.py --model {GGUF_F16}")
