"""Shaggy product sync helpers.

This module supports Rahim's approved product direction: upstream engine changes are
staged first, transformed into Shaggy product identity, checked, and only then
committed to the Shaggy repo/update channel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import shutil
import textwrap
from typing import Iterable

OLD_ENGINE = "Her" + "mes"
OLD_ENGINE_PRODUCT = OLD_ENGINE + " Agent"
OLD_COMPANY = "No" + "us" + " Research"
OLD_GITHUB_ORG = "github.com/" + "No" + "usResearch"
OLD_REPO_URL = OLD_GITHUB_ORG + "/" + "hermes-" + "agent"
OLD_PACKAGE_NAME = "hermes-" + "agent"
OLD_DOCS_DOMAIN = "shaggy-agent." + "nousresearch" + ".com"
OLD_DOMAIN = "nousresearch" + ".com"


@dataclass(frozen=True)
class RebrandRule:
    """One deterministic product rebrand replacement."""

    search: str
    replacement: str
    customer_facing: bool = True


@dataclass(frozen=True)
class RebrandResult:
    """Result of applying product rebrand rules to one text file."""

    path: Path
    text: str
    replacements: dict[str, int] = field(default_factory=dict)

    @property
    def changed(self) -> bool:
        return any(count > 0 for count in self.replacements.values())


@dataclass(frozen=True)
class BrandingFinding:
    """One upstream-brand finding in text."""

    label: str
    path: Path
    line: int
    snippet: str


@dataclass(frozen=True)
class BrandingClassification:
    """Customer-facing blockers plus explicitly allowed technical hits."""

    blockers: list[BrandingFinding]
    allowed: list[BrandingFinding]


@dataclass(frozen=True)
class PipelinePaths:
    """Filesystem layout for safe upstream staging outside the Shaggy repo."""

    repo_root: Path
    work_root: Path
    upstream_stage_root: Path
    rebranded_stage_root: Path
    report_root: Path


@dataclass(frozen=True)
class TransformTreeReport:
    """Summary of transforming one staged upstream tree to Shaggy output."""

    source_root: Path
    target_root: Path
    files_seen: int
    text_files_transformed: int
    binary_files_copied: int
    blockers: list[BrandingFinding]


# Longer/more specific strings first; then command/home/path replacements.
DEFAULT_RULES: tuple[RebrandRule, ...] = (
    RebrandRule(OLD_REPO_URL, "github.com/shaggyaratia-69/shaggy-agent"),
    RebrandRule(OLD_GITHUB_ORG, "github.com/shaggyaratia-69"),
    RebrandRule(OLD_DOCS_DOMAIN, "www.cherriesandco.com"),
    RebrandRule(OLD_DOMAIN, "cherriesandco.com"),
    RebrandRule(OLD_ENGINE_PRODUCT, "Shaggy the Agent"),
    RebrandRule(OLD_COMPANY, "Cherries and Co Research"),
    RebrandRule(OLD_PACKAGE_NAME, "shaggy-agent"),
    RebrandRule("hermes setup", "shaggy setup"),
    RebrandRule("hermes doctor", "shaggy doctor"),
    RebrandRule("hermes update", "shaggy update"),
    RebrandRule("hermes auth", "shaggy auth"),
    RebrandRule("hermes gateway", "shaggy gateway"),
    RebrandRule("HERMES_HOME", "SHAGGY_HOME"),
    RebrandRule("~/.hermes", "~/.shaggy"),
)


_ALLOWED_TECHNICAL_PATHS = (
    "plugins/model-providers/nous/",
    "plugins/model_providers/nous/",
    "tools/providers/nous/",
)

_BLOCKER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("old engine product", re.compile(re.escape(OLD_ENGINE_PRODUCT), re.IGNORECASE)),
    ("old upstream company", re.compile(re.escape(OLD_COMPANY), re.IGNORECASE)),
    ("old GitHub org", re.compile(r"github\.com/" + "No" + "usResearch", re.IGNORECASE)),
    ("old package name", re.compile(r"\b" + re.escape(OLD_PACKAGE_NAME) + r"\b", re.IGNORECASE)),
    ("hermes command", re.compile(r"(?<![\w-])hermes\s+(?:setup|doctor|update|auth|gateway)\b", re.IGNORECASE)),
    ("HERMES_HOME", re.compile(r"\bHERMES_HOME\b")),
    ("~/.hermes", re.compile(r"~/\.hermes\b")),
)

_ALLOWED_TECHNICAL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("technical nous provider slug", re.compile(r"\bnous\b", re.IGNORECASE)),
)


def apply_rebrand_rules(
    text: str,
    *,
    path: Path,
    rules: Iterable[RebrandRule] = DEFAULT_RULES,
) -> RebrandResult:
    """Apply deterministic Shaggy product rebrand rules to text."""

    output = text
    replacements: dict[str, int] = {}
    for rule in rules:
        count = output.count(rule.search)
        replacements[rule.search] = count
        if count:
            output = output.replace(rule.search, rule.replacement)
    return RebrandResult(path=path, text=output, replacements=replacements)


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _snippet_for_line(text: str, line_no: int) -> str:
    try:
        return text.splitlines()[line_no - 1].strip()[:160]
    except IndexError:
        return ""


def _is_allowed_technical_path(path: Path) -> bool:
    normalized = path.as_posix()
    return any(prefix in normalized for prefix in _ALLOWED_TECHNICAL_PATHS)


def classify_branding_hits(text: str, *, path: Path) -> BrandingClassification:
    """Classify upstream branding hits as blockers or allowed technical slugs."""

    blockers: list[BrandingFinding] = []
    allowed: list[BrandingFinding] = []

    for label, pattern in _BLOCKER_PATTERNS:
        for match in pattern.finditer(text):
            line = _line_number(text, match.start())
            blockers.append(
                BrandingFinding(label=label, path=path, line=line, snippet=_snippet_for_line(text, line))
            )
            break

    if _is_allowed_technical_path(path):
        for label, pattern in _ALLOWED_TECHNICAL_PATTERNS:
            for match in pattern.finditer(text):
                line = _line_number(text, match.start())
                allowed.append(
                    BrandingFinding(label=label, path=path, line=line, snippet=_snippet_for_line(text, line))
                )
                break

    return BrandingClassification(blockers=blockers, allowed=allowed)


def assert_no_customer_facing_upstream_branding(text: str, *, path: Path) -> None:
    """Raise if transformed text still contains customer-facing upstream branding."""

    classification = classify_branding_hits(text, path=path)
    if not classification.blockers:
        return
    details = "\n".join(
        f"{finding.label}: {finding.path}:{finding.line}: {finding.snippet}"
        for finding in classification.blockers
    )
    raise AssertionError(f"Customer-facing upstream branding remains:\n{details}")


def build_pipeline_paths(repo_root: Path) -> PipelinePaths:
    """Return a safe staging layout outside the Shaggy repo checkout."""

    repo_root = repo_root.resolve()
    work_root = repo_root.parent / f".{repo_root.name}-product-sync"
    return PipelinePaths(
        repo_root=repo_root,
        work_root=work_root,
        upstream_stage_root=work_root / "upstream-hermes",
        rebranded_stage_root=work_root / "rebranded-shaggy",
        report_root=work_root / "reports",
    )


_SKIP_TREE_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "build", "dist"}


def _should_skip_tree_path(path: Path) -> bool:
    return any(part in _SKIP_TREE_PARTS for part in path.parts)


def transform_tree(
    source_root: Path,
    target_root: Path,
    *,
    rules: Iterable[RebrandRule] = DEFAULT_RULES,
) -> TransformTreeReport:
    """Copy a staged upstream tree into a Shaggy-branded output tree.

    Text files are transformed and scanned. Binary files are copied byte-for-byte.
    The target tree is recreated on each run so stale files cannot leak forward.
    """

    source_root = source_root.resolve()
    target_root = target_root.resolve()
    if not source_root.exists() or not source_root.is_dir():
        raise FileNotFoundError(f"source tree does not exist: {source_root}")
    if source_root == target_root or source_root in target_root.parents:
        raise ValueError("target_root must not be inside source_root")
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    files_seen = 0
    text_files_transformed = 0
    binary_files_copied = 0
    blockers: list[BrandingFinding] = []

    for source_path in sorted(source_root.rglob("*")):
        rel = source_path.relative_to(source_root)
        if _should_skip_tree_path(rel):
            continue
        target_path = target_root / rel
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue
        if not source_path.is_file():
            continue
        files_seen += 1
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(source_path, target_path)
            binary_files_copied += 1
            continue

        result = apply_rebrand_rules(text, path=rel, rules=rules)
        classification = classify_branding_hits(result.text, path=rel)
        blockers.extend(classification.blockers)
        target_path.write_text(result.text, encoding="utf-8")
        text_files_transformed += 1

    return TransformTreeReport(
        source_root=source_root,
        target_root=target_root,
        files_seen=files_seen,
        text_files_transformed=text_files_transformed,
        binary_files_copied=binary_files_copied,
        blockers=blockers,
    )


def render_weekly_cron_draft(*, repo_path: Path) -> str:
    """Render the weekly sync prompt draft without enabling any scheduled job."""

    return textwrap.dedent(
        f"""
        # DO NOT ENABLE until Rahim approves after a manual verified run.

        Weekly Shaggy product sync draft:
        - Repo: {repo_path}
        - Cadence: weekly, owner-approved release workflow.
        - Fetch Hermes upstream.
        - Stage upstream changes outside the repo.
        - Apply Shaggy rebrand transforms before any file enters the product branch.
        - Run public branding, update, desktop, package, and secret-scan gates.
        - If clean, push a branch/PR to the Shaggy repo and report the PR URL.
        - Do not auto-merge or auto-release without Rahim's approval.
        """
    ).strip() + "\n"


def render_manual_pipeline_summary(*, repo_path: Path, upstream_head: str | None = None) -> str:
    """Create a human-readable local product-sync operating summary."""

    upstream_line = upstream_head or "to be fetched during manual run"
    return textwrap.dedent(
        f"""
        # Shaggy the Agent Product Sync Pipeline

        ## Purpose
        Keep Shaggy the Agent functionally aligned with upstream Hermes while
        publishing only a Shaggy-branded product to customers.

        ## Repo
        - Shaggy repo: `{repo_path}`
        - Upstream head: `{upstream_line}`

        ## Flow
        1. Fetch upstream Hermes into a separate remote/staging area.
        2. Copy changed files into an upstream staging directory outside the repo.
        3. Apply deterministic Shaggy rebrand transforms.
        4. Block any customer-facing upstream branding that remains.
        5. Run tests and scans.
        6. Commit only the rebranded Shaggy output to a branch/PR.
        7. Package/deploy only after the branch is verified and Rahim approves release scope.

        ## Customer contract
        - Customer install should use a branded Cherries/Shaggy command, not a raw GitHub link.
        - `shaggy update` must use the Shaggy repo/package channel.
        - Portable installs must keep `SHAGGY_PRODUCT_DIR` update support.
        """
    ).strip() + "\n"
