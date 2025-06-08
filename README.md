# YouTube Video Downloader

This is a simple web application that allows you to download YouTube videos.

## How to use

1.  **Set up the project:**
    Clone or download this repository to your local machine.

2.  **Create a virtual environment and install the dependencies:**
    Open a terminal and run the following command to create a virtual environment and install the necessary Python packages:
    ```bash
    python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
    ```

3.  **Run the application:**
    In the same terminal (with the virtual environment activated), run the following command to start the Flask server:
    ```bash
    python app.py
    ```

4.  **Open the application in your browser:**
    Open your web browser and go to the following address:
    ```
    http://127.0.0.1:8080
    ```

5.  **Download a video:**
    You should now see the YouTube Video Downloader application. You can enter a YouTube video URL in the input field and click the "Download" button to download the video.

6.  **Save the video:**
    After the download is complete, a link will appear. Click the link to download the video to your local drive. The downloaded video will be saved in the `downloads` folder in the same directory as the application.

## How to stop the application

To stop the application, you can press `Ctrl+C` in the terminal where the application is running, or you can kill the process. 