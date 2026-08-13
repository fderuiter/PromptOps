# 🎨 Proompts Visual Studio IDE & Playground Guide

Welcome to the **Proompts Visual Studio IDE**! This dedicated visual guide outlines the core capabilities of the hosted interactive playground and the local desktop-equivalent editor built on Streamlit.

Our visual suite empowers prompt developers, software architects, and clinical regulators to author, sequence, simulate, and synchronize high-quality AI prompts and agentic workflows without touching raw YAML files directly.

## 🚀 Live Hosted Playground
Evaluate the prompt library instantly without cloning the repository! Access the hosted interactive playground here:
👉 **[Live Hosted Playground on Streamlit Cloud](https://share.streamlit.io/)**

---

## 🛠️ Local Desktop Setup & Run Instructions
For developers who want a local, private workspace with direct file system writes and integration with their local Git workflow, the entire visual IDE can be launched with a single command.

### Single-Step Launch Command
Utilize the workspace package manager **`uv`** to launch the local application instantly from the workspace root directory:

```bash
uv run streamlit run studio/studio/app.py
```

> **Note:** Ensure you have installed the workspace dependencies first by running `uv pip install -r requirements.txt` or simply let `uv run` fetch and isolate the correct environment automatically.

---

## 🧭 Core Editor Modules

The Proompts Studio is split into four integrated modules accessible from the sidebar. Each module is documented below with WCAG-compliant high-fidelity visual diagrams representing their layout and interactive functionalities.

### 1. Prompt Editor Module
The **Prompt Editor** is a dynamic form-based editor for authoring `.prompt.md` and `.prompt.yaml` assets. It enforces the repository's strict schemas while offering structured tabs for fields, metadata, user variable definitions, and system messages.

#### Key Features:
* **Interactive Form Inputs:** Direct fields for model selection, temperature, description, and metadata.
* **Structured Output Schema Toggle:** Checkbox to dynamically toggle and visualy edit output schemas.
* **Live Pydantic Validation:** Instant on-save feedback highlighting syntax or field errors.

#### Interface Visualization:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%" style="background-color: #0f172a; border-radius: 8px; font-family: system-ui, -apple-system, sans-serif;">
  <!-- Browser Frame -->
  <rect x="0" y="0" width="800" height="450" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
  <rect x="0" y="0" width="800" height="40" rx="8" fill="#1e293b"/>
  <circle cx="20" cy="20" r="6" fill="#ef4444"/>
  <circle cx="40" cy="20" r="6" fill="#f59e0b"/>
  <circle cx="60" cy="20" r="6" fill="#10b981"/>
  <text x="400" y="25" fill="#94a3b8" font-size="14" font-weight="bold" text-anchor="middle">Proompts Studio - Prompt Editor</text>
  
  <!-- Editor Sidebar / Select -->
  <rect x="20" y="60" width="760" height="45" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="40" y="87" fill="#94a3b8" font-size="13">Select a prompt to edit:</text>
  <rect x="200" y="68" width="560" height="28" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="215" y="86" fill="#f8fafc" font-size="13">prompts/technical/review.prompt.md</text>
  <path d="M740 78 l5 5 l5 -5" stroke="#38bdf8" stroke-width="2" fill="none"/>

  <!-- Tab Bar -->
  <rect x="20" y="120" width="760" height="35" rx="4" fill="#1e293b"/>
  <!-- Active Tab -->
  <rect x="20" y="120" width="150" height="35" rx="4" fill="#38bdf8" fill-opacity="0.15"/>
  <line x1="20" y1="155" x2="170" y2="155" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="95" y="142" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">Details &amp; Variables</text>
  <text x="245" y="142" fill="#94a3b8" font-size="13" text-anchor="middle">Messages</text>
  <text x="365" y="142" fill="#94a3b8" font-size="13" text-anchor="middle">MCP Tools</text>
  <text x="485" y="142" fill="#94a3b8" font-size="13" text-anchor="middle">Output Schema</text>
  <text x="635" y="142" fill="#94a3b8" font-size="13" text-anchor="middle">Test Data &amp; Evaluators</text>

  <!-- Form Fields -->
  <text x="40" y="195" fill="#94a3b8" font-size="12" font-weight="bold">FILE NAME</text>
  <rect x="40" y="205" width="340" height="35" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="55" y="227" fill="#f8fafc" font-size="13">review</text>

  <text x="420" y="195" fill="#94a3b8" font-size="12" font-weight="bold">SUBFOLDER</text>
  <rect x="420" y="205" width="340" height="35" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="435" y="227" fill="#f8fafc" font-size="13">technical</text>

  <text x="40" y="275" fill="#94a3b8" font-size="12" font-weight="bold">MODEL IDENTIFIER</text>
  <rect x="40" y="285" width="340" height="35" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="55" y="307" fill="#f8fafc" font-size="13">gpt-4o-mini</text>

  <!-- Checkbox -->
  <rect x="420" y="293" width="18" height="18" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="1.5"/>
  <path d="M424 302 l3 3 l6 -6" stroke="#0f172a" stroke-width="2" fill="none"/>
  <text x="450" y="307" fill="#f8fafc" font-size="13" font-weight="bold">Has Structured Output Schema</text>

  <!-- Success Banner -->
  <rect x="40" y="350" width="720" height="40" rx="6" fill="#065f46" stroke="#10b981" stroke-width="1"/>
  <circle cx="60" cy="370" r="8" fill="#10b981"/>
  <path d="M57 370 l2 2 l4 -4" stroke="#065f46" stroke-width="2" fill="none"/>
  <text x="80" y="375" fill="#34d399" font-size="13" font-weight="bold">Saved successfully and validated! (prompts/technical/review.prompt.md)</text>

  <!-- Bottom Buttons -->
  <rect x="640" y="405" width="120" height="32" rx="4" fill="#2563eb"/>
  <text x="700" y="425" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">Save Changes</text>
</svg>

---

### 2. Workflow composition Module
The **Workflow Composer** offers a visual multi-step builder layout for orchestrating prompt chains (`.workflow.yaml`). Complex workflows are modeled as consecutive steps, where output from one step can feed into the next step.

#### Key Features:
* **Step-by-Step Builders:** Add new execution steps visually, and select their prompt sources.
* **Sequencing Control:** Drag, drop, or utilize the unified sequence buttons (`Move Up`, `Move Down`) to adjust step ordering.
* **Deletion Hygiene:** Instantly drop steps with local state cleanup and cascade management.

#### Interface Visualization:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%" style="background-color: #0f172a; border-radius: 8px; font-family: system-ui, -apple-system, sans-serif;">
  <!-- Browser Frame -->
  <rect x="0" y="0" width="800" height="450" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
  <rect x="0" y="0" width="800" height="40" rx="8" fill="#1e293b"/>
  <circle cx="20" cy="20" r="6" fill="#ef4444"/>
  <circle cx="40" cy="20" r="6" fill="#f59e0b"/>
  <circle cx="60" cy="20" r="6" fill="#10b981"/>
  <text x="400" y="25" fill="#94a3b8" font-size="14" font-weight="bold" text-anchor="middle">Proompts Studio - Workflow Composer</text>

  <!-- Select Workflow Dropdown -->
  <rect x="20" y="60" width="760" height="45" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="40" y="87" fill="#94a3b8" font-size="13">Select a workflow to edit:</text>
  <rect x="200" y="68" width="560" height="28" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="215" y="86" fill="#f8fafc" font-size="13">workflows/clinical/consensus.workflow.yaml</text>
  <path d="M740 78 l5 5 l5 -5" stroke="#38bdf8" stroke-width="2" fill="none"/>

  <!-- Composer Step Sequence Layout -->
  <text x="40" y="135" fill="#94a3b8" font-size="12" font-weight="bold">WORKFLOW COMPOSITION STEPS</text>
  
  <!-- Step 1 Card -->
  <rect x="40" y="150" width="550" height="70" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <rect x="50" y="160" width="30" height="30" rx="15" fill="#38bdf8" fill-opacity="0.2"/>
  <text x="65" y="180" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">1</text>
  <text x="95" y="178" fill="#f8fafc" font-size="13" font-weight="bold">Step ID: oncologist_review</text>
  <text x="95" y="198" fill="#94a3b8" font-size="12">Prompt Source: prompts/clinical/safety/01_oncologist_review.prompt.yaml</text>
  <!-- Step 1 Reorder Buttons -->
  <rect x="600" y="150" width="80" height="30" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="640" y="169" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">⬆ Move Up</text>
  <rect x="690" y="150" width="90" height="30" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="735" y="169" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">⬇ Move Down</text>
  <rect x="600" y="190" width="180" height="30" rx="4" fill="#ef4444" fill-opacity="0.15" stroke="#ef4444" stroke-width="1"/>
  <text x="690" y="209" fill="#f87171" font-size="11" font-weight="bold" text-anchor="middle">🗑 Delete Step</text>

  <!-- Connection Arrow -->
  <path d="M315 220 L315 240 M310 235 L315 240 L320 235" stroke="#38bdf8" stroke-width="2" fill="none"/>

  <!-- Step 2 Card -->
  <rect x="40" y="245" width="550" height="70" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <rect x="50" y="255" width="30" height="30" rx="15" fill="#38bdf8" fill-opacity="0.2"/>
  <text x="65" y="275" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">2</text>
  <text x="95" y="273" fill="#f8fafc" font-size="13" font-weight="bold">Step ID: cardiologist_review</text>
  <text x="95" y="293" fill="#94a3b8" font-size="12">Prompt Source: prompts/clinical/safety/02_cardiologist_review.prompt.yaml</text>
  <!-- Step 2 Reorder Buttons -->
  <rect x="600" y="245" width="80" height="30" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="640" y="264" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">⬆ Move Up</text>
  <rect x="690" y="245" width="90" height="30" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="735" y="264" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">⬇ Move Down</text>
  <rect x="600" y="285" width="180" height="30" rx="4" fill="#ef4444" fill-opacity="0.15" stroke="#ef4444" stroke-width="1"/>
  <text x="690" y="304" fill="#f87171" font-size="11" font-weight="bold" text-anchor="middle">🗑 Delete Step</text>

  <!-- Add Step Node Button -->
  <rect x="40" y="330" width="550" height="35" rx="6" fill="#0f172a" stroke="#38bdf8" stroke-dasharray="4 4" stroke-width="1.5"/>
  <text x="315" y="352" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">+ Add Step to Sequence</text>

  <!-- Bottom Buttons -->
  <rect x="640" y="405" width="120" height="32" rx="4" fill="#2563eb"/>
  <text x="700" y="425" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">Save Workflow</text>
</svg>

---

### 3. Simulation Runner Module
The **Simulation Runner** executes local prompts and workflows in a completely sandboxed environment using mock LLM triggers. It is packed with sophisticated options to mimic production-level conditions and audits.

#### Advanced Runtime Capabilities:
1. **Simulated Chaotic Anomalies (Chaos Mode):** Inject unexpected API rate limits (HTTP 429) and network latency spikes. Developers can witness how their retry logic and backoff heuristics recover dynamically.
2. **Secure Compliance Reporting:** Generates 21 CFR Part 11 compliant cryptographically signed audit trails and verification reports for high-governance workspaces.
3. **Fidelity and Safety Audits:** Enforces runtime safety restrictions (like the *Aegis* safety guard) and outputs a detailed performance and compliance report.

#### Interface Visualization:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%" style="background-color: #0f172a; border-radius: 8px; font-family: system-ui, -apple-system, sans-serif;">
  <!-- Browser Frame -->
  <rect x="0" y="0" width="800" height="450" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
  <rect x="0" y="0" width="800" height="40" rx="8" fill="#1e293b"/>
  <circle cx="20" cy="20" r="6" fill="#ef4444"/>
  <circle cx="40" cy="20" r="6" fill="#f59e0b"/>
  <circle cx="60" cy="20" r="6" fill="#10b981"/>
  <text x="400" y="25" fill="#94a3b8" font-size="14" font-weight="bold" text-anchor="middle">Proompts Studio - Simulation Runner</text>

  <!-- Engine Options Sidebar (Left) -->
  <rect x="20" y="60" width="220" height="370" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="35" y="85" fill="#38bdf8" font-size="13" font-weight="bold">ENGINE OPTIONS</text>
  
  <!-- Chaos Mode Checkbox -->
  <rect x="35" y="110" width="16" height="16" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="1.5"/>
  <path d="M39 118 l3 3 l6 -6" stroke="#0f172a" stroke-width="2" fill="none"/>
  <text x="60" y="123" fill="#f8fafc" font-size="11" font-weight="bold">Enable Chaos Mode</text>
  <text x="60" y="138" fill="#94a3b8" font-size="10">(Simulate 429s &amp; latency)</text>

  <!-- Strict Mode Checkbox -->
  <rect x="35" y="170" width="16" height="16" rx="3" fill="#1e293b" stroke="#334155" stroke-width="1.5"/>
  <text x="60" y="183" fill="#94a3b8" font-size="11">Enable Strict Mode</text>

  <!-- Simulation Control Panel (Right) -->
  <rect x="260" y="60" width="520" height="370" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="280" y="85" fill="#f8fafc" font-size="13" font-weight="bold">Asset: workflows/clinical/consensus.workflow.yaml</text>
  
  <!-- Run Button -->
  <rect x="650" y="68" width="110" height="28" rx="4" fill="#2563eb"/>
  <text x="705" y="86" fill="#ffffff" font-size="12" font-weight="bold" text-anchor="middle">▶ Run Simulation</text>

  <!-- Console Log Terminal -->
  <text x="280" y="125" fill="#94a3b8" font-size="11" font-weight="bold">SIMULATION OUTPUT LOG</text>
  <rect x="280" y="135" width="480" height="150" rx="4" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="295" y="155" fill="#10b981" font-size="11" font-family="monospace">INFO: Starting workflow simulation: Clinical Consensus</text>
  <text x="295" y="175" fill="#f59e0b" font-size="11" font-family="monospace">WARNING: Chaos Mode active: Injecting 429 RateLimitException (Anomalies)...</text>
  <text x="295" y="195" fill="#38bdf8" font-size="11" font-family="monospace">INFO: Retry 1 of 3 triggered in 2.0s... Success (Secure compliance safe path)</text>
  <text x="295" y="215" fill="#10b981" font-size="11" font-family="monospace">INFO: oncologist_review step completed successfully.</text>
  <text x="295" y="235" fill="#38bdf8" font-size="11" font-family="monospace">INFO: compliance_check: Cryptographically signed audit trail generated.</text>
  <text x="295" y="255" fill="#10b981" font-size="11" font-family="monospace">SUCCESS: Simulation finished successfully.</text>

  <!-- Fidelity and Compliance Report Card -->
  <text x="280" y="312" fill="#94a3b8" font-size="11" font-weight="bold">SECURE COMPLIANCE &amp; FIDELITY REPORT</text>
  <rect x="280" y="322" width="480" height="90" rx="4" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <rect x="295" y="337" width="130" height="60" rx="4" fill="#1e293b" stroke="#10b981" stroke-width="1"/>
  <text x="360" y="355" fill="#10b981" font-size="18" font-weight="bold" text-anchor="middle">100%</text>
  <text x="360" y="375" fill="#94a3b8" font-size="11" text-anchor="middle">Safety Compliance</text>

  <rect x="445" y="337" width="130" height="60" rx="4" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
  <text x="510" y="355" fill="#38bdf8" font-size="18" font-weight="bold" text-anchor="middle">3 / 3</text>
  <text x="510" y="375" fill="#94a3b8" font-size="11" text-anchor="middle">Fidelity Tests Passed</text>

  <rect x="595" y="337" width="150" height="60" rx="4" fill="#1e293b" stroke="#10b981" stroke-width="1"/>
  <text x="670" y="355" fill="#10b981" font-size="14" font-weight="bold" text-anchor="middle">VERIFIED</text>
  <text x="670" y="375" fill="#94a3b8" font-size="11" text-anchor="middle">21 CFR Part 11 Audit Trail</text>
</svg>

---

### 4. Git Sync & Security Boundaries
The **Git Sync** page connects the visual editor directly to version control. It shows localized status, accepts descriptive commit messages, stages edited assets, and pushes changes securely.

#### 🛡️ Local Execution Security Boundaries
Security is paramount in the Proompts Visual Studio. Local execution is constrained by programmatic boundaries to enforce workspace separation and protect system integrity:
1. **Directory Restriction (Safe Paths):** The saving engines utilize `is_safe_path()` validation checks to verify that any target write path resolves strictly inside the repository's root `/app` directory. This programmatically blocks operations from accessing or overwriting system-critical locations.
2. **Path Traversal Eradication:** Inputs are pre-scanned using `has_path_traversal()` to block relative path segments (`..`). Save commands containing traversal sequences (e.g. `../etc/passwd` or `workflows/../../unsafe`) are immediately halted, raising explicit `Path validation failed` banners.

#### Interface & Security Boundary Visualization:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%" style="background-color: #0f172a; border-radius: 8px; font-family: system-ui, -apple-system, sans-serif;">
  <!-- Browser Frame -->
  <rect x="0" y="0" width="800" height="500" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
  <rect x="0" y="0" width="800" height="40" rx="8" fill="#1e293b"/>
  <circle cx="20" cy="20" r="6" fill="#ef4444"/>
  <circle cx="40" cy="20" r="6" fill="#f59e0b"/>
  <circle cx="60" cy="20" r="6" fill="#10b981"/>
  <text x="400" y="25" fill="#94a3b8" font-size="14" font-weight="bold" text-anchor="middle">Proompts Studio - Path Traversal Protection &amp; Git Sync</text>

  <!-- Left Side: Path Traversal Protection Diagram -->
  <rect x="20" y="60" width="370" height="420" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="40" y="85" fill="#ef4444" font-size="13" font-weight="bold">PATH TRAVERSAL PROTECTION BOUNDARY</text>

  <!-- Safe Workspace Box -->
  <rect x="40" y="105" width="330" height="100" rx="4" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="55" y="125" fill="#10b981" font-size="12" font-weight="bold">✓ SAFE WORKSPACE BOUNDARY (ROOT: /app)</text>
  <text x="55" y="150" fill="#f8fafc" font-size="11">Allows saving files to: prompts/ or workflows/</text>
  <text x="55" y="170" fill="#94a3b8" font-size="11">E.g., prompts/technical/test.prompt.md</text>
  <text x="55" y="190" fill="#34d399" font-size="10" font-weight="bold" font-family="monospace">is_safe_path("/app", "/app/prompts/test") -&gt; True</text>

  <!-- Blocked Out-of-Bounds Segment -->
  <rect x="40" y="225" width="330" height="100" rx="4" fill="#0f172a" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="55" y="245" fill="#ef4444" font-size="12" font-weight="bold">✗ RESTRICTED SYSTEM DIRECTORIES</text>
  <text x="55" y="270" fill="#f8fafc" font-size="11">Blocks directory traversal attempts outside /app</text>
  <text x="55" y="290" fill="#f87171" font-size="10" font-weight="bold" font-family="monospace">has_path_traversal("../etc/passwd") -&gt; True (BLOCKED)</text>
  <text x="55" y="310" fill="#f87171" font-size="10" font-weight="bold" font-family="monospace">is_safe_path("/app", "/etc/passwd") -&gt; False (BLOCKED)</text>

  <!-- Big Alert Shield -->
  <rect x="40" y="345" width="330" height="115" rx="4" fill="#7f1d1d" stroke="#ef4444" stroke-width="1"/>
  <path d="M65 375 L80 360 L95 375 L95 395 L80 410 L65 395 Z" fill="#ef4444"/>
  <text x="80" y="390" fill="#ffffff" font-size="14" font-weight="bold" text-anchor="middle">!</text>
  <text x="110" y="375" fill="#fca5a5" font-size="12" font-weight="bold">Path Traversal Blocked!</text>
  <text x="110" y="395" fill="#fca5a5" font-size="11">"Path validation failed: directory traversal</text>
  <text x="110" y="415" fill="#fca5a5" font-size="11">segments ('..') are not allowed."</text>

  <!-- Right Side: Git Sync Interface -->
  <rect x="410" y="60" width="370" height="420" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="430" y="85" fill="#38bdf8" font-size="13" font-weight="bold">DIRECTORY SYNCHRONIZATION (GIT SYNC)</text>

  <text x="430" y="120" fill="#94a3b8" font-size="12" font-weight="bold">CURRENT REPOSITORY STATUS</text>
  <rect x="430" y="130" width="330" height="80" rx="4" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="445" y="155" fill="#f59e0b" font-size="11" font-family="monospace">M prompts/clinical/review.prompt.md</text>
  <text x="445" y="175" fill="#34d399" font-size="11" font-family="monospace">A workflows/clinical/consensus.workflow.yaml</text>

  <text x="430" y="240" fill="#94a3b8" font-size="12" font-weight="bold">COMMIT MESSAGE</text>
  <rect x="430" y="250" width="330" height="35" rx="4" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="445" y="272" fill="#f8fafc" font-size="12">Update prompts via Proompts Studio</text>

  <!-- Sync Button -->
  <rect x="430" y="310" width="330" height="40" rx="4" fill="#2563eb"/>
  <text x="595" y="335" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">☁ Save &amp; Sync changes</text>

  <!-- Successful sync alert -->
  <rect x="430" y="370" width="330" height="90" rx="4" fill="#065f46" stroke="#10b981" stroke-width="1"/>
  <circle cx="455" cy="395" r="8" fill="#10b981"/>
  <path d="M452 395 l2 2 l4 -4" stroke="#065f46" stroke-width="2" fill="none"/>
  <text x="475" y="400" fill="#34d399" font-size="12" font-weight="bold">Successfully synced changes!</text>
  <text x="475" y="420" fill="#a7f3d0" font-size="11">Your updates are securely validated and</text>
  <text x="475" y="440" fill="#a7f3d0" font-size="11">pushed to the remote GitHub repository.</text>
</svg>
