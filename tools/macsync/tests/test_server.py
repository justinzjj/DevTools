from macsync.server import build_gitea_compose


def test_build_gitea_compose_contains_web_and_ssh_ports():
    compose = build_gitea_compose(
        http_port=3000,
        ssh_port=2222,
        data_dir="/srv/gitea",
    )

    assert "gitea/gitea" in compose
    assert "3000:3000" in compose
    assert "2222:22" in compose
    assert "/srv/gitea:/data" in compose
