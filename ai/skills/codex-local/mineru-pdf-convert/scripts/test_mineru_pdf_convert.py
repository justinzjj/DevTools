from __future__ import annotations

import importlib.util
import json
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("mineru_pdf_convert.py")


def load_module():
    spec = importlib.util.spec_from_file_location("mineru_pdf_convert", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_data_id_is_stable_and_bounded() -> None:
    module = load_module()
    pdf = Path("2026 AAAI: A Very Long Paper Title " + "with spaces " * 30 + ".pdf")

    data_id = module.mineru_data_id(pdf)

    assert len(data_id) <= 128
    assert data_id.endswith("_" + module.hashlib.sha1(module.slugify_pdf_stem(pdf).encode("utf-8")).hexdigest()[:10])
    assert " " not in data_id
    assert ":" not in data_id


def test_output_is_converted_requires_metadata_status(tmp_path: Path) -> None:
    module = load_module()
    pdf = tmp_path / "A Test Paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    paper_dir = tmp_path / "out" / "A_Test_Paper"
    paper_dir.mkdir(parents=True)
    (paper_dir / "paper.md").write_text("# A Test Paper\n", encoding="utf-8")
    (paper_dir / "extraction.json").write_text(
        json.dumps({"status": "submitted"}),
        encoding="utf-8",
    )

    assert module.output_is_converted(pdf, tmp_path / "out") is False

    (paper_dir / "extraction.json").write_text(
        json.dumps({"status": "converted"}),
        encoding="utf-8",
    )
    assert module.output_is_converted(pdf, tmp_path / "out") is True


def test_select_full_markdown_from_zip_prefers_full_md(tmp_path: Path) -> None:
    module = load_module()
    zip_path = tmp_path / "mineru-result.zip"
    extract_dir = tmp_path / "assets"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("paper/other.md", "# Other\n")
        archive.writestr("paper/full.md", "# Full\n\nBody\n")
        archive.writestr("paper/images/figure.png", b"fake")

    markdown = module.select_full_markdown_from_zip(zip_path, extract_dir)

    assert markdown == "# Full\n\nBody\n"
    assert (extract_dir / "paper" / "images" / "figure.png").exists()


def test_dry_run_manifest_does_not_include_token(monkeypatch, tmp_path: Path, capsys) -> None:
    module = load_module()
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    monkeypatch.setenv("MINERU_TOKEN", "secret-token-should-not-print")

    exit_code = module.main(
        [
            "--input-pdf",
            str(pdf),
            "--output-dir",
            str(tmp_path / "out"),
            "--backend",
            "mineru",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "secret-token-should-not-print" not in captured.out
    manifest = json.loads(captured.out)
    assert manifest["credential_env"] == "MINERU_TOKEN"
    assert manifest["api"]["requires_token"] is True
