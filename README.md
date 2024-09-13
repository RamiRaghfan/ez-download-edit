
# Video Content Downloader & Editor Backend

This project serves as the backend for a local web application that allows users to efficiently download and edit videos from various social media platforms on the fly. By leveraging `moviepy` for video processing, this tool automates content creation by downloading, renaming, merging, trimming, and managing videos, which can then be moved to a folder of choice over the network.

## Features

- **Download from Social Media**: Download videos from platforms like YouTube, TikTok, and more.
- **Automatic Video Processing**: Trim, merge, rename, and organize videos using `moviepy` to meet user needs.
- **Network File Transfer**: Downloaded and edited files can be moved to networked directories for easier management.
- **Flexible Workflow**: Customize video clipping and merging based on user-defined parameters.
- **Integration with JDownloader**: Downloads are managed through JDownloader 2's API, enabling robust support for handling links and packages.

## Prerequisites

Before running the project, make sure you have the following installed and set up:

1. **Python 3.x**: Install Python on your system. You can download it from [here](https://www.python.org/downloads/).
2. **JDownloader 2**: Download and install [JDownloader 2](https://jdownloader.org/download/index) on your system.
3. **MyJDownloader Account**: Register for a MyJDownloader account and create a device. This will allow the backend to communicate with JDownloader for managing downloads.
4. **Python Packages**: Required Python packages such as `myjdapi`, `moviepy`, and others can be installed by following the instructions below.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ez-downloader-editor.git
   cd ez-downloader-editor
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows use `myenv\Scriptsctivate`
   ```

3. **Install dependencies**:
   Install the required Python packages using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure JDownloader credentials**:
   In the `connection.py` file, make sure to provide your MyJDownloader email, password, and device name:
   ```python
   email = "your_email"
   password = "your_password"
   device_name = "your_device_name"
   ```

## Running the Application

To run the backend, use the following command in your terminal:

```bash
python main.py
```

This will start the application, connect to your MyJDownloader device, and begin processing the download and video editing tasks as per the specified JSON input files.

## How It Works

1. **Download Videos**: The application interacts with MyJDownloader's API to fetch video links from various platforms (e.g., YouTube, TikTok).
2. **Process Videos**: Using the `moviepy` library, the videos are trimmed, merged, and renamed according to the user-defined clip groups in the input JSON files.
3. **Organize Files**: The final video files are saved in organized directories, with options to move them to a network location for easy access.

## JSON Input Structure

Each task is defined in a JSON file with the following structure:

```json
{
  "package": {
    "links": [
      {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "clipGroups": [
          {
            "clips": [
              { "start": "00:00", "end": "00:30" },
              { "start": "01:00", "end": "01:30" }
            ],
            "merge": true,
            "renameGroup": "MyMergedClip"
          }
        ]
      }
    ],
    "globalMergeAll": true,
    "globalMergedTitle": "FinalMergedVideo"
  }
}
```

In this structure:
- **links**: The list of video URLs to download.
- **clipGroups**: Defines the clips (start and end times) and whether they should be merged.
- **globalMergeAll**: If set to `true`, all videos will be merged into a single final video.
- **globalMergedTitle**: The name of the final merged video.

## Troubleshooting

1. **Authentication Issues**: If you face authentication issues, ensure that your MyJDownloader credentials are correctly entered in the `connection.py` file. Also, ensure that JDownloader is running and connected to your MyJDownloader account, otherwise restart Jdownlaoder 2 with the inbuilt restart feature.
2. **Missing Dependencies**: If the application throws an error related to missing Python packages, ensure that you've installed all dependencies from the `requirements.txt` file using `pip install -r requirements.txt`.
