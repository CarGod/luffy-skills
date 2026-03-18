#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import ssl
import uuid
from pathlib import Path
from urllib import request, parse
from urllib.error import URLError


def _make_ssl_context() -> ssl.SSLContext:
    """Create an SSL context, trying certifi first, falling back to unverified."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
        return ctx


_SSL_CTX = _make_ssl_context()


def _make_unverified_ssl_context() -> ssl.SSLContext:
    """Create an SSL context that skips certificate verification."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _urlopen(req, timeout=120):
    """urlopen wrapper with SSL fallback for macOS cert issues."""
    try:
        return request.urlopen(req, timeout=timeout, context=_SSL_CTX)
    except (ssl.SSLCertVerificationError, URLError) as e:
        # URLError wraps SSLCertVerificationError on macOS without certifi
        is_ssl = isinstance(e, ssl.SSLCertVerificationError) or (
            isinstance(e, URLError) and isinstance(e.reason, ssl.SSLCertVerificationError)
        )
        if not is_ssl:
            raise
        ctx = _make_unverified_ssl_context()
        return request.urlopen(req, timeout=timeout, context=ctx)

DEFAULT_OWNER_OPENID = os.environ.get("FEISHU_OWNER_OPENID")
IMAGE_MARKER_RE = re.compile(r"^\[\[IMAGE:(.+?)\]\]$")
FENCE_RE = re.compile(r"^```(\w*)$")

# Map platform shorthand to full URL domain
DOMAIN_MAP = {
    "feishu": "feishu.cn",
    "lark": "larksuite.com",
}

# Markdown language hint → Feishu code block language enum
LANG_MAP = {
    "python": 49, "py": 49,
    "javascript": 30, "js": 30,
    "typescript": 63, "ts": 63,
    "java": 29,
    "go": 22, "golang": 22,
    "bash": 7, "sh": 7, "shell": 60,
    "json": 28,
    "html": 24,
    "css": 12,
    "sql": 56,
    "yaml": 67, "yml": 67,
    "markdown": 39, "md": 39,
    "rust": 53,
    "kotlin": 32, "kt": 32,
    "swift": 61,
    "ruby": 52, "rb": 52,
    "php": 43,
    "c": 10,
    "cpp": 9, "c++": 9, "cxx": 9,
    "csharp": 8, "cs": 8,
    "xml": 66,
    "dockerfile": 18,
    "makefile": 38,
    "diff": 69,
    "graphql": 71,
    "toml": 75,
    "protobuf": 48, "proto": 48,
    "scala": 57,
    "r": 50,
    "lua": 36,
    "dart": 15,
    "scss": 55,
    "perl": 44,
    "haskell": 27,
    "erlang": 19,
    "nginx": 40,
    "powershell": 46,
    "plaintext": 1, "text": 1, "txt": 1,
    "objectivec": 41, "objc": 41,
}


def resolve_url_domain(feishu_cfg: dict) -> str:
    """Resolve the URL domain from config, handling platform shorthands."""
    # Explicit urlDomain takes highest priority
    url_domain = feishu_cfg.get("urlDomain")
    if url_domain:
        return url_domain
    domain = feishu_cfg.get("domain", "feishu")
    # If it contains a dot, it's already a full domain (e.g. morehappiness.feishu.cn)
    if "." in domain:
        return domain
    # Map shorthand: feishu -> feishu.cn, lark -> larksuite.com
    return DOMAIN_MAP.get(domain, f"{domain}.cn")


def api_json(url: str, method: str = "GET", payload=None, token: str | None = None, timeout: int = 120):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method=method)
    with _urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_feishu_config():
    # Try OpenClaw config first, then standalone config
    openclaw_path = os.path.expanduser("~/.openclaw/openclaw.json")
    standalone_path = os.path.expanduser("~/.feishu-doc-writer/config.json")

    if os.path.exists(openclaw_path):
        with open(openclaw_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg["channels"]["feishu"]
    elif os.path.exists(standalone_path):
        with open(standalone_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise SystemExit(
            "Feishu config not found. Please create one of:\n"
            "  1. ~/.openclaw/openclaw.json  (with channels.feishu.appId / appSecret)\n"
            "  2. ~/.feishu-doc-writer/config.json  (with appId / appSecret)\n"
        )


def get_tenant_token(feishu_cfg):
    data = api_json(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        method="POST",
        payload={"app_id": feishu_cfg["appId"], "app_secret": feishu_cfg["appSecret"]},
        timeout=30,
    )
    return data["tenant_access_token"]


def create_doc(token: str, title: str):
    data = api_json(
        "https://open.feishu.cn/open-apis/docx/v1/documents",
        method="POST",
        payload={"title": title},
        token=token,
        timeout=30,
    )
    return data["data"]["document"]["document_id"]


def parse_inline_elements(text: str) -> list[dict]:
    """Parse inline Markdown markers and return a list of Feishu text_run elements.

    Supports:
      - ``code`` → inline_code style
      - **bold** / __bold__ → bold style
      - *italic* / _italic_ → italic style
      - [text](url) → link style
    """
    elements: list[dict] = []
    # Pattern matches inline code, bold, italic, and links in order of priority
    # Inline code first since backtick is unambiguous
    pattern = re.compile(
        r'`([^`]+)`'                   # group 1: inline code
        r'|\*\*(.+?)\*\*'             # group 2: bold **
        r'|__(.+?)__'                 # group 3: bold __
        r'|(?<!\w)\*(.+?)\*(?!\w)'    # group 4: italic *
        r'|(?<!\w)_(.+?)_(?!\w)'      # group 5: italic _
        r'|\[([^\]]+)\]\(([^)]+)\)'   # group 6,7: link [text](url)
    )

    last_end = 0
    for m in pattern.finditer(text):
        # Add plain text before this match
        if m.start() > last_end:
            plain = text[last_end:m.start()]
            if plain:
                elements.append({"text_run": {"content": plain, "text_element_style": {}}})

        if m.group(1) is not None:
            # Inline code
            elements.append({"text_run": {
                "content": m.group(1),
                "text_element_style": {"inline_code": True},
            }})
        elif m.group(2) is not None:
            # Bold **
            elements.append({"text_run": {
                "content": m.group(2),
                "text_element_style": {"bold": True},
            }})
        elif m.group(3) is not None:
            # Bold __
            elements.append({"text_run": {
                "content": m.group(3),
                "text_element_style": {"bold": True},
            }})
        elif m.group(4) is not None:
            # Italic *
            elements.append({"text_run": {
                "content": m.group(4),
                "text_element_style": {"italic": True},
            }})
        elif m.group(5) is not None:
            # Italic _
            elements.append({"text_run": {
                "content": m.group(5),
                "text_element_style": {"italic": True},
            }})
        elif m.group(6) is not None:
            # Link [text](url)
            elements.append({"text_run": {
                "content": m.group(6),
                "text_element_style": {
                    "link": {"url": parse.quote(m.group(7), safe="")},
                },
            }})

        last_end = m.end()

    # Add remaining plain text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            elements.append({"text_run": {"content": remaining, "text_element_style": {}}})

    # If nothing was parsed, return the whole text as a single element
    if not elements:
        elements.append({"text_run": {"content": text, "text_element_style": {}}})

    return elements


def line_to_block(line: str):
    text = line.rstrip()
    if not text.strip():
        return None
    block_type = 2
    prop = "text"
    content = text.strip()
    if text.startswith("# "):
        block_type, prop, content = 3, "heading1", text[2:].strip()
    elif text.startswith("## "):
        block_type, prop, content = 4, "heading2", text[3:].strip()
    elif text.startswith("### "):
        block_type, prop, content = 5, "heading3", text[4:].strip()
    elif text.startswith("> "):
        block_type, prop, content = 15, "quote", text[2:].strip()
    elif text.startswith("- ") or text.startswith("* "):
        block_type, prop, content = 12, "bullet", text[2:].strip()
    elif re.match(r"^\d+\. ", text):
        block_type, prop, content = 13, "ordered", re.sub(r"^\d+\. ", "", text).strip()
    elements = parse_inline_elements(content)
    return {
        "block_type": block_type,
        prop: {"elements": elements},
    }


def make_code_block(code_lines: list[str], lang_hint: str) -> dict:
    """Build a Feishu code block (block_type 14) from collected lines."""
    lang_id = LANG_MAP.get(lang_hint.lower(), 1) if lang_hint else 1
    content = "\n".join(code_lines)
    return {
        "block_type": 14,
        "code": {
            "style": {"language": lang_id},
            "elements": [{"text_run": {"content": content, "text_element_style": {}}}],
        },
    }


def append_blocks(token: str, doc_token: str, blocks: list[dict]):
    for i in range(0, len(blocks), 20):
        chunk = blocks[i:i+20]
        data = api_json(
            f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
            method="POST",
            payload={"children": chunk},
            token=token,
            timeout=30,
        )
        if data.get("code") != 0:
            raise RuntimeError(f"append blocks failed: {data}")


def create_image_block(token: str, doc_token: str):
    data = api_json(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
        method="POST",
        payload={"children": [{"block_type": 27, "image": {}}]},
        token=token,
        timeout=30,
    )
    raw = data.get("data", {})
    if isinstance(raw.get("children"), list) and raw["children"]:
        return raw["children"][0]["block_id"]
    if isinstance(raw.get("items"), list) and raw["items"]:
        return raw["items"][0]["block_id"]
    raise RuntimeError(f"create image block failed: {data}")


def upload_image_material(token: str, image_path: str, block_id: str):
    boundary = "----OpenClawBoundary" + uuid.uuid4().hex
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    filename = Path(image_path).name
    file_bytes = Path(image_path).read_bytes()
    parts: list[bytes] = []

    def add_field(name: str, value):
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode())
        parts.append(str(value).encode())
        parts.append(b"\r\n")

    add_field("file_name", filename)
    add_field("parent_type", "docx_image")
    add_field("parent_node", block_id)
    add_field("size", len(file_bytes))
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n".encode())
    parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = request.Request(
        "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
        method="POST",
    )
    with _urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(f"upload image failed: {data}")
    return data["data"]["file_token"]


def replace_image(token: str, doc_token: str, block_id: str, file_token: str):
    data = api_json(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{block_id}",
        method="PATCH",
        payload={"replace_image": {"token": file_token}},
        token=token,
        timeout=30,
    )
    if data.get("code") != 0:
        raise RuntimeError(f"replace image failed: {data}")


def grant_full_access(token: str, doc_token: str, openid: str):
    url = "https://open.feishu.cn/open-apis/drive/v1/permissions/{}/members?{}".format(
        doc_token,
        parse.urlencode({"need_notification": "true", "type": "docx"}),
    )
    data = api_json(
        url,
        method="POST",
        payload={
            "member_id": openid,
            "member_type": "openid",
            "perm": "full_access",
            "perm_type": "container",
            "type": "user",
        },
        token=token,
        timeout=30,
    )
    if data.get("code") != 0:
        raise RuntimeError(f"grant permission failed: {data}")
    return data


def publish_markdown(token: str, doc_token: str, markdown_text: str):
    """Parse Markdown text and append blocks to a Feishu doc.

    Handles fenced code blocks (```lang ... ```), image markers,
    and normal Markdown lines.
    """
    pending_blocks: list[dict] = []
    image_count = 0

    in_code_fence = False
    code_lines: list[str] = []
    code_lang = ""

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()

        # --- fenced code block state machine ---
        if not in_code_fence:
            fence_match = FENCE_RE.match(stripped)
            if fence_match:
                in_code_fence = True
                code_lang = fence_match.group(1)
                code_lines = []
                continue
        else:
            # Inside a code fence; check for closing fence
            if stripped == "```":
                in_code_fence = False
                block = make_code_block(code_lines, code_lang)
                pending_blocks.append(block)
                code_lines = []
                code_lang = ""
                continue
            else:
                code_lines.append(raw_line)
                continue

        # --- image marker ---
        marker = IMAGE_MARKER_RE.match(stripped)
        if marker:
            if pending_blocks:
                append_blocks(token, doc_token, pending_blocks)
                pending_blocks = []
            image_path = marker.group(1).strip()
            if not os.path.isabs(image_path):
                raise RuntimeError(f"image path must be absolute: {image_path}")
            block_id = create_image_block(token, doc_token)
            file_token = upload_image_material(token, image_path, block_id)
            replace_image(token, doc_token, block_id, file_token)
            image_count += 1
            continue

        # --- normal line ---
        block = line_to_block(raw_line)
        if block:
            pending_blocks.append(block)

    # Handle unclosed code fence (treat remaining lines as code block anyway)
    if in_code_fence and code_lines:
        block = make_code_block(code_lines, code_lang)
        pending_blocks.append(block)

    if pending_blocks:
        append_blocks(token, doc_token, pending_blocks)
    return image_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--markdown-file", required=True)
    ap.add_argument("--owner-openid", default=DEFAULT_OWNER_OPENID)
    args = ap.parse_args()

    if not args.owner_openid:
        raise SystemExit("owner openid is required; pass --owner-openid or set FEISHU_OWNER_OPENID")

    markdown_text = Path(args.markdown_file).read_text(encoding="utf-8")
    feishu_cfg = get_feishu_config()
    url_domain = resolve_url_domain(feishu_cfg)
    tenant_token = get_tenant_token(feishu_cfg)
    doc_token = create_doc(tenant_token, args.title)
    image_count = publish_markdown(tenant_token, doc_token, markdown_text)
    grant_full_access(tenant_token, doc_token, args.owner_openid)

    print(json.dumps({
        "ok": True,
        "title": args.title,
        "doc_token": doc_token,
        "url": f"https://{url_domain}/docx/{doc_token}",
        "owner_openid": args.owner_openid,
        "images_inserted": image_count,
        "permission": "full_access",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
