#!/bin/bash

# Setup script for Mercari Product Explorer

echo "🚀 Setting up the project..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env from .example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️ Please update .env with your actual API keys."
fi

# Initialize database
echo "Initializing database..."
python populate_db.py

echo "✅ Setup complete!"
echo "To run the app: streamlit run streamlit_app.py"
