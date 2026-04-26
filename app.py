import os
import logging
from flask import Flask, request, jsonify, send_from_directory, abort
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def _base_opts():
    return {
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        # Fetches the EJS challenge solver from GitHub (cached after first use).
        # Required for YouTube's signature/n-param decryption alongside Deno.
        'remote_components': ['ejs:github'],
    }


def _resolve_filename(info_dict, fallback_ext):
    if 'entries' in info_dict and info_dict['entries']:
        info_dict = info_dict['entries'][0]

    # requested_downloads is the most reliable source post-processing
    requested = info_dict.get('requested_downloads')
    if requested:
        filepath = requested[-1].get('filepath')
        if filepath:
            return os.path.basename(filepath)

    filepath = info_dict.get('filepath') or info_dict.get('_filename')
    if filepath:
        return os.path.basename(filepath)

    title = info_dict.get('title', 'Unknown')
    ext = info_dict.get('ext', fallback_ext)
    return f"{title}.{ext}"


@app.route('/download', methods=['POST'])
def download():
    """Download video from any yt-dlp supported site (YouTube, Reddit, X, etc.).

    yt-dlp auto-detects the source from the URL — no per-platform branching needed.
    """
    url = (request.json or {}).get('url')
    logging.info(f"Received video download request for URL: {url}")
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            **_base_opts(),
            'format': 'bestvideo*+bestaudio/best',
            'merge_output_format': 'mp4',
        }
        with YoutubeDL(ydl_opts) as ydl:
            logging.info("Starting video download with yt-dlp...")
            info_dict = ydl.extract_info(url, download=True)
            filename = _resolve_filename(info_dict, fallback_ext='mp4')
            logging.info(f"Video download finished. Filename: {filename}")
            return jsonify({'message': 'Download successful', 'filename': filename})
    except Exception as e:
        logging.error(f"An error occurred during video download: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download_audio', methods=['POST'])
def download_audio():
    """Download highest-quality audio from YouTube (or any yt-dlp supported site).

    Default behavior keeps the source codec (Opus or m4a/AAC) — no re-encoding,
    so this is bit-exact source quality. Pass {"format": "mp3"} to convert to
    MP3 320kbps for max compatibility (lossy re-encode).
    """
    payload = request.json or {}
    url = payload.get('url')
    out_format = (payload.get('format') or 'native').lower()

    logging.info(f"Received audio download request for URL: {url} (format={out_format})")
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if out_format == 'mp3':
        extract_audio_pp = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }
    else:
        # 'best' tells yt-dlp to keep the source codec without re-encoding,
        # picking the appropriate container (.opus for Opus, .m4a for AAC).
        extract_audio_pp = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'best',
        }
    postprocessors = [
        extract_audio_pp,
        {'key': 'FFmpegMetadata', 'add_metadata': True},
        {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
    ]

    try:
        ydl_opts = {
            **_base_opts(),
            'format': 'bestaudio/best',
            'writethumbnail': True,
            'postprocessors': postprocessors,
        }
        with YoutubeDL(ydl_opts) as ydl:
            logging.info("Starting audio download with yt-dlp...")
            info_dict = ydl.extract_info(url, download=True)
            filename = _resolve_filename(info_dict, fallback_ext='m4a')
            logging.info(f"Audio download finished. Filename: {filename}")
            return jsonify({'message': 'Download successful', 'filename': filename})
    except Exception as e:
        logging.error(f"An error occurred during audio download: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/downloads/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)


_STATIC_WHITELIST = {'script.js', 'style.css'}


@app.route('/<path:filename>')
def serve_static(filename):
    if filename not in _STATIC_WHITELIST:
        abort(404)
    return send_from_directory('.', filename)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
