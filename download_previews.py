#!/usr/bin/env python3
"""Download remote preview_images from library.json into previews/[id]/ folders.

Updates library.json in-place with local relative paths.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LIBRARY = Path(__file__).parent / "library.json"
PREVIEWS = Path(__file__).parent / "previews"


def ext(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix in (".jpg", ".jpeg", ".png", ".webp", ".gif") else ".jpg"


def download(url: str, dest: Path) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        return None
    except Exception as e:
        return str(e)


def main():
    with open(LIBRARY) as f:
        lib = json.load(f)

    tasks = []  # (template_index, url_index, url, dest_path, local_rel)
    for ti, t in enumerate(lib["templates"]):
        imgs = t.get("preview_images", [])
        for ui, url in enumerate(imgs):
            if not url.startswith("http"):
                continue
            folder = PREVIEWS / t["id"]
            folder.mkdir(parents=True, exist_ok=True)
            fname = f"ref_{ui+1:02d}{ext(url)}"
            dest = folder / fname
            local_rel = f"previews/{t['id']}/{fname}"
            tasks.append((ti, ui, url, dest, local_rel))

    if not tasks:
        print("No remote URLs found — nothing to download.")
        return

    print(f"Downloading {len(tasks)} images across {len(set(t[0] for t in tasks))} templates...")

    errors = []
    done = 0

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(download, url, dest): (ti, ui, url, dest, local_rel)
                   for ti, ui, url, dest, local_rel in tasks}
        for fut in as_completed(futures):
            ti, ui, url, dest, local_rel = futures[fut]
            err = fut.result()
            done += 1
            if err:
                errors.append((url, err))
                print(f"  [{done}/{len(tasks)}] FAIL  {dest.name}: {err}")
            else:
                # Update library.json in memory
                lib["templates"][ti]["preview_images"][ui] = local_rel
                if done % 50 == 0 or done == len(tasks):
                    print(f"  [{done}/{len(tasks)}] ok")

    if errors:
        print(f"\n{len(errors)} download(s) failed:")
        for url, err in errors:
            print(f"  {url[:80]}  →  {err}")

    # Write updated library.json
    with open(LIBRARY, "w") as f:
        json.dump(lib, f, indent=2)
        f.write("\n")

    print(f"\nDone. library.json updated with local paths.")
    if errors:
        print("Failed URLs remain as remote in library.json — re-run to retry.")


if __name__ == "__main__":
    main()
