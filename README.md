# OptiCoreSLM

A small language model fine-tuned to find and fix performance bottlenecks in C++ code — runs locally, no internet required.

OptiCoreSLM is built around one idea: C++ performance work often happens on codebases that can't leave the machine. Cloud-based tools are out. General-purpose local models are either too slow or too generic to be useful for hardware-level rewrites. OptiCoreSLM is fine-tuned specifically on C++ optimization patterns — bit manipulation, branchless arithmetic, cache-friendly data structures, algorithmic complexity — and ships as a VS Code extension backed by a local Python server.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [First-Time Setup](#first-time-setup)
- [Everyday Startup](#everyday-startup)
- [Using the Extension](#using-the-extension)
- [All Commands Reference](#all-commands-reference)
- [Troubleshooting](#troubleshooting)
- [Usage Examples](#usage-examples)
- [Benchmarks](#benchmarks)
- [Links](#links)
- [Acknowledgements](#acknowledgements)

---

## How It Works

OptiCoreSLM has three components that must all be running together:

```
VS Code Extension  (you select C++ code, right-click → OptiCore: Optimize Selection)
       │
       │  POST http://127.0.0.1:8080/optimize
       ▼
Python Server  (server.py — Flask, runs locally)
       │
       ├── Rule-based engine  (always available, instant, no model needed)
       └── GGUF model via llama-cpp-python  (optional, loaded with --model flag)
```

**The server has two modes:**

| Mode | How to start | When to use |
| :--- | :--- | :--- |
| Rule-based fallback | `python server.py` | Demo, testing, no model file available |
| Full AI model | `python server.py --model path/to/model.gguf` | Production use with the fine-tuned weights |

The rule-based mode is not a stub — it covers real patterns: `std::list → std::vector`, `std::map → std::unordered_map`, nested O(N²) loops, missing `reserve()`, raw `new` usage, Dutch National Flag sorting, bubble sort, and linear search on sorted arrays. It is accurate and instant. The GGUF model handles free-form cases outside those patterns.

---

## Project Structure

```
opticore-slm/                        # repo root
└── opticore-slm/                    # project folder
    ├── server/
    │   ├── server.py                # Flask inference server (port 8080)
    │   └── requirements.txt         # flask, flask-cors, llama-cpp-python
    ├── training/                    # fine-tuning scripts and JSONL datasets
    │   ├── train_sft.py
    │   ├── train_unsloth.py
    │   ├── all_training_data.jsonl
    │   └── ...
    └── vscode-extension/            # VS Code extension source
        ├── src/
        │   └── extension.ts         # extension entry point
        ├── out/
        │   └── extension.js         # compiled output
        ├── package.json             # extension manifest (engines: vscode ^1.85.0)
        ├── tsconfig.json
        └── opticore-slm-0.1.0.vsix  # pre-built installable package
```

---

## Prerequisites

| Requirement | Version | Notes |
| :--- | :--- | :--- |
| Python | 3.9+ | Check with `python --version` |
| pip | any recent | Comes with Python |
| Node.js | 18 LTS+ | Only needed if you modify the extension source |
| VS Code | 1.85+ | The extension's `engines` field requires this |
| `@vscode/vsce` | latest | Only needed to repackage the extension after code changes |

You do **not** need Ollama. The server runs the model directly via `llama-cpp-python`.

---

## First-Time Setup

Do these steps once. After that, use [Everyday Startup](#everyday-startup) only.

### Step 1 — Install Python dependencies

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\server
python -m pip install -r requirements.txt
```

`requirements.txt` installs:

| Package | Purpose |
| :--- | :--- |
| `flask>=3.0.0` | Runs the local web server that the extension talks to |
| `flask-cors>=4.0.0` | Allows the extension's webview to make requests to localhost |
| `llama-cpp-python>=0.2.0` | Loads and runs the GGUF model file on CPU |

> **If `llama-cpp-python` fails to install:** It needs C++ build tools. On Windows, install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the "Desktop development with C++" workload, then retry. If you only want the rule-based mode (no model), you can skip it — the server runs fine without it and will print a warning on startup.

Verify the installs:

```bash
python -m pip show flask
python -m pip show flask-cors
python -m pip show llama-cpp-python
```

### Step 2 — Install the VS Code extension

The `.vsix` file is already built and committed. Install it once:

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\vscode-extension
code --install-extension opticore-slm-0.1.0.vsix
```

After installation, reload VS Code: `Ctrl+Shift+P` → **Developer: Reload Window**.

You do not need to run `npm install` or `vsce package` unless you are changing the extension source code.

---

## Everyday Startup

Every time you restart your laptop or want to use OptiCore, do only these two steps.

### Terminal 1 — Start the Python server

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\server
python server.py
```

Wait until you see:

```
[OptiCore] No --model provided. Running in rule-based fallback mode.
[OptiCore] Server starting on http://127.0.0.1:8080
 * Running on http://127.0.0.1:8080
```

**Keep this terminal open.** The extension stops working the moment you close it.

To use the AI model instead of the rule-based fallback:

```bash
python server.py --model path\to\your-model.gguf
```

### Terminal 2 — Open VS Code

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm
code .
```

If VS Code is already open with the right folder, skip this.

---

## Using the Extension

1. Open any `.cpp` or `.c` file in VS Code.
2. Select the code you want to optimize (a function, a block, or the whole file).
3. Right-click the selection.
4. Click **OptiCore: Optimize Selection**.
5. A side panel opens showing original vs optimized code and an explanation.

> The right-click menu item only appears when:
> - A `.cpp` or `.c` file is open (VS Code language ID: `cpp` or `c`)
> - Some text is selected

If the item doesn't appear, check those two conditions first. You can also run it from the Command Palette: `Ctrl+Shift+P` → type `OptiCore: Optimize Selection`.

---

## All Commands Reference

### A. Running the backend

| Task | Command |
| :--- | :--- |
| Navigate to server folder | `cd C:\Users\deepa\opticore-slm\opticore-slm\server` |
| Start server (rule-based mode) | `python server.py` |
| Start server (with AI model) | `python server.py --model path\to\model.gguf` |
| Start on a different port | `python server.py --port 9090` |
| Stop the server | `Ctrl+C` in the server terminal |
| Check Python version | `python --version` |
| Verify Flask is installed | `python -m pip show flask` |
| Verify flask-cors is installed | `python -m pip show flask-cors` |
| Verify llama-cpp-python | `python -m pip show llama-cpp-python` |
| List all installed packages | `python -m pip list` |
| Install all dependencies | `python -m pip install -r requirements.txt` |

### B. Working with the VS Code extension

Navigate to the extension folder first:

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\vscode-extension
```

| Task | Command | When to use |
| :--- | :--- | :--- |
| Install the pre-built extension | `code --install-extension opticore-slm-0.1.0.vsix` | First-time setup or reinstall |
| Force reinstall same version | `code --install-extension opticore-slm-0.1.0.vsix --force` | Extension got corrupted or deactivated |
| Install JS dependencies | `npm install` | Only after cloning fresh or changing `package.json` |
| Compile TypeScript | `npm run compile` | After editing `src/extension.ts` |
| Watch mode (auto-recompile) | `npm run watch` | During active development |
| Package into `.vsix` | `vsce package` | After compiling, to build a new installable file |
| List `.vsix` files | `dir *.vsix` | To see the filename before installing |
| Reload VS Code after install | `Ctrl+Shift+P` → Developer: Reload Window | Always run after installing/updating `.vsix` |

**Workflow when you change the extension source:**

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\vscode-extension
npm run compile
vsce package
dir *.vsix
code --install-extension opticore-slm-0.1.0.vsix --force
```

Then reload VS Code (`Ctrl+Shift+P` → **Developer: Reload Window**).

### C. Verifying the server is up

Open a browser or run this in PowerShell:

```
http://127.0.0.1:8080
```

You should get a JSON response like:

```json
{
  "engine": "opticore-ai",
  "model_loaded": false,
  "service": "OptiCore SLM",
  "status": "ok"
}
```

`model_loaded: false` means the server is in rule-based mode (no GGUF file). That is normal and fine for most use.

---

## Troubleshooting

**`OptiCore: Could not reach the server. Is server.py running?`**

The extension sent a request but got no response. Fix: Start the server in a terminal and keep it running.

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\server
python server.py
```

---

**Server crashes immediately on startup with a colorama/click error**

The server already works around this with `os.environ.setdefault("NO_COLOR", "1")`. If you still see it, make sure you are running the latest `server.py` from the repo.

---

**`python -m pip install -r requirements.txt` fails on `llama-cpp-python`**

This package compiles C++ code. You need build tools installed:

1. Download [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. Select **Desktop development with C++**.
3. Install, then restart your terminal.
4. Retry `python -m pip install llama-cpp-python`.

If you don't need the AI model and only want the rule-based mode, skip this package — `flask` and `flask-cors` are enough to run the server.

---

**`npm install` fails: `Could not find package.json`**

You are in the wrong folder. `package.json` is inside `vscode-extension/`, not the repo root:

```bash
cd C:\Users\deepa\opticore-slm\opticore-slm\vscode-extension
dir
```

Confirm `package.json` is listed, then run `npm install`.

---

**`vsce package` is not recognized**

Install `vsce` globally first:

```bash
npm install -g @vscode/vsce
```

Then retry `vsce package` from inside the `vscode-extension/` folder.

---

**The right-click menu item doesn't show up**

Two conditions must both be true:
1. The file must be a `.cpp` or `.c` file (VS Code detects this automatically from the extension).
2. You must have text selected before right-clicking.

If both are true and the item is still missing: run `code --install-extension opticore-slm-0.1.0.vsix --force` and reload VS Code.

---

**Extension shows an error but the server is running**

The default server URL in the extension is `http://127.0.0.1:8080`. Confirm this in VS Code Settings:

`Ctrl+,` → search `opticore` → check `opticore.serverUrl`

If your server started on a different port (e.g., you used `--port 9090`), update this setting to match.

---

**Model inference takes a long time or times out**

The server waits up to 90 seconds for the model. On CPU-only machines, inference on longer functions can approach this limit. Options:
- Use a smaller/more quantized GGUF file.
- Trim the selection to just the function you want optimized.
- Use rule-based mode for instant results (`python server.py` without `--model`).

---

## Usage Examples

### Bit-count optimization

Before:

```cpp
int countBits(int n) {
    int count = 0;
    while (n) {
        count += n & 1;
        n >>= 1;
    }
    return count;
}
```

After:

```cpp
int countBits(int n) {
    return __builtin_popcount(n);
}
```

### Power-of-2 check

Before:

```cpp
bool isPowerOfTwo(int n) {
    return (n > 0) && (n % 2 == 0);
}
```

After:

```cpp
bool isPowerOfTwo(int n) {
    return (n > 0) && !(n & (n - 1));
}
```

### Sort 0s, 1s, 2s (Dutch National Flag)

Before (counting sort, two passes):

```cpp
void sortZeroOneTwo(vector<int>& nums) {
    int c0 = 0, c1 = 0, c2 = 0;
    for (int x : nums) { if (x==0) c0++; else if (x==1) c1++; else c2++; }
    int i = 0;
    while (c0--) nums[i++] = 0;
    while (c1--) nums[i++] = 1;
    while (c2--) nums[i++] = 2;
}
```

After (single pass, O(N) time, O(1) space):

```cpp
void sortZeroOneTwo(vector<int>& nums) {
    // Dutch National Flag Algorithm (Dijkstra's 3-way partition)
    int low = 0, mid = 0, high = (int)nums.size() - 1;
    while (mid <= high) {
        if      (nums[mid] == 0) { swap(nums[low], nums[mid]); low++; mid++; }
        else if (nums[mid] == 1) { mid++; }
        else                     { swap(nums[mid], nums[high]); high--; }
    }
}
```

---

## Benchmarks

Measured manually at `-O0` on x86-64 (GCC). Numbers are directional.

| Task | Original | Optimized | Approx. reduction |
| :--- | :--- | :--- | :--- |
| Bit count | `while` loop + shift | `__builtin_popcount` | ~90% |
| Power-of-2 check | `n % 2` | `!(n & (n-1))` | ~95% |
| Sort 0/1/2 | Counting sort (2 passes) | Dutch National Flag (1 pass) | ~50% |

---

## Links

| | |
| :--- | :--- |
| Hugging Face model | [Neo-3007/OptiCore_slm](https://huggingface.co/Neo-3007/OptiCore_slm) |
| Hugging Face dataset | [link] |
| GitHub | [jetashjethi-ui/opticore-slm](https://github.com/jetashjethi-ui/opticore-slm) |
| Demo video | [link] |

---

## Acknowledgements

- **[Requestly](https://requestly.com)** — used to mock the `POST /optimize` HTTP calls during development so the extension UI could be built and tested before `server.py` was wired up. Cut integration time significantly.
- **[Flask](https://flask.palletsprojects.com)** — lightweight Python web framework powering the inference server.
- **[llama-cpp-python](https://github.com/abetlen/llama-cpp-python)** — Python bindings for llama.cpp, used to run the GGUF model on CPU.
- **[Hugging Face](https://huggingface.co)** — model and dataset hosting.
