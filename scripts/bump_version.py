#!/usr/bin/env python3
import sys
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
PACKAGE_JSON = ROOT / "package.json"
DOCKER_COMPOSE = ROOT / "docker-compose.yml"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
ROADMAP = ROOT / "ROADMAP.md"


def read_version():
    return VERSION_FILE.read_text(encoding='utf-8').strip()


def write_version(v):
    VERSION_FILE.write_text(v + '\n', encoding='utf-8')


def update_package_json(old, new):
    data = json.loads(PACKAGE_JSON.read_text(encoding='utf-8'))
    data['version'] = new
    PACKAGE_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def update_docker_compose(old, new):
    text = DOCKER_COMPOSE.read_text(encoding='utf-8')
    # Replace image tags for omaya-* images using a callable to avoid backreference issues
    pattern = re.compile(r'(omaya-[\w-]+:)'+re.escape(old))
    def _repl(m):
        return m.group(1) + new
    text = pattern.sub(_repl, text)
    DOCKER_COMPOSE.write_text(text, encoding='utf-8')


def update_readme(old, new):
    text = README.read_text(encoding='utf-8')
    text = text.replace(f'Version-{old}', f'Version-{new}')
    text = text.replace(f'v{old}', f'v{new}')
    README.write_text(text, encoding='utf-8')


def update_roadmap(old, new):
    text = ROADMAP.read_text(encoding='utf-8')
    text = text.replace(f'v{old}', f'v{new}')
    ROADMAP.write_text(text, encoding='utf-8')


def prepend_changelog(old, new):
    text = CHANGELOG.read_text(encoding='utf-8')
    today = date.today().isoformat()
    header = f"## [{new}] - {today}\n\n### Добавени\n- Актуализация до версия {new}.\n\n### Променени\n- Автоматично обновяване на метаданни и тагове чрез `scripts/bump_version.py`.\n\n"
    parts = text.splitlines()
    # find insertion point after the first header line
    if parts:
        new_text = parts[0] + '\n\n' + header + '\n'.join(parts[1:])
    else:
        new_text = '# История на промените (CHANGELOG)\n\n' + header
    CHANGELOG.write_text(new_text, encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print('Usage: bump_version.py NEW_VERSION')
        sys.exit(1)
    new = sys.argv[1].strip()
    old = read_version()
    if old == new:
        print(f'Version is already {new}, continuing to ensure files are synchronized')

    print(f'Bumping version: {old} -> {new}')
    # Update files
    write_version(new)
    update_package_json(old, new)
    update_docker_compose(old, new)
    update_readme(old, new)
    update_roadmap(old, new)
    prepend_changelog(old, new)

    print('Done. Please review changes and commit.')


if __name__ == '__main__':
    main()
