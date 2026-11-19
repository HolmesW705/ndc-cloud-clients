#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Northern Data Centre
# SPDX-License-Identifier: GPL-2.0-or-later
"""Give the upstream Windows packager the same identity as the branded client."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()
replacements = {
    # Craft's current wildcard exports no longer provide os to this blueprint.
    'import info\n': 'import os\nimport info\n',
    'self.displayName = "Nextcloud"': 'self.displayName = "NDC Cloud"',
    'self.webpage = "https://nextcloud.com"': 'self.webpage = "https://northerndatacenter.ca"',
    'self.defines["appname"] = "nextcloud"': 'self.defines["appname"] = "ndccloud"',
    'self.defines["company"] = "Nextcloud GmbH"': 'self.defines["company"] = "Northern Data Centre"',
    'self.applicationExecutable = "nextcloud"': 'self.applicationExecutable = "ndccloud"',
}
for old, new in replacements.items():
    if source.count(old) != 1:
        raise RuntimeError(f"unexpected Craft blueprint: {old}")
    source = source.replace(old, new)
path.write_text(source)
