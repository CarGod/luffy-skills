#!/usr/bin/env python3
"""
Gemini Image Generation Script
Calls the Gemini API to generate or edit images with full control over
aspect ratio, resolution, and model selection.
"""

import argparse
import base64
import os
import sys
import json
import subprocess
import tempfile


API_KEY_ENV = "GEMINI_ANTIGRAVITY_KEY"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

MODELS = {
    "flash": "gemini-3.1-flash-image-preview",
    "pro": "gemini-3-pro-image-preview",
    "2.5-flash": "gemini-2.5-flash-image",
}

VALID_ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16"]
VALID_IMAGE_SIZES = ["1K", "2K", "4K"]


def build_request_body(prompt: str, aspect_ratio: str, image_size: str | None,
                       input_image_path: str | None, response_modality: str) -> dict:
    """Build the JSON request body for the Gemini API."""
    parts = []

    # Add text prompt
    parts.append({"text": prompt})

    # Add input image if provided (image editing mode)
    if input_image_path:
        if not os.path.isfile(input_image_path):
            print(f"Error: Input image not found: {input_image_path}", file=sys.stderr)
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

    # Add image config (aspect ratio, size)
    image_config = {}
    if aspect_ratio and aspect_ratio != "1:1":
        image_config["aspectRatio"] = aspect_ratio
    if image_size:
        image_config["imageSize"] = image_size
    if image_config:
        body["generationConfig"]["imageConfig"] = image_config

    return body


def generate_image(args: argparse.Namespace) -> None:
    """Call the Gemini API and save the generated image."""
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        print(f"Error: Environment variable {API_KEY_ENV} is not set.", file=sys.stderr)
        sys.exit(1)

    model_id = MODELS.get(args.model, args.model)
    url = f"{API_BASE}/{model_id}:generateContent?key={api_key}"

    body = build_request_body(
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size,
        input_image_path=args.input_image,
        response_modality=args.response_modality,
    )

    print(f"Calling Gemini API ({model_id})...")
    print(f"  Prompt: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"  Aspect Ratio: {args.aspect_ratio}")
    if args.image_size:
        print(f"  Image Size: {args.image_size}")
    if args.input_image:
        print(f"  Input Image: {args.input_image}")

    # Write request body to temp file (avoids shell escaping issues with large payloads)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(body, tmp, ensure_ascii=False)
        tmp_path = tmp.name

    try:
        curl_cmd = [
            "curl", "-s", "-S", "--fail-with-body",
            "-X", "POST", url,
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
            "--max-time", "180",
        ]

        proc = subprocess.run(curl_cmd, capture_output=True, text=False, timeout=200)

        if proc.returncode != 0:
            stderr_text = proc.stderr.decode("utf-8", errors="replace")
            stdout_text = proc.stdout.decode("utf-8", errors="replace")
            print(f"Error: curl failed (exit code {proc.returncode})", file=sys.stderr)
            if stderr_text:
                print(stderr_text, file=sys.stderr)
            if stdout_text:
                try:
                    print(json.dumps(json.loads(stdout_text), indent=2, ensure_ascii=False), file=sys.stderr)
                except json.JSONDecodeError:
                    print(stdout_text, file=sys.stderr)
            sys.exit(1)

        result = json.loads(proc.stdout.decode("utf-8"))

    except subprocess.TimeoutExpired:
        print("Error: Request timed out (180s)", file=sys.stderr)
        sys.exit(1)
    finally:
        os.unlink(tmp_path)

    # Extract image from response
    candidates = result.get("candidates", [])
    if not candidates:
        print("Error: No candidates in API response.", file=sys.stderr)
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    saved_count = 0
    text_parts = []

    for part in candidates[0].get("content", {}).get("parts", []):
        if "text" in part:
            text_parts.append(part["text"])
        elif "inlineData" in part:
            inline = part["inlineData"]
            image_bytes = base64.b64decode(inline["data"])

            # Determine file extension from mime type
            mime = inline.get("mimeType", "image/png")
            ext_map = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }
            ext = ext_map.get(mime, ".png")

            # Build output path
            output_path = args.output
            if saved_count > 0:
                base, orig_ext = os.path.splitext(output_path)
                output_path = f"{base}_{saved_count}{orig_ext or ext}"

            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(image_bytes)

            print(f"Image saved: {os.path.abspath(output_path)}")
            saved_count += 1

    if text_parts:
        print(f"\nModel text response:\n{''.join(text_parts)}")

    if saved_count == 0:
        print("Warning: No image was generated in the response.", file=sys.stderr)
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    print(f"\nDone! Generated {saved_count} image(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images using the Gemini API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a 16:9 image
  python3 generate_image.py --prompt "A sunset over the ocean" --aspect-ratio 16:9

  # Generate with pro model at 2K resolution
  python3 generate_image.py --prompt "A cyberpunk city" --model pro --image-size 2K

  # Edit an existing image
  python3 generate_image.py --prompt "Add fireworks in the sky" --input-image photo.png

  # Generate with custom output path
  python3 generate_image.py --prompt "A cute cat" -o /tmp/cat.png --aspect-ratio 9:16
        """,
    )

    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Text description of the image to generate (required).",
    )
    parser.add_argument(
        "--output", "-o",
        default="./generated_image.png",
        help="Output file path (default: ./generated_image.png).",
    )
    parser.add_argument(
        "--aspect-ratio", "-ar",
        default="1:1",
        choices=VALID_ASPECT_RATIOS,
        help="Aspect ratio of the output image (default: 1:1).",
    )
    parser.add_argument(
        "--model", "-m",
        default="flash",
        choices=list(MODELS.keys()),
        help="Model to use: flash (default), pro, or 2.5-flash.",
    )
    parser.add_argument(
        "--image-size", "-s",
        default=None,
        choices=VALID_IMAGE_SIZES,
        help="Image resolution (1K/2K/4K). Only for Gemini 3 models.",
    )
    parser.add_argument(
        "--input-image", "-i",
        default=None,
        help="Path to input image for image editing mode.",
    )
    parser.add_argument(
        "--response-modality",
        default="Image",
        choices=["Image", "Text"],
        help="Response modality (default: Image).",
    )

    args = parser.parse_args()

    # Validate aspect ratio
    if args.aspect_ratio not in VALID_ASPECT_RATIOS:
        parser.error(f"Invalid aspect ratio. Choose from: {VALID_ASPECT_RATIOS}")

    generate_image(args)


if __name__ == "__main__":
    main()
