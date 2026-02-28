---
name: create-agent-skill
description: Use this skill to help a user create a new Agent Skill by conforming to the official Agent Skills specification, including directory structure and SKILL.md frontmatter.
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
---

# Create Agent Skill

## When to use this skill
Use this skill when the user asks to create, build, or scaffold a new Agent Skill or a "skill" for an AI agent. This skill ensures that the generated skills conform to the open format for extending AI agent capabilities.

## Overview of the Agent Skills Specification
An Agent Skill is a directory containing at minimum a `SKILL.md` file. It can optionally contain `scripts/`, `references/`, and `assets/` directories for executable code, reference materials, and templates respectively.

The root of the skill must be a directory matching the skill name. 

Inside the directory, the `SKILL.md` file is required. It contains YAML frontmatter and Markdown body content.

## Directory Structure
```
skill-name/
├── SKILL.md      # Required: instructions + metadata
├── scripts/      # Optional: executable code (python, bash, JS, etc.)
├── references/   # Optional: reference documentation
└── assets/       # Optional: templates, resources
```

## Creating a new skill step-by-step

When the user asks to create a new skill, follow these exact steps:

### 1. Identify the Skill Name
Work with the user to determine the skill name. The name must be standard.
**Naming Rules:**
- Must be 1-64 characters.
- Must ONLY contain unicode lowercase alphanumeric characters and hyphens (`a-z`, `0-9`, and `-`).
- Must NOT start or end with a hyphen (`-`).
- Must NOT contain consecutive hyphens (`--`).
- The directory name containing the skill MUST match this skill name exactly.

Example valid names: `data-analysis`, `code-review`, `pdf-processing`.

### 2. Determine the Description
Write a description for the skill. This is critical for the agent to know when to use it.
**Description Rules:**
- Must be 1-1024 characters.
- Must describe BOTH what the skill does AND when to use it.
- Should include specific keywords that help the agent identify relevant tasks.
Example: `Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`

### 3. Create the Directory
Create the root directory for the skill named exactly exactly as the `name` identified in Step 1.
Create the `SKILL.md` file inside this new directory.

### 4. Write the SKILL.md Frontmatter
Write the `SKILL.md` file starting with the required YAML frontmatter delineated by `---`.

**Required Fields:**
- `name`: the name determined in Step 1.
- `description`: the description determined in Step 2.

**Optional Fields (include if relevant):**
- `license`: short license name (e.g. `Apache-2.0`, `Proprietary`).
- `compatibility`: specific environment requirements (e.g. `Requires git, docker`).
- `metadata`: map from string to string for arbitrary values (e.g. author, version).
- `allowed-tools`: space-delimited list of safe tools (experimental).

Example frontmatter:
```yaml
---
name: awesome-data-tool
description: Analyzes CSV data and creates charts. Use when the user asks to visualize data or process CSV files.
license: MIT
metadata:
  author: AI Agent
  version: "1.0"
---
```

### 5. Write the SKILL.md Body Content
After the frontmatter, provide the instructions for the skill in Markdown format.
The instructions should guide an agent on how to accomplish the task using the provided scripts or references.

**A good instruction body should.**
- Use Markdown headers, lists, and code blocks for readability.
- Detail when the skill should be used.
- Provide step-by-step instructions.
- Provide examples of inputs and outputs.
- Point to any reference files (e.g., `See [the reference guide](references/REFERENCE.md) for details.`) 
- Mention edge cases and how to handle them.

### 6. Add Optional Resources
If the skill requires external scripts, reference docs, or assets:
- Create the `scripts/`, `references/`, or `assets/` folders inside the skill directory.
- Create the respective files inside the folders.
- Ensure the `SKILL.md` explicitly references these scripts or files utilizing relative paths, e.g., `Run the Python script at scripts/process.py`.

### 7. Verification
Inform the user that the skill has been created. Show them the directory structure and the `SKILL.md` frontmatter to confirm it meets the specification requirements.
