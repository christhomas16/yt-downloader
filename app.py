import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    logging.info(f"Received download request for URL: {url}")
    if not url:
        logging.error("URL is required but not provided.")
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'format': 'best'
        }
        with YoutubeDL(ydl_opts) as ydl:
            logging.info("Starting download with yt-dlp...")
            info_dict = ydl.extract_info(url, download=True)
            
            if 'entries' in info_dict:
                video_info = info_dict['entries'][0]
            else:
                video_info = info_dict

            filepath = video_info.get('filepath') or video_info.get('_filename')
            
            if not filepath:
                logging.warning("Could not determine final filepath from yt-dlp info. Falling back to constructing filename.")
                video_title = video_info.get('title', 'Unknown Title')
                video_ext = video_info.get('ext', 'mp4')
                filename = f"{video_title}.{video_ext}"
            else:
                filename = os.path.basename(filepath)

            logging.info(f"Download finished. Filename: {filename}")
            return jsonify({'message': 'Download successful', 'filename': filename})
    except Exception as e:
        logging.error(f"An error occurred during download: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080) 