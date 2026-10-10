#!/bin/bash

# Navigate to project root
cd /Users/onkardange/Documents/crmaai/memory_db || exit

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install required libraries silently
pip install -q fastapi uvicorn jinja2 pymongo python-dotenv python-multipart certifi dnspython

# Check if main.py exists and start server
if [ -f "app/main.py" ]; then
    echo "Starting Context & Memory UI Server on http://localhost:8000 ..."
    uvicorn app.main:app --reload
else
    echo "Error: app/main.py not found. Are you in the right directory?"
fi
