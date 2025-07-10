# YouTube, Reddit, and X Video Downloader

This is a simple web application that allows you to download videos from YouTube, Reddit, and X (Twitter).

## Features

- **YouTube Video Downloads**: Download videos from YouTube
- **Reddit Video Downloads**: Download videos from Reddit posts
- **X (Twitter) Video Downloads**: Download videos from X (Twitter) posts
- **Web Interface**: Easy-to-use web interface with tabbed navigation
- **Automatic Setup**: Simple setup script for quick installation

## Quick Start (Recommended)

1. **Clone or download this repository** to your local machine.

2. **Run the setup script** (macOS/Linux):
   ```bash
   ./run.sh
   ```
   
   Or on Windows (if you have Git Bash or WSL):
   ```bash
   bash run.sh
   ```

3. **Open the application** in your browser:
   ```
   http://127.0.0.1:8080
   ```

The script will automatically:
- Check for Python 3
- Create a virtual environment
- Install all dependencies
- Create the downloads directory
- Start the application

## Manual Setup

If you prefer to set up manually:

1. **Set up the project:**
   Clone or download this repository to your local machine.

2. **Create a virtual environment and install the dependencies:**
   Open a terminal and run the following command to create a virtual environment and install the necessary Python packages:
   ```bash
   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   ```

3. **Run the application:**
   In the same terminal (with the virtual environment activated), run the following command to start the Flask server:
   ```bash
   python app.py
   ```

4. **Open the application in your browser:**
   Open your web browser and go to the following address:
   ```
   http://127.0.0.1:8080
   ```

## How to use

1. **Select a platform**: Choose the appropriate tab (YouTube, Reddit, or X) for your video source.

2. **Enter the video URL**: Paste the video URL in the input field.

3. **Download the video**: Click the "Download" button and wait for the process to complete.

4. **Save the video**: After the download is complete, a link will appear. Click the link to download the video to your local drive. The downloaded video will be saved in the `downloads` folder in the same directory as the application.

## How to stop the application

To stop the application, you can press `Ctrl+C` in the terminal where the application is running, or you can kill the process. 