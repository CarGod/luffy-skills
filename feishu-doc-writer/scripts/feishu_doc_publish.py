#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import uuid
from pathlib import Path
from urllib import request, parse

DEFAULT_OWNER_OPENID = os.environ.get("FEISHU_OWNER_OPENID")
IMAGE_MARKER_RE = re.compile(r"^\[\[IMAGE:(.+?)\]\]$")


def api_json(url: str, method: str = "GET", payload=None, token: str | None = None, timeout: int = 120):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=timeout) as resp:
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


def normalize_inline_markdown(text: str) -> str:
    # Feishu doc publishing in this workflow does not reliably map Markdown bold
    # to rich-text styling, so strip the raw markers to avoid visible ** / __.
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    return text


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
    content = normalize_inline_markdown(content)
    return {
        "block_type": block_type,
        prop: {"elements": [{"text_run": {"content": content, "text_element_style": {}}}]},
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
    with request.urlopen(req, timeout=120) as resp:
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
    pending_blocks: list[dict] = []
    image_count = 0
    for raw_line in markdown_text.splitlines():
        marker = IMAGE_MARKER_RE.match(raw_line.strip())
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
        block = line_to_block(raw_line)
        if block:
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
    domain = feishu_cfg.get("domain", "feishu.cn")
    tenant_token = get_tenant_token(feishu_cfg)
    doc_token = create_doc(tenant_token, args.title)
    image_count = publish_markdown(tenant_token, doc_token, markdown_text)
    grant_full_access(tenant_token, doc_token, args.owner_openid)

    print(json.dumps({
        "ok": True,
        "title": args.title,
        "doc_token": doc_token,
        "url": f"https://{domain}/docx/{doc_token}",
        "owner_openid": args.owner_openid,
        "images_inserted": image_count,
        "permission": "full_access",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
