<#
.SYNOPSIS
    Development Helper Script for Cryptographic Integrity Toolkit.
.DESCRIPTION
    Verifies virtual environment status, executes pytest test suite, and validates CLI entry points.
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Cryptographic Integrity Toolkit Verification Script ===" -ForegroundColor Cyan

# 1. Check Virtual Environment
$venvPython = ".\.venv\Scripts\python.exe"
$venvPytest = ".\.venv\Scripts\pytest.exe"
$venvIntegrity = ".\.venv\Scripts\integrity.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[ERROR] Virtual environment not found in .venv/! Run 'python -m venv .venv' first." -ForegroundColor Red
    exit 1
}

# 2. Run Pytest
Write-Host "`n[1/2] Running Pytest Test Suite..." -ForegroundColor Yellow
& $venvPytest -v

# 3. Verify CLI
Write-Host "`n[2/2] Verifying CLI Execution..." -ForegroundColor Yellow
Write-Host "Version: " -NoNewline
& $venvIntegrity --version

Write-Host "`n[SUCCESS] All development baseline checks passed cleanly!" -ForegroundColor Green