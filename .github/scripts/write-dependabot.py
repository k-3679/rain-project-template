#!/usr/bin/env python3
"""Uncomment the Dependabot ecosystem blocks for the selected languages.
"""
import os

path = ".github/dependabot.yml"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

for eco in os.environ["ECOSYSTEMS"].split():
    marker = '# - package-ecosystem: "%s"' % eco
    new_lines = []
    active = False
    for line in lines:
        if line.strip() == marker:
            active = True
        if active:
            if line.strip() == "":
                active = False
                new_lines.append(line)
                continue
            idx = line.find("# ")
            new_lines.append(line[:idx] + line[idx + 2:] if idx != -1 else line)
        else:
            new_lines.append(line)
    lines = new_lines

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
