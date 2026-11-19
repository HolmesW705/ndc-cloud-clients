#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Northern Data Centre
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reconstruct the NDC client source from its pinned upstream and binary patch."""
import argparse
from pathlib import Path
import subprocess

RELEASES = {
    "desktop": ("https://github.com/nextcloud/desktop.git", "1e5b93f08b8ce07ffb3ad47d7def17df469b189c"),
    "android": ("https://github.com/nextcloud/android.git", "9687c1ed2e5acf7945880b56fb2dbddd8833fc09"),
    "ios": ("https://github.com/nextcloud/ios.git", "bb593bb65e569355a66b2b5abcf2cc19c76d18c4"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client", choices=RELEASES)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        parser.error("choose a new destination; existing source is never overwritten")
    repository, revision = RELEASES[args.client]
    destination.mkdir(parents=True)
    def git(*arguments):
        return subprocess.run(["git", "-C", str(destination), *arguments], check=True)
    git("init")
    # Binary Git patches must be applied to LF source on Windows as well.
    git("config", "core.autocrlf", "false")
    git("remote", "add", "origin", repository)
    git("fetch", "--depth", "1", "origin", revision)
    git("checkout", "--detach", "FETCH_HEAD")
    actual = subprocess.check_output(["git", "-C", str(destination), "rev-parse", "HEAD"], universal_newlines=True).strip()
    if actual != revision:
        raise RuntimeError("upstream revision did not match")
    patch = Path(__file__).resolve().parent / "patches" / f"{args.client}-branding.patch"
    patch_bytes = patch.read_bytes().replace(b"\r\n", b"\n")
    for options in (("--check",), ()):
        subprocess.run(["git", "-C", str(destination), "apply", *options, "-"],
                       input=patch_bytes, check=True)
    print(f"NDC {args.client} source prepared at {destination}")


if __name__ == "__main__":
    main()
