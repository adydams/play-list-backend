#!/bin/bash

# Activate the virtual environment (Windows-specific)
echo "Activating virtual environment..."
source venv/Scripts/activate  # This is for Windows with a virtual environment

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development  # For development environment
export FLASK_DEBUG=1  # Enables debug mode

# Start the Flask server and display logs
echo "Starting Flask server..."
flask run --host=0.0.0.0 --port=5000

# Optionally, log output to a file
# flask run --host=0.0.0.0 --port=5000 > server.log 2>&1
