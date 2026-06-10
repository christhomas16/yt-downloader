document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('active'));
            contents.forEach(item => item.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');

            // Refresh the dropdown so freshly downloaded videos show up.
            if (tab.dataset.tab === 'extract') {
                loadDownloadsList();
            }
        });
    });

    // YouTube Downloader
    document.getElementById('youtube-download-btn').addEventListener('click', () => {
        console.log("YouTube download button clicked.");
        const url = document.getElementById('youtube-url').value;
        const message = document.getElementById('youtube-message');
        handleDownload('/download', url, message);
    });

    // Reddit Downloader (uses unified /download endpoint — yt-dlp auto-detects source)
    document.getElementById('reddit-download-btn').addEventListener('click', () => {
        console.log("Reddit download button clicked.");
        const url = document.getElementById('reddit-url').value;
        const message = document.getElementById('reddit-message');
        handleDownload('/download', url, message);
    });

    // X (Twitter) Downloader (uses unified /download endpoint)
    document.getElementById('x-download-btn').addEventListener('click', () => {
        console.log("X download button clicked.");
        const url = document.getElementById('x-url').value;
        const message = document.getElementById('x-message');
        handleDownload('/download', url, message);
    });

    // Audio Downloader
    document.getElementById('audio-download-btn').addEventListener('click', () => {
        console.log("Audio download button clicked.");
        const url = document.getElementById('audio-url').value;
        const message = document.getElementById('audio-message');
        const format = document.querySelector('input[name="audio-format"]:checked').value;
        handleDownload('/download_audio', url, message, { format });
    });

    // Strip to Audio — operates on a local file, not a URL.
    loadDownloadsList();
    document.getElementById('extract-btn').addEventListener('click', () => {
        console.log("Strip to Audio button clicked.");
        const message = document.getElementById('extract-message');
        const format = document.querySelector('input[name="extract-format"]:checked').value;
        const fileInput = document.getElementById('extract-upload');
        const selected = document.getElementById('extract-file-select').value;

        if (fileInput.files.length > 0) {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('format', format);
            setMessage(message, 'loading', 'Extracting audio…');
            fetch('/extract_audio', { method: 'POST', body: formData })
                .then(response => response.json())
                .then(data => renderResult(message, data))
                .catch(error => {
                    console.error("Fetch error:", error);
                    setMessage(message, 'error', `Error: ${error.message}`);
                });
        } else if (selected) {
            setMessage(message, 'loading', 'Extracting audio…');
            fetch('/extract_audio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: selected, format })
            })
                .then(response => response.json())
                .then(data => renderResult(message, data))
                .catch(error => {
                    console.error("Fetch error:", error);
                    setMessage(message, 'error', `Error: ${error.message}`);
                });
        } else {
            setMessage(message, 'error', 'Select a downloaded video or choose a file to upload.');
        }
    });

    function loadDownloadsList() {
        const select = document.getElementById('extract-file-select');
        if (!select) return;
        fetch('/list_downloads')
            .then(response => response.json())
            .then(data => {
                const current = select.value;
                select.innerHTML = '<option value="">— select a downloaded video —</option>';
                (data.files || []).forEach(name => {
                    const option = document.createElement('option');
                    option.value = name;
                    option.textContent = name;
                    select.appendChild(option);
                });
                // Preserve the user's selection across a refresh if still present.
                if (current) select.value = current;
            })
            .catch(error => console.error("Failed to load downloads list:", error));
    }

    function setMessage(messageElement, state, text) {
        messageElement.className = `message ${state}`;
        messageElement.textContent = text;
    }

    function renderResult(messageElement, data) {
        if (data.error) {
            setMessage(messageElement, 'error', `⚠ ${data.error}`);
        } else {
            messageElement.className = 'message success';
            const href = `/downloads/${encodeURIComponent(data.filename)}`;
            messageElement.innerHTML =
                `<span class="msg-text">✓ Saved</span>` +
                `<a href="${href}" download>Download ${data.filename}</a>`;
        }
    }

    function handleDownload(endpoint, url, messageElement, extraPayload = {}) {
        if (!url) {
            setMessage(messageElement, 'error', 'Please enter a URL.');
            console.log("URL input is empty.");
            return;
        }

        setMessage(messageElement, 'loading', 'Downloading…');
        console.log(`Sending request to ${endpoint} with URL: ${url}`);

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url, ...extraPayload })
        })
        .then(response => {
            console.log("Received response from server.");
            return response.json();
        })
        .then(data => {
            console.log("Parsed JSON data:", data);
            renderResult(messageElement, data);
        })
        .catch(error => {
            console.error("Fetch error:", error);
            setMessage(messageElement, 'error', `Error: ${error.message}`);
        });
    }
}); 