from macsync.cli import main



def test_cli_exposes_version(capsys):
    exit_code = main(["version"])

    assert exit_code == 0
    assert "macsync" in capsys.readouterr().out
