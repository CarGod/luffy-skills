#!/usr/bin/env python3
"""
Gemini Image Generation Script (v1.2)
Calls the Gemini API to generate or edit images.
Features: auto retry, text verification, proxy auto-detection, flush output.
"""

import argparse
import base64
import os
import sys
import json
import subprocess
import tempfile
import time


API_KEY_ENV = "GEMINI_ANTIGRAVITY_KEY"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

MODELS = {
    "flash": "gemini-3.1-flash-image-preview",
}

VALID_ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16"]
VALID_IMAGE_SIZES = ["1K", "2K", "4K"]


def get_proxy() -> str | None:
    """Auto-detect proxy: env vars first, then macOS system proxy settings."""
    proxy = (os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or
             os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY"))
    if proxy:
        return proxy

    # Try macOS system proxy via scutil
    try:
        result = subprocess.run(
            ["scutil", "--proxy"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.splitlines()
        http_enabled = http_host = http_port = None
        for line in lines:
            line = line.strip()
            if "HTTPEnable" in line:
                http_enabled = line.split(":")[1].strip() == "1"
            elif "HTTPProxy" in line and "Port" not in line:
                http_host = line.split(":")[1].strip()
            elif "HTTPPort" in line:
                http_port = line.split(":")[1].strip()
        if http_enabled and http_host and http_port:
            detected = f"http://{http_host}:{http_port}"
            print(f"  [Proxy] Auto-detected macOS system proxy: {detected}", flush=True)
            return detected
    except Exception:
        pass

    return None


def log(msg: str, err: bool = False) -> None:
    """Print with flush=True to ensure real-time output in all environments."""
    print(msg, file=sys.stderr if err else sys.stdout, flush=True)


def build_request_body(prompt: str, aspect_ratio: str, image_size: str | None,
                       input_image_path: str | None, response_modality: str) -> dict:
    parts = []

    if prompt:
        parts.append({"text": prompt})

    if input_image_path:
        if not os.path.isfile(input_image_path):
            log(f"Error: Input image not found: {input_image_path}", err=True)
            sys.exit(1)

        ext = os.path.splitext(input_image_path)[1].lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime_type = mime_map.get(ext, "image/png")

        with open(input_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": image_data,
            }
        })

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": [response_modality],
        },
    }

    image_config = {}
    if aspect_ratio and aspect_ratio != "1:1":
        image_config["aspectRatio"] = aspect_ratio
    if image_size:
        image_config["imageSize"] = image_size
    if image_config:
        body["generationConfig"]["imageConfig"] = image_config

    return body


def run_curl(url: str, tmp_path: str, proxy: str | None, timeout_sec: int) -> dict | None:
    """Run curl and return parsed JSON, or None on failure."""
    curl_cmd = [
        "curl", "-s", "-S", "--fail-with-body",
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", f"@{tmp_path}",
        "--max-time", str(timeout_sec),
    ]
    if proxy:
        curl_cmd += ["-x", proxy]

    try:
        proc = subprocess.run(curl_cmd, capture_output=True, text=False, timeout=timeout_sec + 5)
    except subprocess.TimeoutExpired:
        log(f"Error: curl timed out after {timeout_sec}s. Check network/proxy.", err=True)
        return None

    if proc.returncode != 0:
        log(f"Error: curl failed (exit {proc.returncode})", err=True)
        if proc.stderr:
            log(proc.stderr.decode("utf-8", errors="replace"), err=True)
        if proc.stdout:
            try:
                log(json.dumps(json.loads(proc.stdout.decode("utf-8")), indent=2, ensure_ascii=False), err=True)
            except Exception:
                log(proc.stdout.decode("utf-8", errors="replace"), err=True)
        return None

    try:
        return json.loads(proc.stdout.decode("utf-8"))
    except json.JSONDecodeError as e:
        log(f"Error: Failed to parse API response as JSON: {e}", err=True)
        return None


def verify_image_text(api_key: str, image_path: str, expected_texts: str, proxy: str | None) -> bool:
    log(f"  [Verify] Checking image for text: '{expected_texts}'...")
    url = f"{API_BASE}/gemini-3.1-flash:generateContent?key={api_key}"

    ext = os.path.splitext(image_path)[1].lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/png")

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    body = {
        "contents": [{"parts": [
            {"text": f"Look at this image. Does it clearly contain these text/characters: [{expected_texts}]? Reply EXACTLY 'YES' or 'NO'."},
            {"inlineData": {"mimeType": mime, "data": image_data}}
        ]}],
        "generationConfig": {"temperature": 0.1}
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(body, tmp, ensure_ascii=False)
        tmp_path = tmp.name

    try:
        result = run_curl(url, tmp_path, proxy, timeout_sec=30)
        if result is None:
            log("  [Verify] Verification failed (curl error). Skipping verify.", err=True)
            return True
        text_resp = (result.get("candidates", [{}])[0]
                     .get("content", {}).get("parts", [{}])[0]
                     .get("text", "").strip().upper())
        if "YES" in text_resp:
            log("  [Verify] Passed ✓")
            return True
        else:
            log(f"  [Verify] Failed. Model says: {text_resp}")
            return False
    except Exception as e:
        log(f"  [Verify] Exception: {e}. Skipping verify.", err=True)
        return True
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def generate_image(args: argparse.Namespace) -> None:
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        log(f"Error: Environment variable {API_KEY_ENV} is not set.", err=True)
        sys.exit(1)

    proxy = get_proxy()
    model_id = MODELS.get(args.model, args.model)
    url = f"{API_BASE}/{model_id}:generateContent?key={api_key}"

    log(f"Calling Gemini API ({model_id})...")
    log(f"  Prompt: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    log(f"  Aspect Ratio: {args.aspect_ratio}")
    if args.verify_text:
        log(f"  Verify Text: {args.verify_text}")
    if proxy:
        log(f"  Proxy: {proxy}")

    for attempt in range(1, args.max_retries + 1):
        if attempt > 1:
            log(f"\n--- Retry {attempt}/{args.max_retries} ---")
            time.sleep(2)

        body = build_request_body(
            prompt=args.prompt,
            aspect_ratio=args.aspect_ratio,
            image_size=args.image_size,
            input_image_path=args.input_image,
            response_modality=args.response_modality,
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(body, tmp, ensure_ascii=False)
            tmp_path = tmp.name

        try:
            result = run_curl(url, tmp_path, proxy, timeout_sec=60)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        if result is None:
            if attempt == args.max_retries:
                log("Max retries reached. Exiting.", err=True)
                sys.exit(1)
            continue

        candidates = result.get("candidates", [])
        if not candidates:
            log("Warning: No candidates in API response (safety/content block?).", err=True)
            if attempt == args.max_retries:
                sys.exit(1)
            continue

        saved_count = 0
        last_saved_path = None

        for part in candidates[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                inline = part["inlineData"]
                image_bytes = base64.b64decode(inline["data"])
                mime = inline.get("mimeType", "image/png")
                ext = {"image/png": ".png", "image/jpeg": ".jpg"}.get(mime, ".png")

                output_path = args.output
                if saved_count > 0:
                    base, orig_ext = os.path.splitext(output_path)
                    output_path = f"{base}_{saved_count}{orig_ext or ext}"

                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                with open(output_path, "wb") as f:
                    f.write(image_bytes)

                last_saved_path = os.path.abspath(output_path)
                log(f"Image saved: {last_saved_path}")
                saved_count += 1

            elif "text" in part:
                log(f"Model returned text (no image): {part['text']}", err=True)

        if saved_count == 0:
            log("Warning: API returned no image data. Prompt may have been rejected.", err=True)
            if attempt == args.max_retries:
                sys.exit(1)
            continue

        if args.verify_text and last_saved_path:
            is_valid = verify_image_text(api_key, last_saved_path, args.verify_text, proxy)
            if not is_valid:
                log("Image text verification failed.", err=True)
                if attempt < args.max_retries:
                    os.unlink(last_saved_path)
                    continue
                else:
                    log("Max retries reached, keeping last image anyway.", err=True)

        log(f"\nDone! Generated {saved_count} image(s).")
        return

    log("All attempts exhausted. No image generated.", err=True)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images using the Gemini API (v1.2).",
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description (required)")
    parser.add_argument("--output", "-o", default="./generated_image.png", help="Output file path")
    parser.add_argument("--aspect-ratio", "-ar", default="1:1", choices=VALID_ASPECT_RATIOS)
    parser.add_argument("--model", "-m", default="flash", choices=list(MODELS.keys()),
                        help="Model: flash = gemini-3.1-flash-image-preview (default & only option)")
    parser.add_argument("--image-size", "-s", default=None, choices=VALID_IMAGE_SIZES)
    parser.add_argument("--input-image", "-i", default=None, help="Input image for editing mode")
    parser.add_argument("--response-modality", default="Image", choices=["Image", "Text"])
    parser.add_argument("--max-retries", "-r", type=int, default=3,
                        help="Max retries on failure or verify mismatch (default: 3)")
    parser.add_argument("--verify-text", "-vt", default=None,
                        help="Text to verify in image using vision model (e.g. '大语言模型')")

    args = parser.parse_args()
    generate_image(args)


if __name__ == "__main__":
    main()
