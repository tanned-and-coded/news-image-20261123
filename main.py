#!/usr/bin/env python3
"""Copy the shipped entry.png to the make.fun output directory.

The output is validated (PNG magic bytes and the 1 MiB size limit),
written atomically, and made world-readable.
"""

import os
import tempfile
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def main() -> None:
    source = Path(__file__).resolve().parent / "entry.png"
    data = source.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise ValueError("entry.png is not a valid PNG file")
    if len(data) > MAX_BYTES:
        raise ValueError("entry.png exceeds the 1 MiB limit")

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "entry.png"

    fd, tmp_name = tempfile.mkstemp(dir=output_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, destination)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    os.chmod(destination, 0o644)


if __name__ == "__main__":
    main()
