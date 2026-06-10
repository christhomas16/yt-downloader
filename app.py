import os
import logging
import subprocess
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
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


# Video extensions surfaced in the "strip to audio" dropdown.
_VIDEO_EXTS = {
    '.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv',
    '.m4v', '.ts', '.wmv', '.mpg', '.mpeg', '.3gp',
}

# Audio codec -> container that can hold it via stream copy (no re-encode).
# Mirrors what yt-dlp's FFmpegExtractAudio 'best' does for the download path.
# Unknown codecs fall back to Matroska audio (.mka), which accepts anything.
_AUDIO_EXT_BY_CODEC = {
    'aac': 'm4a',
    'alac': 'm4a',
    'opus': 'opus',
    'mp3': 'mp3',
    'vorbis': 'ogg',
    'flac': 'flac',
    'ac3': 'ac3',
    'eac3': 'eac3',
    'mp2': 'mp2',
    'pcm_s16le': 'wav',
    'pcm_s24le': 'wav',
}


def _safe_download_path(filename):
    """Resolve a user-supplied name to a path inside DOWNLOAD_FOLDER, or None.

    Guards against path traversal — the resolved path must stay within the
    downloads folder.
    """
    folder = os.path.abspath(app.config['DOWNLOAD_FOLDER'])
    path = os.path.abspath(os.path.join(folder, os.path.basename(filename)))
    if os.path.commonpath([folder, path]) != folder:
        return None
    return path


def _probe_audio_codec(path):
    """Return the codec_name of the first audio stream (e.g. 'aac', 'opus')."""
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
         '-show_entries', 'stream=codec_name',
         '-of', 'default=noprint_wrappers=1:nokey=1', path],
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def _strip_to_audio(src_path, out_format):
    """Remove the video stream from src_path, leaving audio. Returns out name.

    'native' copies the source audio codec (no re-encode) into the matching
    container; 'mp3' re-encodes to MP3 320kbps. Raises RuntimeError on failure.
    """
    folder = app.config['DOWNLOAD_FOLDER']
    stem = os.path.splitext(os.path.basename(src_path))[0]

    if out_format == 'mp3':
        ext = 'mp3'
        audio_args = ['-c:a', 'libmp3lame', '-b:a', '320k']
    else:
        codec = _probe_audio_codec(src_path)
        ext = _AUDIO_EXT_BY_CODEC.get(codec, 'mka')
        audio_args = ['-acodec', 'copy']

    out_name = f"{stem}.{ext}"
    out_path = os.path.join(folder, out_name)
    # Don't let ffmpeg read and write the same file (e.g. source is already .mp3).
    if os.path.abspath(out_path) == os.path.abspath(src_path):
        out_name = f"{stem}_audio.{ext}"
        out_path = os.path.join(folder, out_name)

    cmd = ['ffmpeg', '-y', '-i', src_path, '-vn', *audio_args, out_path]
    logging.info(f"Stripping to audio: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # ffmpeg's last stderr line is usually the actionable error.
        tail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'ffmpeg failed'
        raise RuntimeError(tail)
    return out_name


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
            # Prefer H.264 video + AAC audio so files play natively in
            # QuickTime / Apple ecosystem. Falls back to best-available if
            # H.264/AAC isn't offered (e.g. some Reddit/X clips).
            'format': (
                'bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/'
                'bestvideo[vcodec^=avc1]+bestaudio/'
                'best[vcodec^=avc1]/'
                'best'
            ),
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


@app.route('/list_downloads', methods=['GET'])
def list_downloads():
    """List video files already in downloads/, newest first.

    Powers the dropdown in the 'strip to audio' tab.
    """
    folder = app.config['DOWNLOAD_FOLDER']
    entries = []
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and os.path.splitext(name)[1].lower() in _VIDEO_EXTS:
            entries.append((name, os.path.getmtime(path)))
    entries.sort(key=lambda e: e[1], reverse=True)
    return jsonify({'files': [name for name, _ in entries]})


@app.route('/extract_audio', methods=['POST'])
def extract_audio():
    """Strip the video stream from a local file, leaving only audio.

    Two input modes:
      - multipart upload: form field 'file' (the video) + 'format'.
      - JSON {"filename": "...", "format": "..."} referencing a downloads/ file.
    'format' is 'native' (copy source audio codec) or 'mp3' (re-encode 320k).
    """
    upload = request.files.get('file')
    if upload and upload.filename:
        out_format = (request.form.get('format') or 'native').lower()
        safe_name = secure_filename(upload.filename) or 'upload'
        src_path = os.path.join(app.config['DOWNLOAD_FOLDER'], safe_name)
        upload.save(src_path)
        logging.info(f"Received uploaded video for audio extraction: {safe_name}")
    else:
        payload = request.get_json(silent=True) or {}
        filename = payload.get('filename')
        out_format = (payload.get('format') or 'native').lower()
        if not filename:
            return jsonify({'error': 'Select a downloaded video or upload a file.'}), 400
        src_path = _safe_download_path(filename)
        if not src_path or not os.path.isfile(src_path):
            return jsonify({'error': 'File not found'}), 404
        logging.info(f"Extracting audio from existing download: {os.path.basename(src_path)} (format={out_format})")

    try:
        out_name = _strip_to_audio(src_path, out_format)
        logging.info(f"Audio extraction finished. Filename: {out_name}")
        return jsonify({'message': 'Audio extracted', 'filename': out_name})
    except Exception as e:
        logging.error(f"An error occurred during audio extraction: {e}", exc_info=True)
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
