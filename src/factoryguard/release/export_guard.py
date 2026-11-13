"""Keep portable reviewer builds out of source and private-file directories."""
from pathlib import Path


GENERATED_FILES = frozenset({'index.html', 'source-manifest.json', '.nojekyll'})
PROTECTED_DIRECTORIES = (
    'src', 'site', 'assistant', 'configs', 'tests', 'scripts', '.git', '.github',
    'graphify-out', 'data',
)


def validate_export_directory(output, *, repository_root):
    """Accept a new/empty directory or a previous three-file reviewer export.

    Reject mixed folders without deleting their contents. This is a build-time
    accident guard, not a sandbox against concurrent filesystem changes.
    """
    target = Path(output)
    if target.is_symlink():
        raise ValueError('Reviewer output must not be a symbolic link')
    resolved = target.resolve()
    root = Path(repository_root).resolve()
    if resolved == root or resolved in root.parents:
        raise ValueError('Keep reviewer output separate from the repository root')
    for name in PROTECTED_DIRECTORIES:
        if resolved.is_relative_to(root / name):
            raise ValueError('Keep reviewer output outside source, data and tooling directories')
    if target.exists():
        if not target.is_dir():
            raise ValueError('Reviewer output must be a directory')
        for child in target.iterdir():
            if child.name not in GENERATED_FILES or child.is_symlink() or not child.is_file():
                raise ValueError(
                    'Reviewer output must be empty or contain only regular '
                    'index.html, source-manifest.json and .nojekyll files; '
                    'choose a clean output directory (existing files are preserved)'
                )
    return target
