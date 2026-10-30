# OptiCoreSLM

A local-first VS Code assistant for reviewing and improving C/C++ performance. It combines lightweight pattern-based suggestions with an optional GGUF language model running through a local Python server.

[Hugging Face model](https://huggingface.co/Neo-3007/OptiCore_slm) · [GGUF weights](https://huggingface.co/Neo-3007/OptiCore_slm/resolve/main/opticore.gguf) · [Training dataset](https://huggingface.co/datasets/Neo-3007/opticore_Slm) · [Installable VS Code extension](https://github.com/jetashjethi-ui/opticore-slm/blob/main/opticore-slm/vscode-extension/opticore-slm-0.1.0.vsix)

## What it does

Select C or C++ code in VS Code and run **OptiCore: Optimize Selection**. The extension sends the selection to a Flask service on your own machine. The service applies its rule-based checks and, when a GGUF model is configured, can also ask that model for a rewrite and explanation.

The server binds to 127.0.0.1 by default. Code is sent to that local process; the extension does not call a hosted inference API. Downloading the optional model from Hugging Face is a separate one-time step.

## How it is built

- VS Code extension: TypeScript command and results panel.
- Local API: Flask service with GET / for status and POST /optimize for code analysis.
- Heuristic engine: identifies selected common patterns and returns suggestions; a few cases can produce a code rewrite.
- Optional model: GGUF loaded with llama-cpp-python when the server starts with a model path.

These checks are heuristic. A suggested rewrite can change behavior or be unsuitable for a particular workload. Review it, compile it, run your tests, and measure performance before adopting it.

## Quick start

Requirements: Python, VS Code, and Node.js only if you plan to build the extension from source.

From the repository root, create a Python virtual environment:

    git clone https://github.com/jetashjethi-ui/opticore-slm.git
    cd opticore-slm/opticore-slm/server
    python -m venv .venv

Activate it before installing packages. On Windows PowerShell, run .venv/Scripts/Activate.ps1; on macOS or Linux, run source .venv/bin/activate.

Install the base dependencies:

    python -m pip install Flask flask-cors

Choose one server mode:

Rule-based mode:

    python server.py

Model mode: install the full requirements, download opticore.gguf from the Hugging Face model repository, replace PATH_TO_OPTICORE_GGUF with its local path, then start the server:

    python -m pip install -r requirements.txt
    python server.py --model "PATH_TO_OPTICORE_GGUF"

The server listens at http://127.0.0.1:8080. Keep that terminal open while using the extension. The hosted GGUF file is about 1.82 GB. Installing llama-cpp-python can require platform-specific build tools; see the [llama-cpp-python installation guide](https://github.com/abetlen/llama-cpp-python).

## Install the VS Code extension

The repository includes a packaged VSIX. From the repository root, enter the extension folder and install it:

    cd opticore-slm/vscode-extension
    code --install-extension opticore-slm-0.1.0.vsix

Reload VS Code, open a C or C++ file, select code, and run **OptiCore: Optimize Selection** from the context menu or Command Palette. The default server URL is http://127.0.0.1:8080 and can be changed in the OptiCore settings.

From the repository root, build the extension from source:

    cd opticore-slm/vscode-extension
    npm ci
    npm run compile

## Local API

GET / returns service status, including whether a model loaded.

POST /optimize accepts JSON with a code field:

    {"code": "int compute() { /* selected C++ code */ }"}

The response contains optimized_code, explanation, and engine fields. The output is a suggestion; the service does not compile or execute the submitted code.

## Model and dataset

The [Hugging Face model repository](https://huggingface.co/Neo-3007/OptiCore_slm) hosts opticore.gguf. The training scripts in this repository use [HuggingFaceTB/SmolLM2-1.7B](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B) as their base model.

The [training dataset](https://huggingface.co/datasets/Neo-3007/opticore_Slm) is also hosted on Hugging Face. The training directory contains the source batches, a merged JSONL file, and scripts for merging, training, and GGUF export. See [training notes](opticore-slm/training/TRAINING_GUIDE.md) for what those scripts expect.

## Scope and limitations

- This is a portfolio prototype, not a compiler, formal verifier, or production code optimizer.
- The rule engine uses pattern matching and does not understand every C++ program or its surrounding requirements.
- Model-generated rewrites can be incorrect, incomplete, or slower on the target machine.
- This repository does not publish a repeatable performance benchmark or a held-out model-quality evaluation. No speed-up or accuracy figures are claimed here.
- Model weights are hosted separately and are not included in the Git repository.
- The source repository currently has no license file. Check the model and dataset pages for their separate terms before reusing those artifacts.

## Repository layout

- opticore-slm/server: Flask API and runtime dependencies.
- opticore-slm/vscode-extension: extension source, package metadata, and installable VSIX.
- opticore-slm/training: JSONL data and training/export scripts.
