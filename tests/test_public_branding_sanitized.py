"""Public repository branding guard for Cherries and Co Shaggy publish.

The README/GitHub-facing repository should not expose old upstream company or
product branding. Internal provider slugs may still use lowercase implementation
keys where technically required, but old public labels and domains must stay gone.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Split the literal old strings so this guard does not fail on its own source.
FORBIDDEN_PATTERNS = {
    "hermes_agent": re.compile(r"Hermes[ \t]+Agent", re.IGNORECASE),
    "hermes_agent_banner": re.compile("HERMES" + r"-" + "AGENT", re.IGNORECASE),
    "nous_research": re.compile(r"Nous[ \t]+Research", re.IGNORECASE),
    "nous_shaggy": re.compile("NOUS" + r"[ \t]+" + "SHAGGY", re.IGNORECASE),
    "old_docs_domain": re.compile("shaggy-agent." + "nousresearch" + r"\.com", re.IGNORECASE),
    "old_domain": re.compile("nousresearch" + r"\.com", re.IGNORECASE),
    "old_github_org": re.compile(r"github\.com/" + "NousResearch", re.IGNORECASE),
    "old_discord": re.compile(r"discord\.gg/" + "NousResearch", re.IGNORECASE),
    "old_built_badge": re.compile("Built%20by-" + "Nous", re.IGNORECASE),
    "old_assistant_name": re.compile(r"\b" + "Har" + "vey" + r"\b", re.IGNORECASE),
}

SKIP_PATH_PREFIXES = {
    ".git/",
    ".venv/",
    "venv/",
    "node_modules/",
    "build/",
    "dist/",
}


def _tracked_text_files() -> list[Path]:
    names = subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True).splitlines()
    paths: list[Path] = []
    for name in names:
        if any(name.startswith(prefix) for prefix in SKIP_PATH_PREFIXES):
            continue
        path = REPO_ROOT / name
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        paths.append(path)
    return paths


def test_public_repo_has_no_old_upstream_branding() -> None:
    findings: list[str] = []
    for path in _tracked_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                rel = path.relative_to(REPO_ROOT)
                findings.append(f"{label}: {rel}:{line_no}")
                break
    assert not findings, "Old public branding found:\n" + "\n".join(findings[:200])
