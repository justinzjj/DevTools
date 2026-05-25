from macsync.cli import main



def test_cli_exposes_version(capsys):
    exit_code = main(["version"])

    assert exit_code == 0
    assert "macsync" in capsys.readouterr().out


def test_cli_init_config_writes_template(tmp_path):
    config_path = tmp_path / "config.yml"

    exit_code = main(["--config", str(config_path), "init-config"])

    assert exit_code == 0
    assert "repos:" in config_path.read_text(encoding="utf-8")
