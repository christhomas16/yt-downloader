document.getElementById('download-btn').addEventListener('click', () => {
    console.log("Download button clicked.");
    const url = document.getElementById('youtube-url').value;
    const message = document.getElementById('message');

    if (!url) {
        message.textContent = 'Please enter a YouTube URL.';
        console.log("URL input is empty.");
        return;
    }

    message.textContent = 'Downloading...';
    console.log(`Sending request to /download with URL: ${url}`);

    fetch('/download', {
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
            message.textContent = `Error: ${data.error}`;
        } else {
            message.innerHTML = `Download successful! <a href="/downloads/${data.filename}" download>Click here to download</a>`;
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
        message.textContent = `Error: ${error.message}`;
    });
}); 