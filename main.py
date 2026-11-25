#!/usr/bin/env python3
"""Entry point: copy the pre-drawn front page (entry.png) to the output.

Runs with no network and only the standard library (the grader installs
nothing). The output is a byte-for-byte copy of entry.png, so repeated
runs are identical. Dimensions are read from the PNG IHDR chunk with
struct, no image library needed.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")

MAX_BYTES = 1048576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_size(path):
    """Return (width, height) from a PNG's IHDR chunk, stdlib only."""
    with open(path, "rb") as f:
        data = f.read(33)
    if data[:8] != PNG_MAGIC or data[12:16] != b"IHDR":
        raise ValueError("not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    with open(SRC, "rb") as f:
        header = f.read(8)
    if header != PNG_MAGIC:
        print("entry.png is not a PNG", file=sys.stderr)
        return 1

    shutil.copyfile(SRC, out_path)

    size = os.path.getsize(out_path)
    if size > MAX_BYTES:
        print(f"output too large: {size} bytes", file=sys.stderr)
        return 1
    try:
        w, h = png_size(out_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if w > MAX_DIM or h > MAX_DIM:
        print(f"output too big: {w}x{h}", file=sys.stderr)
        return 1
    print(f"wrote {out_path} ({w}x{h}, {size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
