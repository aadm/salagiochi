#!/usr/bin/env python3
"""Reduce and store a score-proof photo.

Hugo copies static files verbatim, so a photo must be downscaled before being
committed or the repo and the site balloon in size. This script resizes to a
max dimension, strips EXIF metadata, and re-encodes as JPEG.

Usage:
  python scripts/optimize_photo.py INPUT.jpg static/scores/<slug>/<slug>-<player>-<date>.jpg
  python scripts/optimize_photo.py INPUT.png static/scores/<slug>/<slug>-<player>-<date>.jpg --max-size 1600 --quality 82
"""

import argparse
import os
from PIL import Image, ImageOps


def reduce_image(src, dest, max_size=1600, quality=82):
    """Resize src (path or file-like) to max_size and write dest as JPEG."""
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")

    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
    return img.size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="source photo or screenshot")
    parser.add_argument("output", help="destination path under static/scores/")
    parser.add_argument("--max-size", type=int, default=1600, help="max width/height in px (default 1600)")
    parser.add_argument("--quality", type=int, default=82, help="JPEG quality (default 82)")
    args = parser.parse_args()

    size = reduce_image(args.input, args.output, args.max_size, args.quality)
    size_kb = os.path.getsize(args.output) / 1024
    print(f"OK {args.output} ({size[0]}x{size[1]}, {size_kb:.0f} KB)")


if __name__ == "__main__":
    main()