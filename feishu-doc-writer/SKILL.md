---
name: feishu-doc-writer
description: Create or update Feishu/Lark documents from drafted content, with optional inline images and automatic collaborator permission grant for the user. Use when the user asks to write, publish, create, or update a Feishu document/blog/article/report, especially when the result should be editable by the user in Feishu.
license: MIT
metadata:
  author: LuffyLiu
  version: "1.1"
  origin: OpenClaw
---

# Feishu Doc Writer

> This skill was originally built for **OpenClaw** (an AI Agent framework). It can also be used by other AI agents — see the "Installation Prerequisites" section below for setup instructions.

## Installation Prerequisites

Before using this skill, the agent **must** perform the following checks. Do **not** skip this step.

### Step 1: Check for the config file

Look for a Feishu configuration in this order:

1. `~/.openclaw/openclaw.json` → read `channels.feishu.appId` and `channels.feishu.appSecret`
2. `~/.feishu-doc-writer/config.json` → read `appId` and `appSecret`

If **either** file exists and contains valid `appId` + `appSecret`, proceed to Step 2.

If **neither** file exists, go to Step 1b.

### Step 1b: Ask the user for Feishu app credentials

Tell the user:

> This skill requires a Feishu (飞书) self-built app's `appId` and `appSecret` to create documents via API.
>
> You can create a Feishu app at https://open.feishu.cn/app and enable the following API permissions:
> - `docx:document` (create and edit documents)
> - `drive:drive` (upload files)
> - `drive:permission:member` (grant document permissions)
>
> Please provide your `appId` and `appSecret`.

If the user **cannot** provide the credentials:
- **Stop here.** Do not install or use this skill. Inform the user that the skill cannot function without valid Feishu app credentials.

If the user provides the credentials:
- Create `~/.feishu-doc-writer/config.json` with this content:

```json
{
  "appId": "<user-provided-app-id>",
  "appSecret": "<user-provided-app-secret>"
}
```

- Set the file permission to `600` to protect the secret.

### Step 2: Verify the credentials

Run:

```bash
python3 -c "
import json, urllib.request
cfg_path = None
import os
for p in [os.path.expanduser('~/.openclaw/openclaw.json'), os.path.expanduser('~/.feishu-doc-writer/config.json')]:
    if os.path.exists(p):
        cfg_path = p
        break
with open(cfg_path) as f:
    raw = json.load(f)
cfg = raw.get('channels', {}).get('feishu', raw)
body = json.dumps({'app_id': cfg['appId'], 'app_secret': cfg['appSecret']}).encode()
req = urllib.request.Request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', data=body, headers={'Content-Type':'application/json'}, method='POST')
resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
print('OK' if resp.get('code') == 0 else f'FAILED: {resp}')
"
```

- If the output is `OK`, the skill is ready to use.
- If it fails, report the error to the user and do **not** proceed.

---

## Core rule

When publishing a Feishu doc for the user, do **all** of the following unless the user explicitly says otherwise:

1. Draft the content locally first
2. Generate images if helpful
3. Insert images at the correct positions in the document
4. Grant the user **full_access** on the final Feishu document
5. Return the final Feishu doc link

Do **not** stop at "document created". A successful outcome means the user can actually open and edit it.

## Dynamic owner permission

Do **not** hardcode the collaborator user ID.

Default behavior:

- Read the **current conversation sender ID** from the current turn's message metadata / inbound context.
- In Feishu direct chats, this is typically the user's `openid`.
- Use that sender ID as the collaborator target when publishing the document.
- If the user explicitly gives a different Feishu `openid`, use the explicit value instead.

Default permission to grant:

- permission: `full_access`
- permission scope: `container`
- collaborator type in API body: `type: user`
- member id type in API body: `member_type: openid`

A publish is not complete until the final document is editable by the current requester.

## Recommended workflow

### 1. Draft locally

Write the document in a local Markdown file first.

If images are needed, place image markers in the Markdown file using this exact format on their own line:

```markdown
[[IMAGE:/absolute/path/to/image.png]]
```

The publishing script will insert the image at that exact position.

### 2. Generate images when needed

If diagrams, hero images, or illustrations would improve the document, generate them first and save them locally.

### 3. Publish with the bundled script

Run:

```bash
python3 {baseDir}/scripts/feishu_doc_publish.py \
  --title "Document Title" \
  --markdown-file /absolute/path/to/content.md \
  --owner-openid <current_sender_openid>
```

Before running the script, resolve `<current_sender_openid>` from the current conversation sender metadata.
If the user provides a different openid explicitly, replace it.
If you cannot determine the sender openid from context, stop and ask.

### 4. What the script does

The script will:

- create a new Feishu doc
- convert Markdown into doc blocks
- upload and insert images at each `[[IMAGE:...]]` marker
- add the target user as a collaborator with `full_access`
- print the final doc URL as JSON

The collaborator grant uses the official Feishu permission-member create interface pattern:

- `POST /open-apis/drive/v1/permissions/{doc_token}/members?need_notification=true&type=docx`
- request body includes:
  - `member_id`: current sender openid
  - `member_type`: `openid`
  - `perm`: `full_access`
  - `perm_type`: `container`
  - `type`: `user`

### 5. After publishing

Reply with the final Feishu doc link and confirm that edit permission was granted.

## Input guidance

Use simple Markdown structures for best compatibility:

- `#` / `##` / `###` headings
- normal paragraphs
- `-` bullet lists
- `1.` ordered lists
- `> ` quotes

### Important formatting rule

Avoid Markdown bold markers such as:

- `**bold**`
- `__bold__`

Feishu doc publishing in this workflow does not reliably convert those markers into rich-text bold. If included as raw Markdown, Feishu may display the literal asterisks/underscores.

Preferred alternatives:

- use headings for emphasis
- use short standalone lines
- use bullet points to highlight key ideas
- if you need visual emphasis, rewrite the sentence instead of relying on bold markers

The bundled script also strips common bold markers as a safety fallback, so the final document does not show raw `**` / `__` syntax.

## Failure handling

If publishing fails, report the exact API error and where it failed:

- token/auth
- document creation
- block append
- image upload
- permission grant

If document creation succeeds but permission grant fails, say so explicitly. Do not claim success until the final link and permission state are known.
