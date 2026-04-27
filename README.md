# YouTube, Reddit, and X Video & Audio Downloader

A simple web application for downloading videos from YouTube, Reddit, and X (Twitter), plus high-quality audio from YouTube.

## Features

- **YouTube Video Downloads**: Download videos from YouTube
- **Reddit Video Downloads**: Download videos from Reddit posts
- **X (Twitter) Video Downloads**: Download videos from X (Twitter) posts
- **Audio Downloads (Music)**: Pull highest-quality audio from YouTube — keep the source codec (Opus/m4a, no re-encode) or convert to MP3 320kbps for max compatibility. Thumbnails and metadata are embedded.
- **Apple-friendly video output**: Prefers H.264 + AAC in an MP4 container so files play natively in QuickTime and across the Apple ecosystem, falling back to best-available when the source doesn't offer it.
- **Web Interface**: Easy-to-use tabbed interface
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

## Requirements

- **Python 3**
- **ffmpeg** — required for merging video/audio streams and for audio extraction/conversion. Install via `brew install ffmpeg` (macOS), `apt install ffmpeg` (Debian/Ubuntu), or [ffmpeg.org](https://ffmpeg.org/download.html).
- **Deno** — required by yt-dlp for YouTube's signature/n-param decryption. Install via `brew install deno` or from [deno.land](https://deno.land/).

## Manual Setup

If you prefer to set up manually:

1. **Set up the project:**
   Clone or download this repository to your local machine.

2. **Create a virtual environment and install the dependencies:**
   ```bash
   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open the application in your browser:**
   ```
   http://127.0.0.1:8080
   ```

## How to use

### Video downloads (YouTube / Reddit / X)

1. **Select a platform**: Choose the tab for your video source.
2. **Enter the video URL**: Paste the URL into the input field.
3. **Download**: Click "Download" and wait for the process to finish.
4. **Save the file**: A link will appear when the download completes — click it to save the video locally. Files are written to the `downloads/` folder next to the application.

### Audio downloads (Music)

1. Open the **Audio (Music)** tab.
2. Paste a YouTube URL.
3. Choose a format:
   - **Native (Opus/m4a)** — bit-exact source quality, no re-encoding. Recommended for best fidelity.
   - **MP3 320kbps** — lossy re-encode, broadest compatibility (older devices, DJ software, etc.).
4. Click **Download Audio**. The output file embeds the thumbnail as cover art and includes track metadata.

## How to stop the application

Press `Ctrl+C` in the terminal where the application is running, or kill the process.
