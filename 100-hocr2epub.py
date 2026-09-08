#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Personality Style for Dummies",
    "--doc-subtitle", "HRDQ Special Edition",
    # "--doc-subject", "",
    "--doc-date", "2011",
    "--doc-edition", "1",
    "--doc-extent", "96 pages",
    "--color-image-pages", "97,98",
    "--doc-author", "Roger R. Pearman",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Wiley Publishing",
    # "--doc-language", "de", # german
    "--doc-language", "en", # english
    "--doc-isbn", "9781118076965",
    "--doc-cover-image", "072-deskew-fix-page-size/097.tiff",
    "--canonical-url-base", "https://milahu.github.io/personality-style-for-dummies-2011/",
    "--doc-description", """
Personality Style for Dummies is a practical guide that helps you understand what drives behavior at work.
Centered on two key traits – assertiveness and expressiveness – it introduces the four core personality styles:
Direct, Spirited, Considerate, and Systematic.

Learn how to identify your own style, recognize others’,
and adapt your approach to improve teamwork, communication, and leadership across any situation.

A Crash Course in Personality Styles

Personality style is the primary force driving human behavior.
Knowing its ins and outs sheds light on just about everything employees do –
from how they manage to how they work as part of a team.

Your specific personality style boils down to two fundamental behaviors: assertiveness and expressiveness.
These two traits combine in various ways to form the four basic personality styles: Direct, Spirited, Considerate, and Systematic.

Discover your team members' unique styles using Personality Style for Dummies.

This handy reference guide does the following:

- Introduces the concepts of the four personality styles
- Illustrates how style applies to a wide range of organizational situations
- Shows readers how to spot someone else's personality style
- Offers tips for "flexing" personality styles in any situation
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
