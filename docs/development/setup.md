# Development Environment Setup Guide

**Project:** Cryptographic Integrity Toolkit  
**Sprint ID:** CL-00 / S00  

---

## 1. Environment Prerequisites

Ensure the following tools are installed on your host system:
- **Python:** Version `3.11` or higher (`python --version`)
- **Git:** Version `2.30` or higher (`git --version`)
- **Shell:** PowerShell 7+ on Windows, or Bash on Linux/macOS

---

## 2. Step-by-Step Setup

### Step 1: Clone the Repository

```powershell
git clone <repository-url>
cd cryptographic-integrity-toolkit

```

### Step 2: Create a Local Virtual Environment

Isolate project dependencies using standard `venv`:

```powershell
# Create .venv
python -m venv .venv

```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1

```

**Linux / macOS (Bash):**

```bash
source .venv/bin/activate

```

### Step 4: Upgrade Package Installer

```powershell
python -m pip install --upgrade pip

```

### Step 5: Install Development Dependencies

```powershell
python -m pip install -r requirements-dev.txt

```

### Step 6: Install Package in Editable Mode

Install the local package in editable mode (`-e`) so changes to `src/` are immediately reflected:

```powershell
python -m pip install -e .

```

---

## 3. Environment Verification

To verify that your local environment is correctly configured, run the following commands:

### 3.1 Verify CLI Entry Point

```powershell
integrity --version
# Expected output: integrity 0.0.1

integrity --help
# Expected output: top-level CLI help menu

```

### 3.2 Run Test Suite

```powershell
pytest -v
# Expected output: All tests under tests/ pass cleanly

```

---

## 4. Common Troubleshooting

### Execution Policy Restrictions (Windows PowerShell)

If PowerShell blocks virtual environment activation script execution (`Activate.ps1`):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

```

### Module Not Found Errors

Ensure the virtual environment is activated and that `python -m pip install -e .` has been executed.

```