#!/usr/bin/env python3
"""Automated File Organizer & Cleanup Utility.

Sorts files in a directory (default: ~/Downloads) into category sub-folders
(Documents, Images, Videos, Archives, Code, ...) based on file extension.

Safe by design
--------------
* Naming collisions  -> file is renamed "name (1).ext", never overwritten.
* Permission errors  -> logged and skipped, the run continues.
* Subfolders, hidden files and this script are never moved.
* --dry-run previews every move without touching the disk.

Usage
-----
    python organizer.py                     # organize ~/Downloads
    python organizer.py /path/to/folder
    python organizer.py /path --dry-run
"""
import argparse
import logging
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".csv", ".ppt", ".pptx", ".md"},
    "Images":    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"},
    "Videos":    {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Audio":     {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives":  {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code":      {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp",
                  ".json", ".sh", ".sql", ".ipynb"},
}
OTHER = "Others"
EXT_TO_CATEGORY = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}
LOG_FILE = Path(__file__).with_name("organizer.log")

log = logging.getLogger("organizer")


def setup_logging(log_file: Path = LOG_FILE) -> None:
    log.setLevel(logging.INFO)
    log.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    for handler in (logging.StreamHandler(sys.stdout),
                    logging.FileHandler(log_file, encoding="utf-8")):
        handler.setFormatter(fmt)
        log.addHandler(handler)


def category_for(path: Path) -> str:
    return EXT_TO_CATEGORY.get(path.suffix.lower(), OTHER)


def unique_destination(dest_dir: Path, name: str) -> Path:
    """Return a path in dest_dir that does not exist, adding ' (n)' if needed."""
    candidate = dest_dir / name
    stem, suffix = Path(name).stem, Path(name).suffix
    n = 1
    while candidate.exists():
        candidate = dest_dir / f"{stem} ({n}){suffix}"
        n += 1
    return candidate


def organize(directory: Path, dry_run: bool = False) -> Counter:
    """Organize `directory`. Returns a Counter of moved files per category."""
    moved: Counter = Counter()
    errors = skipped = 0
    this_script = Path(__file__).resolve()

    with os.scandir(directory) as it:
        entries = sorted(it, key=lambda e: e.name.lower())

    for entry in entries:
        path = Path(entry.path)
        if (not entry.is_file(follow_symlinks=False) or entry.name.startswith(".")
                or path.resolve() == this_script):
            skipped += 1
            continue

        category = category_for(path)
        dest_dir = directory / category
        try:
            dest = unique_destination(dest_dir, entry.name)
            if dry_run:
                log.info("[DRY RUN] %s -> %s/%s", entry.name, category, dest.name)
            else:
                dest_dir.mkdir(exist_ok=True)
                shutil.move(str(path), str(dest))
                log.info("Moved %s -> %s/%s", entry.name, category, dest.name)
            moved[category] += 1
        except PermissionError:
            log.error("Permission denied: %s", entry.name)
            errors += 1
        except FileExistsError:
            log.error("Destination already exists: %s", entry.name)
            errors += 1
        except OSError as exc:
            log.error("Could not move %s: %s", entry.name, exc)
            errors += 1

    print_summary(moved, skipped, errors, dry_run)
    return moved


def print_summary(moved: Counter, skipped: int, errors: int, dry_run: bool) -> None:
    title = "DRY RUN SUMMARY" if dry_run else "EXECUTION SUMMARY"
    print("\n" + "=" * 36 + f"\n  {title}\n" + "=" * 36)
    for cat, n in sorted(moved.items()):
        print(f"  {cat:<12}{n:>5}")
    print("-" * 36)
    print(f"  {'Files moved':<12}{sum(moved.values()):>5}")
    print(f"  {'Skipped':<12}{skipped:>5}")
    print(f"  {'Errors':<12}{errors:>5}\n" + "=" * 36)


def main() -> int:
    ap = argparse.ArgumentParser(description="Organize files into category folders")
    ap.add_argument("directory", nargs="?", default=str(Path.home() / "Downloads"))
    ap.add_argument("--dry-run", action="store_true", help="preview without moving")
    args = ap.parse_args()

    target = Path(args.directory).expanduser()
    if not target.is_dir():
        print(f"Error: '{target}' is not a directory.")
        return 1
    setup_logging()
    log.info("Organizing %s%s", target, " (dry run)" if args.dry_run else "")
    organize(target, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
