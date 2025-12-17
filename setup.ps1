# Quick Installation Script for Healthcare Chatbot Backend
# Run this script to set up everything automatically

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Healthcare Chatbot Backend - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python version
Write-Host "Step 1: Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Green

$versionNumber = [regex]::Match($pythonVersion, '\d+\.\d+').Value
if ([double]$versionNumber -lt 3.10) {
    Write-Host "  ERROR: Python 3.10 or higher required!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python version OK" -ForegroundColor Green
Write-Host ""

# Step 2: Create virtual environment
Write-Host "Step 2: Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Step 4: Install dependencies
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
pip install --upgrade pip -q
pip install -r requirements.txt -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: Create .env file
Write-Host "Step 5: Setting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  .env file already exists" -ForegroundColor Gray
} else {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ .env file created from template" -ForegroundColor Green
        Write-Host ""
        Write-Host "  IMPORTANT: Edit .env file and add your API keys!" -ForegroundColor Yellow
        Write-Host "  Required: OPENAI_API_KEY" -ForegroundColor Yellow
    } else {
        Write-Host "  WARNING: .env.example not found" -ForegroundColor Yellow
    }
}
Write-Host ""

# Step 6: Verify installation
Write-Host "Step 6: Verifying installation..." -ForegroundColor Yellow
$testImport = python -c "from backend_api import app; from agent_graph import healthcare_agent; from models import ChatRequest; print('OK')" 2>&1
if ($testImport -match "OK") {
    Write-Host "  ✓ All imports successful" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Import test failed" -ForegroundColor Red
    Write-Host "  $testImport" -ForegroundColor Red
}
Write-Host ""

# Step 7: Check syntax
Write-Host "Step 7: Checking code syntax..." -ForegroundColor Yellow
python -m py_compile backend_api.py 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ backend_api.py - OK" -ForegroundColor Green
}
python -m py_compile agent_graph.py 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ agent_graph.py - OK" -ForegroundColor Green
}
python -m py_compile models.py 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ models.py - OK" -ForegroundColor Green
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env is configured
$envConfigured = $false
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        $envConfigured = $true
    }
}

if ($envConfigured) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
    Write-Host "✓ Virtual environment ready" -ForegroundColor Green
    Write-Host "✓ Environment configured" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to start the server!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Run: python backend_api.py" -ForegroundColor Yellow
    Write-Host "Or:  uvicorn backend_api:app --reload" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
    Write-Host "✓ Virtual environment ready" -ForegroundColor Green
    Write-Host "⚠ Environment needs configuration" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Edit .env file and add your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "2. Run: python backend_api.py" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Need help? Check:" -ForegroundColor Gray
Write-Host "  - DRY_RUN_REPORT.md" -ForegroundColor Gray
Write-Host "  - QUICKSTART.md" -ForegroundColor Gray
Write-Host "  - README.md" -ForegroundColor Gray
Write-Host ""
