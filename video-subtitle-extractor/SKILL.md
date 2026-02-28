---
name: video-subtitle-extractor
description: Extracts text subtitles from video URLs (e.g., YouTube, Bilibili) using yt-dlp. Use this skill when the user asks you to summarize, analyze, or explain the content of a video URL. It converts subtitles into a readable text file and provides the path to the Agent.
license: MIT
compatibility: Requires python3, yt-dlp, webvtt-py, pysrt
metadata:
  author: Luffy Liu
  version: "1.0"
---

# Video Subtitle Extractor

## When to use this skill
Use this skill when the user provides a link to a video platform (like YouTube, Bilibili) and asks you to summarize, analyze, or explain the video's content.

## Setup and Prerequisites
Before running the script, make sure the dependencies are installed. You can install them by running:
```bash
pip install -r requirements.txt
```
*Note: Make sure your environment has `yt-dlp` working correctly.*

## How to use this skill
1. Run the provided Python script located at `scripts/extract_subtitles.py` from this skill directory.
   ```bash
   python3 scripts/extract_subtitles.py "<VIDEO_URL>"
   ```
2. The script will attempt to download the subtitles (auto-generated or manual) and convert the file to a plain text file, stripped of timestamps.
3. If successful, the script will output `SUCCESS` and print the `FILE_PATH` to the generated text file containing the subtitles.
4. Use the `view_file` tool to read the contents of the generated file.
5. Using the content from the file, answer the user's original prompt (e.g., summarize the video).
6. If the script fails or outputs that no subtitles are available, inform the user that you are unable to extract the subtitles and cannot analyze the video's content directly using this method. Suggest alternative ways if possible.

## Examples
User says: "Summarize this video: https://www.youtube.com/watch?v=C1GLT9_tag0"
You run:
```bash
python3 scripts/extract_subtitles.py "https://www.youtube.com/watch?v=C1GLT9_tag0"
```
You receive `FILE_PATH: /tmp/yt_sub_...txt`.
You use `view_file` on that path.
You reply to the user with the summary.
