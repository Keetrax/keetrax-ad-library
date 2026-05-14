#!/usr/bin/env python3
"""Merge prompt fields from prompt_templates.json into library.json.

Run this once after updating prompt_templates.json to pull in the latest
Peelkit prompt text for all nanobanana entries. Keetrax entries are untouched.

Usage:
    python3 keetrax_library/merge_prompts.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATES_FILE = ROOT / "prompt_templates.json"
LIBRARY_FILE   = ROOT / "keetrax_library" / "library.json"


def main():
    with open(TEMPLATES_FILE) as f:
        peelkit = json.load(f)          # list of 114 dicts

    with open(LIBRARY_FILE) as f:
        lib = json.load(f)

    by_id = {t["id"]: t for t in peelkit}

    updated = skipped = missing = 0
    for entry in lib["templates"]:
        if entry.get("source") != "nanobanana":
            skipped += 1
            continue
        src = by_id.get(entry["id"])
        if src is None:
            missing += 1
            print(f"  WARNING: no match for {entry['id']} in prompt_templates.json")
            continue
        entry["prompt"] = src["prompt"]
        if src.get("updated_at"):
            entry["peelkit_updated_at"] = src["updated_at"]
        updated += 1

    with open(LIBRARY_FILE, "w") as f:
        json.dump(lib, f, indent=2)
        f.write("\n")

    print(f"Done. Updated {updated} nanobanana entries, skipped {skipped} keetrax entries, {missing} unmatched.")


if __name__ == "__main__":
    main()
