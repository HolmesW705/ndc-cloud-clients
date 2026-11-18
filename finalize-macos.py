#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Northern Data Centre
# SPDX-License-Identifier: GPL-2.0-or-later
"""Relocate installed dylibs inside an unsigned NDC build before publisher signing."""
from pathlib import Path
import os
import plistlib
import subprocess
import sys

app = Path(sys.argv[1]).resolve()
if app.is_relative_to(Path("/Applications")):
    raise RuntimeError("use a staging build, never an installed application")
info = plistlib.loads((app / "Contents/Info.plist").read_bytes())
if info.get("CFBundleIdentifier") != "net.northerndatacenter.cloud.desktop":
    raise RuntimeError("this is not the NDC desktop application")
signature = subprocess.run(["codesign", "-dvv", str(app)], capture_output=True, text=True).stderr
if "Authority=" in signature:
    raise RuntimeError("publisher-signed applications must be rebuilt before changes")

frameworks = app / "Contents/Frameworks"
changes = []
for binary in app.rglob("*"):
    if not binary.is_file() or binary.is_symlink():
        continue
    with binary.open("rb") as stream:
        magic = stream.read(4)
    if magic not in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        continue
    own_ids = set(line.strip() for line in subprocess.run(
        ["otool", "-D", str(binary)], capture_output=True, text=True
    ).stdout.splitlines()[1:])
    dependencies = subprocess.check_output(["otool", "-L", str(binary)], text=True).splitlines()[1:]
    for line in dependencies:
        dependency = line.strip().split(" (")[0]
        if dependency in own_ids or not dependency.startswith("/"):
            continue
        if dependency.startswith(("/System/Library/", "/usr/lib/")):
            continue
        candidates = [p for p in frameworks.rglob(Path(dependency).name) if p.is_file()]
        targets = {p.resolve() for p in candidates}
        if len(targets) != 1:
            raise RuntimeError(f"dependency is missing or ambiguous: {dependency}")
        target = targets.pop()
        if not target.is_relative_to(frameworks.resolve()):
            raise RuntimeError("a bundled library points outside the application")
        relative = "@loader_path/" + os.path.relpath(target, binary.parent)
        changes.append((binary, dependency, relative))

for binary, old, new in changes:
    subprocess.run(["install_name_tool", "-change", old, new, str(binary)], check=True)
print(f"Relocated {len(changes)} dependency references inside {app}")
print("Perform NDC publisher signing and notarization after this step.")
