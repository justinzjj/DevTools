from pathlib import Path

from macsync.config import WorkspaceConfig
from macsync.workspace import (
    apply_workspace_gitignore,
    build_workspace_repos,
    discover_nested_git_repos,
    load_workspace_manifest,
    render_workspace_gitignore_block,
)


def test_discover_nested_git_repos_skips_root_repo_and_sorts_by_path(tmp_path):
    root = tmp_path / "knowledge"
    root.mkdir()
    (root / ".git").mkdir()
    beta = root / "6-projects" / "beta"
    alpha = root / "4-paper" / "alpha"
    beta.mkdir(parents=True)
    alpha.mkdir(parents=True)
    (beta / ".git").mkdir()
    (alpha / ".git").mkdir()

    nested = discover_nested_git_repos(root)

    assert nested == [alpha, beta]


def test_build_workspace_repos_returns_root_then_nested_repos(tmp_path):
    root = tmp_path / "knowledge"
    nested = root / "4-paper" / "CrossDataGen"
    nested.mkdir(parents=True)
    (root / ".git").mkdir()
    (nested / ".git").mkdir()
    workspace = WorkspaceConfig(
        name="personal-knowledge",
        root=root,
        root_repo="personal-knowledge-root",
        branch="main",
        auto_discover_nested_git=True,
        ignore=["附件/**"],
    )

    repos = build_workspace_repos(workspace)

    assert [repo.name for repo in repos] == ["personal-knowledge-root", "CrossDataGen"]
    assert [repo.path for repo in repos] == [root, nested]
    assert repos[0].gitea_repo == "personal-knowledge-root"
    assert repos[0].ignore == ["附件/**", "4-paper/CrossDataGen", "4-paper/CrossDataGen/**"]


def test_render_workspace_gitignore_block_marks_generated_section():
    block = render_workspace_gitignore_block(
        "personal-knowledge",
        ["**/.DS_Store", "4-paper/CrossDataGen/**"],
    )

    assert "# >>> macsync workspace personal-knowledge >>>" in block
    assert "**/.DS_Store" in block
    assert "4-paper/CrossDataGen/**" in block
    assert "# <<< macsync workspace personal-knowledge <<<" in block


def test_apply_workspace_gitignore_writes_nested_repo_manifest(tmp_path):
    root = tmp_path / "knowledge"
    nested = root / "4-paper" / "CrossDataGen"
    nested.mkdir(parents=True)
    (root / ".git").mkdir()
    (nested / ".git").mkdir()
    workspace = WorkspaceConfig(
        name="personal-knowledge",
        root=root,
        root_repo="personal-knowledge-root",
        branch="main",
        auto_discover_nested_git=True,
    )

    apply_workspace_gitignore(workspace)

    manifest = load_workspace_manifest(root)
    assert manifest[0].name == "CrossDataGen"
    assert manifest[0].path == Path("4-paper/CrossDataGen")
    assert manifest[0].gitea_repo == "CrossDataGen"
