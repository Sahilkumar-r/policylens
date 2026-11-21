"""Deploy PolicyLens as a public Hugging Face Docker Space (free CPU).

Usage:   hf auth login          # once, with a token that has write access
         uv run python deploy/hf_space.py [space_name]

The Space runs in extractive mode with uploads disabled (DEMO_READONLY=1) and has no LLM key, so it costs
nothing and cannot be used to spend your API credit or to upload files.
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
SPACE_README = """---
title: PolicyLens
sdk: docker
app_port: 8000
pinned: false
short_description: Access controlled RAG over scans, tables and Urdu
---

Demo of [PolicyLens](https://github.com/Sahilkumar-r/policylens). Pick a role at the top of the page and ask a
question. Uploads are disabled and answers are extractive (no LLM) on this public demo.
"""

api = HfApi()
user = api.whoami()["name"]
repo_id = f"{user}/{sys.argv[1] if len(sys.argv) > 1 else 'policylens'}"
api.create_repo(repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
api.add_space_variable(repo_id, "DEMO_READONLY", "1")
api.upload_folder(
    repo_id=repo_id,
    repo_type="space",
    folder_path=str(ROOT),
    allow_patterns=["src/**", "static/**", "data/**", "Dockerfile", "pyproject.toml", "uv.lock"],
    ignore_patterns=["**/__pycache__/**", "**/*.pyc"],
    commit_message="Deploy PolicyLens demo",
)
api.upload_file(
    path_or_fileobj=SPACE_README.encode(), path_in_repo="README.md", repo_id=repo_id, repo_type="space"
)
print(f"Deployed: https://huggingface.co/spaces/{repo_id}  (the first build takes several minutes)")
