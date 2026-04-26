document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('active'));
            contents.forEach(item => item.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
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

    function handleDownload(endpoint, url, messageElement, extraPayload = {}) {
        if (!url) {
            messageElement.textContent = 'Please enter a URL.';
            console.log("URL input is empty.");
            return;
        }

        messageElement.textContent = 'Downloading...';
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
            if (data.error) {
                messageElement.textContent = `Error: ${data.error}`;
            } else {
                messageElement.innerHTML = `Download successful! <a href="/downloads/${data.filename}" download>Click here to download</a>`;
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            messageElement.textContent = `Error: ${error.message}`;
        });
    }
}); 