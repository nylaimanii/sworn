"""tests for the MFT timeline parser and receipt hash stability.

These exercise the PARSER directly against a saved fls body-file sample — no
subprocess / no live image required. The live fls run is exercised only inside
the SIFT VM against the real disk image.
"""
from pathlib import Path

from sworn import Receipt
from sworn.tools.mft import MFTEntry, _parse

FIXTURE = Path(__file__).parent / "fixtures" / "fls_sample.body"


def _raw() -> bytes:
    return FIXTURE.read_bytes()


def test_parser_produces_expected_records():
    records = _parse(_raw())
    assert len(records) == 4

    # First line: cmd.exe with distinct a/m/c times.
    cmd = records[0]
    assert isinstance(cmd, MFTEntry)
    assert cmd.filename == "C:/Windows/System32/cmd.exe"
    assert cmd.inode == "16-128-1"  # compound NTFS inode preserved as-is
    assert cmd.atime == "2021-01-01T00:00:00+00:00"
    assert cmd.mtime == "2021-02-01T00:00:00+00:00"
    assert cmd.ctime == "2021-03-01T00:00:00+00:00"
    assert cmd.byte_offset is None

    # Second line: the suspicious binary, all times equal.
    evil = records[1]
    assert evil.filename == "C:/Users/hadi/Desktop/evil.exe"
    assert evil.inode == "9234-128-3"
    assert evil.atime == evil.mtime == evil.ctime == "2021-02-01T00:00:00+00:00"

    # Fourth line ($MFT) has crtime 0; the a/m/c fields we map are non-zero.
    mft = records[3]
    assert mft.filename == "C:/$MFT"
    assert mft.ctime == "2021-01-01T00:00:00+00:00"


def test_zero_epoch_becomes_empty_string():
    # A line whose mtime is 0 must yield "" rather than a fabricated 1970 time.
    line = b"0|C:/x|1-1-1|r/r|0|0|0|0|0|0|0\n"
    rec = _parse(line)[0]
    assert rec.mtime == ""
    assert rec.atime == ""
    assert rec.ctime == ""


def test_malformed_lines_skipped():
    raw = b"not|enough|fields\n\n" + _raw()
    records = _parse(raw)
    # blank line + short line dropped; the 4 valid lines remain.
    assert len(records) == 4


def test_hash_stability_same_bytes_same_sha():
    """Two receipts built from identical raw bytes MUST share a sha256.

    This underpins the whole thesis: the receipt is a deterministic fingerprint
    of the evidence output.
    """
    raw = _raw()
    r1 = Receipt.for_run(tool_name="extract_mft_timeline", args={"image_path": "img"},
                         file_path="img", raw_output=raw)
    r2 = Receipt.for_run(tool_name="extract_mft_timeline", args={"image_path": "img"},
                         file_path="img", raw_output=raw)
    assert r1.raw_output_sha256 == r2.raw_output_sha256
    assert len(r1.raw_output_sha256) == 64
