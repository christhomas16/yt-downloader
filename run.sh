#!/bin/bash

# YouTube, Reddit, and X Video Downloader - Setup and Run Script
# This script sets up the virtual environment and runs the application

set -e  # Exit on any error

echo "🎬 Video Downloader Setup and Run Script"
echo "========================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

echo "✅ Found app.py in current directory"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create downloads directory if it doesn't exist
if [ ! -d "downloads" ]; then
    echo "📁 Creating downloads directory..."
    mkdir -p downloads
    echo "✅ Downloads directory created"
else
    echo "✅ Downloads directory already exists"
fi

echo ""
echo "🚀 Starting the Video Downloader application..."
echo "📍 The application will be available at: http://127.0.0.1:8080"
echo "📍 You can also access it at: http://localhost:8080"
echo ""
echo "📋 Features available:"
echo "   • YouTube video downloads"
echo "   • Reddit video downloads"
echo "   • X (Twitter) video downloads"
echo ""
echo "🛑 To stop the application, press Ctrl+C"
echo ""

# Run the application
python app.py 