"""
Build the PDF ingestion Cloud Function ZIP from local import discovery.

The function entry point expects sibling ingestion modules at the ZIP root and
the required ``services`` modules under ``services/``. This script discovers
those files by walking Python imports reachable from ``main.py``.
"""

from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable
from pathlib import Path
import zipfile


FUNCTION_DIR = Path(__file__).resolve().parent
REPO_ROOT = FUNCTION_DIR.parents[1]
ENTRY_POINT = FUNCTION_DIR / "main.py"
DEFAULT_OUTPUT = FUNCTION_DIR / "pdf_ingestion.zip"
SERVICES_DIR = REPO_ROOT / "services"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Package the PDF ingestion Cloud Function."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination ZIP file.",
    )

    args = parser.parse_args()

    files = discover_local_dependencies(ENTRY_POINT)
    files.add(FUNCTION_DIR / "requirements.txt")

    output = args.output.resolve()

    write_zip(
        output=output,
        files=files,
    )

    print(f"Wrote {output}")
    print(f"Files: {len(files)}")


def discover_local_dependencies(
    entry_point: Path,
) -> set[Path]:
    """Discover local Python files imported from the entry point."""

    pending = [
        entry_point.resolve()
    ]
    discovered: set[Path] = set()

    while pending:
        current = pending.pop()

        if current in discovered:
            continue

        if not _is_packaged_python_file(current):
            continue

        discovered.add(current)

        for init_file in _package_init_files(current):
            if init_file not in discovered:
                pending.append(init_file)

        for module_name in _imported_modules(current):
            for resolved in _resolve_local_module(module_name):
                if resolved not in discovered:
                    pending.append(resolved)

    return discovered


def write_zip(
    *,
    output: Path,
    files: Iterable[Path],
) -> None:
    """Write the deployment ZIP with stable relative paths."""

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for file_path in sorted(
            files,
            key=lambda path: str(
                _zip_arcname(path)
            ),
        ):
            if not _should_include(file_path):
                continue

            archive.write(
                file_path,
                _zip_arcname(file_path),
            )


def _imported_modules(
    source_file: Path,
) -> set[str]:
    tree = ast.parse(
        source_file.read_text(
            encoding="utf-8"
        )
    )

    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)

        if isinstance(node, ast.ImportFrom):
            module_name = _absolute_import_module(
                source_file=source_file,
                module=node.module,
                level=node.level,
            )

            if module_name is None:
                continue

            modules.add(module_name)

            for alias in node.names:
                if alias.name == "*":
                    continue

                modules.add(
                    f"{module_name}.{alias.name}"
                )

    return modules


def _absolute_import_module(
    *,
    source_file: Path,
    module: str | None,
    level: int,
) -> str | None:
    if level == 0:
        return module

    current_package = _current_package(source_file)

    if level > len(current_package) + 1:
        return None

    anchor = current_package[
        : len(current_package) - level + 1
    ]

    if module:
        anchor.extend(
            module.split(".")
        )

    if not anchor:
        return None

    return ".".join(anchor)


def _current_package(
    source_file: Path,
) -> list[str]:
    try:
        relative = source_file.resolve().relative_to(
            REPO_ROOT
        )
    except ValueError:
        return []

    parts = list(
        relative.with_suffix("").parts
    )

    if not parts:
        return []

    if parts[-1] == "__init__":
        return parts[:-1]

    return parts[:-1]


def _resolve_local_module(
    module_name: str,
) -> set[Path]:
    parts = [
        part
        for part in module_name.split(".")
        if part
    ]

    if not parts:
        return set()

    candidates: list[Path] = []

    if len(parts) == 1:
        candidates.append(
            FUNCTION_DIR / f"{parts[0]}.py"
        )

    module_path = Path(*parts)

    candidates.extend(
        [
            REPO_ROOT / module_path.with_suffix(".py"),
            REPO_ROOT / module_path / "__init__.py",
        ]
    )

    return {
        candidate.resolve()
        for candidate in candidates
        if candidate.is_file()
        and _is_packaged_python_file(candidate)
    }


def _package_init_files(
    source_file: Path,
) -> set[Path]:
    resolved = source_file.resolve()

    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        return set()

    if relative.parts[:1] != ("services",):
        return set()

    init_files: set[Path] = set()

    for parent in resolved.parents:
        if parent == REPO_ROOT:
            break

        if not _is_within(parent, SERVICES_DIR):
            continue

        init_file = parent / "__init__.py"

        if init_file.is_file():
            init_files.add(
                init_file.resolve()
            )

    return init_files


def _is_packaged_python_file(
    path: Path,
) -> bool:
    if path.suffix != ".py":
        return False

    resolved = path.resolve()

    return _is_within(
        resolved,
        FUNCTION_DIR,
    ) or _is_within(
        resolved,
        SERVICES_DIR,
    )


def _should_include(
    path: Path,
) -> bool:
    if not path.is_file():
        return False

    if "__pycache__" in path.parts:
        return False

    if path.suffix == ".pyc":
        return False

    return True


def _zip_arcname(
    path: Path,
) -> str:
    resolved = path.resolve()

    if _is_within(
        resolved,
        FUNCTION_DIR,
    ):
        return resolved.relative_to(
            FUNCTION_DIR
        ).as_posix()

    return resolved.relative_to(
        REPO_ROOT
    ).as_posix()


def _is_within(
    path: Path,
    parent: Path,
) -> bool:
    try:
        path.resolve().relative_to(
            parent.resolve()
        )
    except ValueError:
        return False

    return True


if __name__ == "__main__":
    main()
