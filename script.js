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

    // Reddit Downloader
    document.getElementById('reddit-download-btn').addEventListener('click', () => {
        console.log("Reddit download button clicked.");
        const url = document.getElementById('reddit-url').value;
        const message = document.getElementById('reddit-message');
        handleDownload('/download_reddit', url, message);
    });

    function handleDownload(endpoint, url, messageElement) {
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
            body: JSON.stringify({ url: url })
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