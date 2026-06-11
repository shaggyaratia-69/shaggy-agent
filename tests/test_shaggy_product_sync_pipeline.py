from __future__ import annotations

from pathlib import Path

import pytest

from tools.shaggy_product_sync import (
    DEFAULT_RULES,
    PipelinePaths,
    apply_rebrand_rules,
    assert_no_customer_facing_upstream_branding,
    build_pipeline_paths,
    classify_branding_hits,
    render_weekly_cron_draft,
    transform_tree,
)

OLD_ENGINE_PRODUCT = "Her" + "mes Agent"
OLD_COMPANY = "No" + "us Research"
OLD_ORG_URL = "github.com/" + "No" + "usResearch"
OLD_REPO_URL = OLD_ORG_URL + "/hermes-" + "agent"
OLD_PACKAGE_NAME = "hermes-" + "agent"


def test_rebrand_rules_convert_customer_facing_hermes_copy_to_shaggy() -> None:
    source = f"""
# {OLD_ENGINE_PRODUCT}
Run `hermes setup`, then `hermes doctor`, then `hermes update`.
Package: {OLD_PACKAGE_NAME}
Home: HERMES_HOME and ~/.hermes
Built by {OLD_COMPANY}.
Source: https://{OLD_REPO_URL}
"""

    result = apply_rebrand_rules(source, path=Path("README.md"), rules=DEFAULT_RULES)

    assert "Shaggy the Agent" in result.text
    assert "`shaggy setup`" in result.text
    assert "`shaggy doctor`" in result.text
    assert "`shaggy update`" in result.text
    assert "shaggy-agent" in result.text
    assert "SHAGGY_HOME" in result.text
    assert "~/.shaggy" in result.text
    assert "Cherries and Co Research" in result.text
    assert "github.com/shaggyaratia-69/shaggy-agent" in result.text
    assert result.changed is True
    assert result.replacements[OLD_ENGINE_PRODUCT] == 1
    assert OLD_ENGINE_PRODUCT not in result.text
    assert OLD_COMPANY not in result.text


def test_branding_classifier_allows_technical_nous_provider_slug_but_blocks_public_copy() -> None:
    technical = classify_branding_hits(
        "provider = 'nous'\n# internal adapter slug only\n",
        path=Path("plugins/model-providers/nous/provider.py"),
    )
    assert technical.blockers == []
    assert technical.allowed

    public = classify_branding_hits(
        f"Install {OLD_ENGINE_PRODUCT} from {OLD_REPO_URL} and run hermes setup.",
        path=Path("website/docs/install.md"),
    )
    assert {finding.label for finding in public.blockers} >= {
        "old engine product",
        "old GitHub org",
        "hermes command",
    }


def test_raw_upstream_customer_branding_is_a_hard_blocker() -> None:
    transformed = apply_rebrand_rules(
        f"{OLD_ENGINE_PRODUCT} users should run hermes setup.",
        path=Path("docs/customer.md"),
        rules=DEFAULT_RULES,
    )
    assert_no_customer_facing_upstream_branding(transformed.text, path=Path("docs/customer.md"))

    with pytest.raises(AssertionError) as exc:
        assert_no_customer_facing_upstream_branding(
            f"{OLD_ENGINE_PRODUCT} users should run hermes setup.",
            path=Path("docs/customer.md"),
        )
    assert "docs/customer.md" in str(exc.value)
    assert "old engine product" in str(exc.value)


def test_transform_tree_copies_only_rebranded_safe_output(tmp_path: Path) -> None:
    upstream = tmp_path / "upstream"
    rebranded = tmp_path / "rebranded"
    (upstream / "docs").mkdir(parents=True)
    (upstream / "docs" / "install.md").write_text(
        f"# {OLD_ENGINE_PRODUCT}\nRun hermes setup from {OLD_REPO_URL}.\n",
        encoding="utf-8",
    )
    (upstream / "plugins" / "model-providers" / "nous").mkdir(parents=True)
    (upstream / "plugins" / "model-providers" / "nous" / "provider.py").write_text(
        "provider = 'nous'\n",
        encoding="utf-8",
    )
    (upstream / "assets").mkdir()
    (upstream / "assets" / "icon.png").write_bytes(b"\x89PNG\r\n")

    report = transform_tree(upstream, rebranded)

    assert (rebranded / "docs" / "install.md").read_text(encoding="utf-8") == (
        "# Shaggy the Agent\n"
        "Run shaggy setup from github.com/shaggyaratia-69/shaggy-agent.\n"
    )
    assert (rebranded / "plugins" / "model-providers" / "nous" / "provider.py").read_text(
        encoding="utf-8"
    ) == "provider = 'nous'\n"
    assert (rebranded / "assets" / "icon.png").read_bytes() == b"\x89PNG\r\n"
    assert report.files_seen == 3
    assert report.text_files_transformed == 2
    assert report.binary_files_copied == 1
    assert report.blockers == []


def test_pipeline_paths_keep_upstream_staging_outside_customer_repo(tmp_path: Path) -> None:
    repo = tmp_path / "shaggy-agent"
    repo.mkdir()
    paths = build_pipeline_paths(repo)

    assert isinstance(paths, PipelinePaths)
    assert paths.repo_root == repo
    assert paths.upstream_stage_root.name == "upstream-hermes"
    assert paths.rebranded_stage_root.name == "rebranded-shaggy"
    assert paths.work_root.parent != repo
    assert repo not in paths.upstream_stage_root.parents
    assert repo not in paths.rebranded_stage_root.parents


def test_weekly_cron_draft_is_self_contained_and_not_enabled() -> None:
    draft = render_weekly_cron_draft(repo_path=Path("/product/shaggy-agent"))

    assert "cronjob(action='create'" not in draft
    assert "DO NOT ENABLE" in draft
    assert "weekly" in draft.lower()
    assert "/product/shaggy-agent" in draft
    assert "Hermes upstream" in draft
    assert "Shaggy rebrand" in draft
    assert "push a branch/PR" in draft
