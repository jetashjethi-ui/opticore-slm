/**
 * OptiCore SLM — VS Code Extension
 * ==================================
 * Sends selected C++ code to the local Python server for performance analysis.
 * Results are displayed in a styled Webview side panel.
 */

import * as vscode from "vscode";
import * as http from "http";

// ──────────────────────────────────────────────────────────────────────────────
// Extension lifecycle
// ──────────────────────────────────────────────────────────────────────────────

export function activate(context: vscode.ExtensionContext) {
  console.log("[OptiCore] Extension activated.");

  const disposable = vscode.commands.registerCommand(
    "opticore.optimizeSelection",
    () => handleOptimize(context)
  );

  context.subscriptions.push(disposable);
}

export function deactivate() {
  console.log("[OptiCore] Extension deactivated.");
}

// ──────────────────────────────────────────────────────────────────────────────
// Core command handler
// ──────────────────────────────────────────────────────────────────────────────

async function handleOptimize(context: vscode.ExtensionContext) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("OptiCore: No active editor.");
    return;
  }

  const selection = editor.selection;
  const selectedText = editor.document.getText(selection);

  if (!selectedText.trim()) {
    vscode.window.showWarningMessage("OptiCore: Please select some C++ code first.");
    return;
  }

  // Show progress indicator
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "OptiCore: Analyzing your code…",
      cancellable: false,
    },
    async () => {
      try {
        const serverUrl = vscode.workspace
          .getConfiguration("opticore")
          .get<string>("serverUrl", "http://127.0.0.1:5000");

        const result = await postToServer(serverUrl, selectedText);
        showResultPanel(context, selectedText, result);
      } catch (err: any) {
        vscode.window.showErrorMessage(
          `OptiCore: Could not reach the server. Is server.py running?\n${err.message}`
        );
      }
    }
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// HTTP client (zero dependencies — uses Node built-in http)
// ──────────────────────────────────────────────────────────────────────────────

interface OptimizeResult {
  optimized_code: string;
  explanation: string;
  engine: string;
}

function postToServer(serverUrl: string, code: string): Promise<OptimizeResult> {
  return new Promise((resolve, reject) => {
    const url = new URL("/optimize", serverUrl);
    const payload = JSON.stringify({ code });

    const options: http.RequestOptions = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
      },
    };

    const req = http.request(options, (res: http.IncomingMessage) => {
      let body = "";
      res.on("data", (chunk: string) => (body += chunk));
      res.on("end", () => {
        try {
          const json = JSON.parse(body);
          if (json.error) {
            reject(new Error(json.error));
          } else {
            resolve(json as OptimizeResult);
          }
        } catch {
          reject(new Error("Invalid JSON response from server."));
        }
      });
    });

    req.on("error", (e) => reject(e));
    req.setTimeout(120000, () => {
      req.destroy();
      reject(new Error("Request timed out (120 s)."));
    });

    req.write(payload);
    req.end();
  });
}

// ──────────────────────────────────────────────────────────────────────────────
// Webview panel — shows original vs optimized side by side
// ──────────────────────────────────────────────────────────────────────────────

function showResultPanel(
  context: vscode.ExtensionContext,
  original: string,
  result: OptimizeResult
) {
  const panel = vscode.window.createWebviewPanel(
    "opticoreResult",
    "OptiCore — Optimization Result",
    vscode.ViewColumn.Beside,
    { enableScripts: false }
  );

  panel.webview.html = getWebviewHtml(original, result);
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function getWebviewHtml(original: string, result: OptimizeResult): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OptiCore Result</title>
  <style>
    :root {
      --bg: #1e1e2e;
      --surface: #2a2a3d;
      --border: #3a3a5c;
      --accent: #a777e3;
      --accent2: #6e8efb;
      --text: #cdd6f4;
      --text-dim: #9399b2;
      --green: #a6e3a1;
      --red: #f38ba8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', 'Consolas', monospace;
      background: var(--bg);
      color: var(--text);
      padding: 24px;
      line-height: 1.6;
    }
    h1 {
      font-size: 1.4rem;
      margin-bottom: 8px;
      background: linear-gradient(135deg, var(--accent2), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .engine-badge {
      display: inline-block;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 20px;
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--accent);
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 24px;
    }
    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }
    .panel-header {
      padding: 10px 16px;
      font-weight: 600;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--border);
    }
    .panel-header.original { color: var(--red); }
    .panel-header.optimized { color: var(--green); }
    pre {
      padding: 16px;
      font-size: 0.85rem;
      overflow-x: auto;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    .explanation {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
    }
    .explanation h2 {
      font-size: 1rem;
      color: var(--accent);
      margin-bottom: 12px;
    }
    .explanation p {
      color: var(--text-dim);
      font-size: 0.9rem;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <h1>⚡ OptiCore SLM</h1>
  <span class="engine-badge">Engine: ${escapeHtml(result.engine)}</span>

  <div class="grid">
    <div class="panel">
      <div class="panel-header original">▎ Original Code</div>
      <pre>${escapeHtml(original)}</pre>
    </div>
    <div class="panel">
      <div class="panel-header optimized">▎ Optimized Code</div>
      <pre>${escapeHtml(result.optimized_code)}</pre>
    </div>
  </div>

  <div class="explanation">
    <h2>💡 Why This Is Faster</h2>
    <p>${escapeHtml(result.explanation)}</p>
  </div>
</body>
</html>`;
}
