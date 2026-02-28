#!/usr/bin/env python3
import sys
import subprocess
import os
import glob
import tempfile
import json
from pathlib import Path

def print_error(msg):
    print(f"Error: {msg}")
    sys.exit(0)

def extract_subtitles(url):
    tmp_dir = tempfile.mkdtemp(prefix='yt_sub_')
    
    print(f"Fetching subtitles for URL: {url} ...")
    
    # We prefer vtt/srt formats
    output_template = os.path.join(tmp_dir, "%(id)s.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--write-subs",
        "--sub-format", "vtt/srt/json/best",
        "--extractor-args", "youtube:player_client=default,ios",
        "--skip-download",
        "-o", output_template,
        url
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        print_error("yt-dlp is not installed or not in PATH.")

    # Check for downloaded subtitle files
    # yt-dlp might download formats like `<id>.<lang>.vtt` or `<id>.json`
    sub_files = []
    for ext in ('*.vtt', '*.srt', '*.json', '*.xml'):
        sub_files.extend(glob.glob(os.path.join(tmp_dir, ext)))
    
    if not sub_files:
        print_error("Failed to download subtitles. The video might not have subtitles, or it requires login (e.g., Bilibili). Output from yt-dlp:\n" + result.stderr)
        
    # We will process the first subtitle file we find
    sub_file = sub_files[0]
    output_txt = os.path.join(tmp_dir, f"{Path(sub_file).stem}_subtitles.txt")
    
    converted = False
    
    if sub_file.endswith('.vtt'):
        try:
            import webvtt
            vtt = webvtt.read(sub_file)
            with open(output_txt, 'w', encoding='utf-8') as f:
                last_line = None
                for caption in vtt:
                    text_block = caption.text.strip()
                    for line in text_block.split('\n'):
                        line = line.strip()
                        if line and line != last_line:
                            # remove some common formatting from youtube
                            line = line.replace('<c>', '').replace('</c>', '')
                            f.write(line + "\n")
                            last_line = line
            converted = True
        except ImportError:
            print_error("webvtt-py is not installed. Please install it with 'pip install webvtt-py'")
        except Exception as e:
            print_error(f"Failed to parse VTT file: {e}")
            
    elif sub_file.endswith('.srt'):
        try:
            import pysrt
            subs = pysrt.open(sub_file)
            with open(output_txt, 'w', encoding='utf-8') as f:
                last_line = None
                for sub in subs:
                    text_block = sub.text.strip()
                    for line in text_block.split('\n'):
                        line = line.strip()
                        if line and line != last_line:
                            f.write(line + "\n")
                            last_line = line
            converted = True
        except ImportError:
            # Fallback if pysrt is missing
            with open(sub_file, 'r', encoding='utf-8') as f, open(output_txt, 'w', encoding='utf-8') as out:
                for line in f:
                    if not line.strip().isdigit() and '-->' not in line:
                        out.write(line)
            converted = True
        except Exception as e:
            print_error(f"Failed to parse SRT file: {e}")
            
    elif sub_file.endswith('.json'):
        try:
            with open(sub_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(output_txt, 'w', encoding='utf-8') as f:
                if isinstance(data, dict) and 'events' in data: # Youtube json format
                    for event in data['events']:
                        if 'segs' in event:
                            text = "".join([s.get('utf8', '') for s in event['segs']])
                            f.write(text + "\n")
                elif isinstance(data, list): # generic json array
                    for item in data:
                        if isinstance(item, dict) and 'content' in item:
                            f.write(item['content'] + "\n")
            converted = True
        except Exception as e:
            print_error(f"Failed to parse JSON file: {e}")
            
    elif sub_file.endswith('.xml'):
        # For bilibili danmaku or subtitle, we do basic regex extraction
        import re
        try:
            with open(sub_file, 'r', encoding='utf-8') as f:
                content = f.read()
            matches = re.findall(r'<d p=".*?">(.*?)</d>', content)
            if not matches:
                # Try standard XML text extraction
                matches = re.findall(r'>([^<]+)</', content)
                
            with open(output_txt, 'w', encoding='utf-8') as f:
                for text in matches:
                    text = text.strip()
                    if text and not text.isdigit():
                        f.write(text + "\n")
            converted = True
        except Exception as e:
            print_error(f"Failed to parse XML file: {e}")
            
    if not converted:
        print_error(f"Could not convert downloaded subtitle file: {sub_file}")
        
    print(f"SUCCESS: Subtitles extracted and converted to clear text.")
    print(f"FILE_PATH: {output_txt}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_error("Usage: python3 extract_subtitles.py <VIDEO_URL>")
    
    video_url = sys.argv[1]
    extract_subtitles(video_url)
