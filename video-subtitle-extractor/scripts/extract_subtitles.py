#!/usr/bin/env python3
"""
Video Subtitle Extractor - Robust subtitle extraction from video platforms.

Features:
  - Tiered retry with browser cookie authentication (Chrome → Firefox)
  - Smart subtitle language detection via --list-subs probing
  - Comprehensive HTML/XML tag cleaning
  - Clear diagnostic error messages
"""
import sys
import subprocess
import os
import re
import glob
import tempfile
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Language preference order (highest priority first)
PREFERRED_LANGS = ["zh-Hans", "zh", "zh-CN", "zh-Hant", "zh-TW", "en"]

# Browsers to try for cookie-based authentication, in order
COOKIE_BROWSERS = ["chrome", "firefox", "edge", "safari"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_error(msg):
    print(f"Error: {msg}")
    sys.exit(0)


def clean_html_tags(text: str) -> str:
    """Remove all HTML/XML tags from text (e.g. <c>, <font>, position tags)."""
    return re.sub(r"<[^>]+>", "", text)


def run_yt_dlp(args: list[str], quiet: bool = False) -> subprocess.CompletedProcess:
    """Run yt-dlp with the given arguments and return the result."""
    cmd = ["yt-dlp"] + args
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        print_error("yt-dlp is not installed or not in PATH.")


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_available_languages(url: str, extra_args: list[str] | None = None) -> list[str]:
    """
    Use `yt-dlp --list-subs` to discover available subtitle languages.
    Returns a list of language codes (e.g. ['zh-Hans', 'en']).
    """
    # BCP-47 language code pattern (e.g. 'zh', 'zh-Hans', 'zh-TW', 'en', 'pt-BR')
    lang_code_re = re.compile(r"^[a-zA-Z]{2,4}(-[a-zA-Z]{2,5})?$")

    args = ["--list-subs", "--skip-download"] + (extra_args or []) + [url]
    result = run_yt_dlp(args)
    # Only parse stdout — stderr contains Python warnings and yt-dlp debug output
    output = result.stdout

    # Parse the "Available subtitles" section
    # Lines look like: "zh-Hans  Chinese (Simplified) vtt, srt, ..."
    langs = []
    in_available = False
    for line in output.splitlines():
        if "Available subtitles" in line:
            in_available = True
            continue
        if in_available:
            # Skip header lines like "Language Name  Formats"
            parts = line.strip().split()
            if parts and not parts[0].startswith("-") and parts[0] != "Language":
                lang_code = parts[0]
                # Validate: must look like a BCP-47 language code
                if not lang_code_re.match(lang_code):
                    continue
                # Skip translated subtitle entries like "en-zh-Hans" (translations from another lang)
                if "-" in lang_code and lang_code.count("-") >= 2:
                    continue
                langs.append(lang_code)
    return langs


def pick_best_language(available: list[str]) -> str | None:
    """Pick the best subtitle language from available ones based on preference order."""
    for preferred in PREFERRED_LANGS:
        if preferred in available:
            return preferred
    # If none of the preferred languages match, return the first available one
    return available[0] if available else None


# ---------------------------------------------------------------------------
# Subtitle download with tiered retry
# ---------------------------------------------------------------------------

def try_download_subtitles(url: str, tmp_dir: str, sub_lang: str | None, cookie_browser: str | None = None) -> tuple[bool, str, list[str]]:
    """
    Attempt to download subtitles. Returns (success, stderr_output, subtitle_files).
    """
    output_template = os.path.join(tmp_dir, "%(id)s.%(ext)s")

    args = [
        "--write-subs",
        "--write-auto-subs",
        "--sub-format", "vtt/srt/json/best",
        "--skip-download",
        "-o", output_template,
    ]

    if sub_lang:
        args += ["--sub-lang", sub_lang]

    if cookie_browser:
        args += ["--cookies-from-browser", cookie_browser]

    args.append(url)

    result = run_yt_dlp(args)

    # Check for downloaded subtitle files
    sub_files = []
    for ext in ("*.vtt", "*.srt", "*.json", "*.xml"):
        sub_files.extend(glob.glob(os.path.join(tmp_dir, ext)))

    success = len(sub_files) > 0
    return success, result.stderr, sub_files


def download_subtitles(url: str, tmp_dir: str) -> list[str]:
    """
    Download subtitles with tiered retry strategy:
      1. Direct download (no cookies)
      2. With Chrome cookies
      3. With Firefox cookies
      4. With other browsers (edge, safari)

    At each tier, language detection is attempted first.
    """
    attempts = []

    # Build list of auth strategies to try
    auth_strategies = [None] + COOKIE_BROWSERS  # None = no cookies

    for browser in auth_strategies:
        strategy_name = f"cookies from {browser}" if browser else "direct (no cookies)"
        extra_args = ["--cookies-from-browser", browser] if browser else []

        # Step 1: Detect available languages
        print(f"  → Strategy: {strategy_name}")
        available_langs = detect_available_languages(url, extra_args or None)

        if available_langs:
            best_lang = pick_best_language(available_langs)
            print(f"    Available languages: {available_langs[:10]}{'...' if len(available_langs) > 10 else ''}")
            print(f"    Selected language: {best_lang}")
        else:
            best_lang = None
            print(f"    No language info detected, trying default download...")

        # Step 2: Try downloading
        # Use a fresh sub-dir for each attempt to avoid stale files
        attempt_dir = tempfile.mkdtemp(prefix="yt_sub_attempt_", dir=tmp_dir)
        success, stderr, sub_files = try_download_subtitles(
            url, attempt_dir, sub_lang=best_lang, cookie_browser=browser
        )

        if success:
            print(f"    ✓ Download succeeded!")
            return sub_files

        # Check if it's an auth error (sign-in required)
        is_auth_error = "Sign in to confirm" in stderr or "sign in" in stderr.lower()
        attempts.append({
            "strategy": strategy_name,
            "error": "Authentication required" if is_auth_error else "No subtitles found",
            "stderr_snippet": stderr.strip()[-200:] if stderr else "(no output)",
        })

        if is_auth_error and browser is None:
            print(f"    ✗ Authentication required, will retry with browser cookies...")
            continue
        elif not success and not is_auth_error:
            # Not an auth error — different browsers won't help, but language might differ
            print(f"    ✗ No subtitles found with this strategy.")
            if browser is not None:
                # Already tried with cookies, stop trying more browsers
                break
            continue

    # All attempts failed — produce diagnostic output
    print("\n" + "=" * 60)
    print("ALL DOWNLOAD ATTEMPTS FAILED")
    print("=" * 60)
    for i, attempt in enumerate(attempts, 1):
        print(f"\n  Attempt {i} ({attempt['strategy']}):")
        print(f"    Result : {attempt['error']}")
        print(f"    Details: {attempt['stderr_snippet']}")
    print()
    print_error(
        "Could not download subtitles after trying all strategies. "
        "The video may not have subtitles, or authentication failed. "
        "See the diagnostic output above for details."
    )
    return []  # unreachable, print_error exits


# ---------------------------------------------------------------------------
# Subtitle file processing
# ---------------------------------------------------------------------------

def process_vtt(sub_file: str, output_txt: str) -> bool:
    try:
        import webvtt
    except ImportError:
        print_error("webvtt-py is not installed. Please install it with 'pip install webvtt-py'")
        return False

    try:
        vtt = webvtt.read(sub_file)
        with open(output_txt, "w", encoding="utf-8") as f:
            last_line = None
            for caption in vtt:
                text_block = caption.text.strip()
                for line in text_block.split("\n"):
                    line = clean_html_tags(line).strip()
                    if line and line != last_line:
                        f.write(line + "\n")
                        last_line = line
        return True
    except Exception as e:
        print_error(f"Failed to parse VTT file: {e}")
        return False


def process_srt(sub_file: str, output_txt: str) -> bool:
    try:
        import pysrt
        subs = pysrt.open(sub_file)
        with open(output_txt, "w", encoding="utf-8") as f:
            last_line = None
            for sub in subs:
                text_block = sub.text.strip()
                for line in text_block.split("\n"):
                    line = clean_html_tags(line).strip()
                    if line and line != last_line:
                        f.write(line + "\n")
                        last_line = line
        return True
    except ImportError:
        # Fallback if pysrt is missing
        with open(sub_file, "r", encoding="utf-8") as f, open(output_txt, "w", encoding="utf-8") as out:
            for line in f:
                stripped = line.strip()
                if not stripped.isdigit() and "-->" not in stripped:
                    cleaned = clean_html_tags(stripped).strip()
                    if cleaned:
                        out.write(cleaned + "\n")
        return True
    except Exception as e:
        print_error(f"Failed to parse SRT file: {e}")
        return False


def process_json(sub_file: str, output_txt: str) -> bool:
    try:
        with open(sub_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(output_txt, "w", encoding="utf-8") as f:
            if isinstance(data, dict) and "events" in data:
                # YouTube json format
                for event in data["events"]:
                    if "segs" in event:
                        text = "".join([s.get("utf8", "") for s in event["segs"]])
                        text = clean_html_tags(text).strip()
                        if text:
                            f.write(text + "\n")
            elif isinstance(data, list):
                # Generic json array
                for item in data:
                    if isinstance(item, dict) and "content" in item:
                        text = clean_html_tags(item["content"]).strip()
                        if text:
                            f.write(text + "\n")
        return True
    except Exception as e:
        print_error(f"Failed to parse JSON file: {e}")
        return False


def process_xml(sub_file: str, output_txt: str) -> bool:
    try:
        with open(sub_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Try Bilibili danmaku format first
        matches = re.findall(r'<d p=".*?">(.*?)</d>', content)
        if not matches:
            # Fallback: standard XML text extraction
            matches = re.findall(r">([^<]+)</", content)

        with open(output_txt, "w", encoding="utf-8") as f:
            for text in matches:
                text = text.strip()
                if text and not text.isdigit():
                    f.write(text + "\n")
        return True
    except Exception as e:
        print_error(f"Failed to parse XML file: {e}")
        return False


def convert_subtitle_file(sub_file: str) -> str:
    """Convert a subtitle file to plain text. Returns the output text file path."""
    output_txt = os.path.join(
        os.path.dirname(sub_file),
        f"{Path(sub_file).stem}_subtitles.txt",
    )

    processors = {
        ".vtt": process_vtt,
        ".srt": process_srt,
        ".json": process_json,
        ".xml": process_xml,
    }

    ext = Path(sub_file).suffix.lower()
    processor = processors.get(ext)

    if not processor:
        print_error(f"Unsupported subtitle format: {ext} (file: {sub_file})")

    if not processor(sub_file, output_txt):
        print_error(f"Could not convert downloaded subtitle file: {sub_file}")

    return output_txt


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def extract_subtitles(url: str):
    tmp_dir = tempfile.mkdtemp(prefix="yt_sub_")

    print(f"Fetching subtitles for URL: {url} ...")
    print()

    # Download with tiered retry
    sub_files = download_subtitles(url, tmp_dir)

    if not sub_files:
        print_error("No subtitle files were downloaded.")

    # Pick the best subtitle file (prefer vtt > srt > json > xml)
    format_priority = {".vtt": 0, ".srt": 1, ".json": 2, ".xml": 3}
    sub_files.sort(key=lambda f: format_priority.get(Path(f).suffix.lower(), 99))
    sub_file = sub_files[0]

    print(f"  Processing: {os.path.basename(sub_file)}")

    # Convert to plain text
    output_txt = convert_subtitle_file(sub_file)

    print()
    print(f"SUCCESS: Subtitles extracted and converted to plain text.")
    print(f"FILE_PATH: {output_txt}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_error("Usage: python3 extract_subtitles.py <VIDEO_URL>")

    video_url = sys.argv[1]
    extract_subtitles(video_url)
