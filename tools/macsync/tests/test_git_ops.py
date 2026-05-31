from pathlib import Path

from macsync.config import RepoConfig
from macsync.git_ops import RepoStatus, build_handoff_commands, build_setup_remote_commands, build_sync_commands, inspect_repo


class FakeRunner:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = []

    def run(self, cwd: Path, args: list[str]) -> str:
        self.calls.append((cwd, args))
        return self.outputs[tuple(args)]


class MissingRemoteRunner(FakeRunner):
    def run(self, cwd: Path, args: list[str]) -> str:
        if args == ["rev-list", "--left-right", "--count", "HEAD...origin/main"]:
            raise RuntimeError("missing origin")
        return super().run(cwd, args)


def test_inspect_repo_reports_dirty_and_remote_divergence(tmp_path):
    repo = RepoConfig(name="demo", path=tmp_path, branch="main")
    runner = FakeRunner(
        {
            ("rev-parse", "--abbrev-ref", "HEAD"): "main\n",
            ("status", "--porcelain"): " M README.md\n?? notes.md\n",
            ("rev-list", "--left-right", "--count", "HEAD...macsync/main"): "2\t3\n",
            ("rev-list", "--left-right", "--count", "HEAD...origin/main"): "0\t1\n",
        }
    )

    status = inspect_repo(repo, runner, sync_remote="macsync", github_remote="origin")

    assert status == RepoStatus(
        name="demo",
        path=tmp_path,
        branch="main",
        dirty_count=2,
        sync_ahead=2,
        sync_behind=3,
        origin_ahead=0,
        origin_behind=1,
    )


def test_inspect_repo_treats_missing_github_remote_as_zero_divergence(tmp_path):
    repo = RepoConfig(name="demo", path=tmp_path, branch="main")
    runner = MissingRemoteRunner(
        {
            ("rev-parse", "--abbrev-ref", "HEAD"): "main\n",
            ("status", "--porcelain"): "",
            ("rev-list", "--left-right", "--count", "HEAD...macsync/main"): "0\t0\n",
        }
    )

    status = inspect_repo(repo, runner, sync_remote="macsync", github_remote="origin")

    assert status.origin_ahead == 0
    assert status.origin_behind == 0


def test_build_handoff_commands_commits_dirty_repo_and_pushes_intranet(tmp_path):
    repo = RepoConfig(name="demo", path=tmp_path, branch="main")
    commands = build_handoff_commands(
        repo,
        dirty=True,
        sync_remote="macsync",
        message="wip: handoff from macbook",
    )

    assert commands == [
        ["git", "add", "-A"],
        ["git", "commit", "-m", "wip: handoff from macbook"],
        ["git", "push", "macsync", "main"],
    ]


def test_build_setup_remote_preserves_origin_and_adds_macsync(tmp_path):
    repo = RepoConfig(
        name="demo",
        path=tmp_path,
        branch="main",
        gitea_repo="demo",
        github="git@github.com:justinzjj/demo.git",
    )

    commands = build_setup_remote_commands(
        repo,
        sync_remote="macsync",
        gitea_host="codex-linux-wg",
        gitea_owner="justin",
        gitea_ssh_user="git",
    )

    assert commands == [
        ["git", "remote", "add", "macsync", "git@codex-linux-wg:justin/demo.git"],
    ]


def test_build_setup_remote_supports_custom_ssh_port(tmp_path):
    repo = RepoConfig(name="demo", path=tmp_path, branch="main", gitea_repo="demo")

    commands = build_setup_remote_commands(
        repo,
        sync_remote="macsync",
        gitea_host="192.168.31.53",
        gitea_owner="justin",
        gitea_ssh_user="git",
        gitea_ssh_port=2222,
    )

    assert commands == [
        ["git", "remote", "add", "macsync", "ssh://git@192.168.31.53:2222/justin/demo.git"],
    ]


def test_build_sync_commands_uses_fast_forward_by_default(tmp_path):
    repo = RepoConfig(name="demo", path=tmp_path, branch="main")

    assert build_sync_commands(repo, sync_remote="macsync", merge=False) == [
        ["git", "fetch", "macsync"],
        ["git", "pull", "--ff-only", "macsync", "main"],
    ]


def test_build_sync_commands_can_allow_git_merge(tmp_path):
    repo = RepoConfig(name="demo", path=tmp_path, branch="main")

    assert build_sync_commands(repo, sync_remote="macsync", merge=True) == [
        ["git", "fetch", "macsync"],
        ["git", "pull", "--no-rebase", "macsync", "main"],
    ]
