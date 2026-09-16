#!/usr/bin/env python3
"""Rewrite the placeholder lint/CodeQL config in validate.yml.
"""
import os

linters = os.environ["LINTERS_JSON"]
codeql = os.environ["CODEQL_JSON"]
path = ".github/workflows/validate.yml"

with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "if: needs.check-init.outputs.ready == 'true' && fromJSON('[]')[0] != null",
    "if: needs.check-init.outputs.ready == 'true' && fromJSON('%s')[0] != null" % linters,
    1,
)
text = text.replace("linters: '[]'", "linters: '%s'" % linters, 1)
text = text.replace(
    'languages: \'[{"language":"actions","build-mode":"none"}]\'',
    "languages: '%s'" % codeql,
    1,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
