# PowerShell script to run the FastAPI backend
# Usage: .\run_backend.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Healthcare Chatbot Backend API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and configure your API keys" -ForegroundColor Yellow
    Write-Host ""
    
    $create = Read-Host "Would you like to create .env from .env.example? (y/n)"
    if ($create -eq "y") {
        Copy-Item ".env.example" ".env"
        Write-Host ".env file created. Please edit it with your API keys before continuing." -ForegroundColor Green
        Write-Host ""
        exit
    }
}

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "No virtual environment found. Consider creating one with:" -ForegroundColor Yellow
    Write-Host "python -m venv venv" -ForegroundColor Yellow
    Write-Host ""
}

# Check if dependencies are installed
$dependencies_ok = $true
$required_packages = @("fastapi", "uvicorn", "langchain", "langgraph", "supabase", "web3")

foreach ($package in $required_packages) {
    $installed = python -c "import $package" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Missing package: $package" -ForegroundColor Red
        $dependencies_ok = $false
    }
}

if (-Not $dependencies_ok) {
    Write-Host ""
    Write-Host "Some dependencies are missing. Install them with:" -ForegroundColor Yellow
    Write-Host "pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    
    $install = Read-Host "Would you like to install dependencies now? (y/n)"
    if ($install -eq "y") {
        Write-Host "Installing dependencies..." -ForegroundColor Green
        pip install -r requirements.txt
    } else {
        exit
    }
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "API Documentation will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the FastAPI server
python backend_api.py
