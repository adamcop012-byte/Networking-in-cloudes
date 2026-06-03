#!/bin/bash
set -e
echo "Starting ERP service..."
echo "Python version: $(python --version)"
echo "Uvicorn version: $(python -m pip show uvicorn | grep Version)"
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la
echo "Starting uvicorn..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000

