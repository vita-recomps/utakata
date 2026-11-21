"""Stamps a release's version into recomplauncher.json's prepare.version (release workflow), so
RecompLauncher builds the game again from the player's dump after each update: a release's front end
and kit need modules recompiled by that release (docs/INSTALLING.md, Updating). Only that value
changes; the file keeps its layout.

usage: python -I tools/stamp-recomplauncher.py recomplauncher.json <version>
"""
import json
import re
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    path, version = sys.argv[1], sys.argv[2]
    with open(path, encoding='utf-8') as f:
        text = f.read()
    stamped, n = re.subn(r'("version"\s*:\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(version), text)
    if n != 1 or json.loads(stamped)['prepare']['version'] != version:
        sys.exit(f'{path}: expected one "version", prepare\'s')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(stamped)
    print(f'{path}: prepare.version = {version}')


if __name__ == '__main__':
    main()
