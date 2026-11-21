"""Unit tests for Sprint 05 unified CLI additions (hash --file, merkle subcommands)."""
import pytest
from integrity_toolkit.cli.main import main, create_parser

def test_cli_hash_file(tmp_path, capsys):
    test_file = tmp_path / "sample.txt"
    test_file.write_bytes(b"hello world")
    
    exit_code = main(["hash", "--file", str(test_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "SHA256" in captured.out
    assert "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9" in captured.out

def test_cli_hash_file_nonexistent(capsys):
    exit_code = main(["hash", "--file", "nonexistent_file_999.txt"])
    assert exit_code == 3

def test_cli_hash_file_and_text_mutually_exclusive(tmp_path, capsys):
    test_file = tmp_path / "sample.txt"
    test_file.write_bytes(b"data")
    exit_code = main(["hash", "--file", str(test_file), "--text", "data"])
    assert exit_code == 2

def test_cli_merkle_no_subcommand(capsys):
    exit_code = main(["merkle"])
    assert exit_code == 2

def test_cli_merkle_lifecycle(tmp_path, capsys):
    # Setup directory and manifest
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "f1.txt").write_bytes(b"content 1")
    (data_dir / "f2.txt").write_bytes(b"content 2")
    manifest_file = tmp_path / "manifest.json"

    # Fingerprint
    assert main(["fingerprint", str(data_dir), "-o", str(manifest_file)]) == 0

    # Merkle root
    capsys.readouterr()
    assert main(["merkle", "root", str(manifest_file)]) == 0
    out_root = capsys.readouterr().out
    assert "Merkle Root:" in out_root

    # Merkle build
    summary_file = tmp_path / "tree.json"
    assert main(["merkle", "build", str(manifest_file), "-o", str(summary_file)]) == 0
    assert summary_file.exists()

    # Merkle prove
    proof_file = tmp_path / "f1_proof.json"
    assert main(["merkle", "prove", str(manifest_file), "f1.txt", "-o", str(proof_file)]) == 0
    assert proof_file.exists()

    # Get root value for verification
    root_val = out_root.split("Merkle Root:")[1].split()[0].strip()

    # Merkle verify-proof (SUCCESS)
    capsys.readouterr()
    assert main(["merkle", "verify-proof", str(proof_file), "--data", str(data_dir / "f1.txt"), "--root", root_val]) == 0
    assert "SUCCESS" in capsys.readouterr().out

    # Merkle verify-proof with WRONG root (FAILURE exit code 1)
    wrong_root = "0" * 64
    assert main(["merkle", "verify-proof", str(proof_file), "--data", str(data_dir / "f1.txt"), "--root", wrong_root]) == 1
