#!/usr/bin/env python3
"""Resize all preview images to max 500px wide, convert to WebP, update library.json paths."""
import json
import os
from pathlib import Path
from PIL import Image

LIBRARY = Path(__file__).parent / "library.json"
PREVIEWS = Path(__file__).parent / "previews"
MAX_WIDTH = 500
QUALITY = 82


def resize_and_convert(src: Path) -> Path:
    dest = src.with_suffix(".webp")
    with Image.open(src) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        w, h = img.size
        if w > MAX_WIDTH:
            new_h = int(h * MAX_WIDTH / w)
            img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)
        img.save(dest, "WEBP", quality=QUALITY, method=4)
    return dest


def main():
    with open(LIBRARY) as f:
        lib = json.load(f)

    total = replaced = errors = 0

    for ti, t in enumerate(lib["templates"]):
        imgs = t.get("preview_images", [])
        for ui, rel in enumerate(imgs):
            src = PREVIEWS.parent / rel
            if not src.exists():
                continue
            total += 1
            try:
                dest = resize_and_convert(src)
                # Delete original if it differs from dest
                if src != dest:
                    src.unlink()
                new_rel = str(dest.relative_to(PREVIEWS.parent))
                if new_rel != rel:
                    lib["templates"][ti]["preview_images"][ui] = new_rel
                    replaced += 1
            except Exception as e:
                errors += 1
                print(f"  ERROR {src.name}: {e}")

        if (ti + 1) % 20 == 0:
            print(f"  {ti+1}/{len(lib['templates'])} templates processed...")

    print(f"Processed {total} images, updated {replaced} paths, {errors} errors.")

    with open(LIBRARY, "w") as f:
        json.dump(lib, f, indent=2)
        f.write("\n")

    size = sum(f.stat().st_size for f in PREVIEWS.rglob("*") if f.is_file())
    print(f"previews/ total size: {size / 1_048_576:.1f} MB")


if __name__ == "__main__":
    main()
