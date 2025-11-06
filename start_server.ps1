# PowerShell script to start the FastAPI server
Write-Host "Starting FastAPI Server..." -ForegroundColor Green
Write-Host "=" * 60
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=" * 60
Write-Host ""

# Activate virtual environment and run uvicorn
& ".\\.venv\\Scripts\\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
