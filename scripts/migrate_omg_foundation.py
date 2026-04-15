#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
import sys


def copy_tree(src: Path, dst: Path) -> int:
    count = 0
    for path in src.rglob('*'):
        rel = path.relative_to(src)
        out = dst / rel
        if path.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)
        count += 1
    return count


def count_md(path: Path) -> int:
    return sum(1 for _ in path.rglob('*.md')) if path.exists() else 0


def main() -> int:
    if len(sys.argv) != 3:
        print('usage: migrate_omg_foundation.py <omg_repo_path> <brain_repo_path>', file=sys.stderr)
        return 1

    omg = Path(sys.argv[1]).expanduser().resolve()
    brain = Path(sys.argv[2]).expanduser().resolve()
    research = omg / 'research'
    if not research.exists():
        print(f'missing research dir: {research}', file=sys.stderr)
        return 1

    imports_root = brain / 'imports' / 'omg-windmill-02-foundation'
    wiki_dst = imports_root / 'wiki'
    primary_dst = imports_root / 'primary-sources'
    analysis_dst = imports_root / 'analysis'
    logs_dst = imports_root / 'log'
    imports_root.mkdir(parents=True, exist_ok=True)

    wiki_count = copy_tree(research / 'wiki', wiki_dst)
    primary_count = copy_tree(research / 'primary-sources', primary_dst)
    analysis_count = copy_tree(research / 'analysis', analysis_dst)
    log_count = copy_tree(research / 'log', logs_dst)

    manifest = {
        'source_repo': str(omg),
        'source_branch': 'origin/omg-windmill/02-foundation',
        'import_root': str(imports_root),
        'copied_files': {
            'wiki': wiki_count,
            'primary_sources': primary_count,
            'analysis': analysis_count,
            'log': log_count,
        },
        'markdown_counts': {
            'wiki': count_md(research / 'wiki'),
            'primary_sources': count_md(research / 'primary-sources'),
            'analysis': count_md(research / 'analysis'),
            'log': count_md(research / 'log'),
        },
    }
    (imports_root / 'migration-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

    report = f'''# OMG 02 Foundation Import

Source branch: `origin/omg-windmill/02-foundation`

This import preserves the OMG research wiki and source corpus under `imports/omg-windmill-02-foundation/`.
It is intentionally additive and non-destructive: the original OMG structure is preserved first, then future normalization can happen incrementally.

## Imported counts

- wiki markdown pages: {manifest['markdown_counts']['wiki']}
- primary source markdown pages: {manifest['markdown_counts']['primary_sources']}
- analysis markdown pages: {manifest['markdown_counts']['analysis']}
- log markdown pages: {manifest['markdown_counts']['log']}

## Notes

- This import is a frozen snapshot intended to preserve tracked entities, concepts, papers, links, and source provenance.
- Follow-up normalization can map selected pages into first-class `people/`, `companies/`, `concepts/`, `projects/`, and other GBrain-native directories.
- See `migration-manifest.json` for machine-readable details.
'''
    (imports_root / 'README.md').write_text(report)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
