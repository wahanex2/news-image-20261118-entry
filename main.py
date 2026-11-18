#!/usr/bin/env python3
"""Copy the pre-drawn front page for Wednesday 18 November 2026 to the output dir.

Deterministic: byte-for-byte copy of entry.png, no network, no timestamps.
The shipped file is refused if it is over the 1 MiB gate or if its first
bytes are neither PNG nor JPEG magic. Copying onto the shipped file itself
(an output dir pointing at the repository) is refused, since opening the
destination for writing would truncate the source. After copying, the
output is verified: same size, same SHA-256 as the shipped file. Any mismatch
fails loudly so a bad copy can never pass as a valid entry.
"""
import hashlib
import os
import shutil
import sys

MAX_BYTES = 1 << 20  # the gate takes a picture of at most 1 MiB
MAGIC = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")  # PNG, JPEG


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    if os.path.getsize(src) > MAX_BYTES:
        sys.exit(f"entry.png is {os.path.getsize(src)} bytes, over the 1 MiB gate")
    with open(src, "rb") as probe:
        head = probe.read(8)
    if not head.startswith(MAGIC):
        sys.exit("entry.png is neither a PNG nor a JPEG image")
    if os.path.realpath(dst) == os.path.realpath(src):
        sys.exit("output entry.png would overwrite the shipped file; pick another dir")
    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out, length=1024 * 1024)
    if sha256_of(dst) != sha256_of(src):
        sys.exit("copied entry.png does not match the shipped file")
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes, sha256 {sha256_of(dst)[:16]}...)")


if __name__ == "__main__":
    main()
