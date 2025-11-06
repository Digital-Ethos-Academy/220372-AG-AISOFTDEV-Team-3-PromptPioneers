# Steps to Run the Application

## Prerequisites
- Python 3.x installed
- Node.js and npm installed
- Git (for cloning the repository)

## Backend Setup
1. Create and activate virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1     # For Windows
    ```

2. Install backend dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set environment variables (required for AI features):
    ```bash
    # PowerShell (Windows)
    $env:ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
    ```

4. Start the backend server with uvicorn:
    ```bash
    # From project root directory
    .venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload  # Windows
    
    ```

## Frontend Setup
1. Install frontend dependencies (from project root):
    ```bash
    npm install
    ```

2. Start the frontend application:
    ```bash
    npm start
    ```

## Accessing the Application

Once both servers are running:
- **Frontend (React)**: http://localhost:3000
- **Backend API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

The React frontend will automatically proxy API requests to the backend server.

## Important Notes

- Make sure to set the `ANTHROPIC_API_KEY` environment variable before starting the backend
- The backend must be running on port 8000 for the frontend proxy to work
- Both servers support hot-reload for development
- Dependencies (LangGraph, LangChain, FAISS, etc.) will be auto-installed on first backend startup