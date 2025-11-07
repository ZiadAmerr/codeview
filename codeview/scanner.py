"""
Codebase scanner module
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Dict, Any, Set


class CodebaseScanner:
    """Scans a codebase and collects file information"""

    # Default patterns for code files
    DEFAULT_CODE_PATTERNS = [
        "*.py",
        "*.js",
        "*.jsx",
        "*.ts",
        "*.tsx",
        "*.java",
        "*.c",
        "*.cpp",
        "*.h",
        "*.hpp",
        "*.cs",
        "*.go",
        "*.rs",
        "*.rb",
        "*.php",
        "*.swift",
        "*.kt",
        "*.scala",
        "*.r",
        "*.m",
        "*.sh",
        "*.bash",
        "*.zsh",
        "*.sql",
        "*.html",
        "*.css",
        "*.scss",
        "*.sass",
        "*.less",
        "*.vue",
        "*.xml",
        "*.json",
        "*.yaml",
        "*.yml",
        "*.toml",
        "*.md",
        "*.rst",
        "*.txt",
        "*.conf",
        "*.cfg",
        "Makefile",
        "Dockerfile",
        "*.gradle",
        "*.maven",
    ]

    # Default directories to exclude
    DEFAULT_EXCLUDE_DIRS = [
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        "dist",
        "build",
        ".idea",
        ".vscode",
        ".DS_Store",
        "*.egg-info",
        ".tox",
        "coverage",
        ".coverage",
    ]

    def __init__(
        self,
        root_dir: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        search_pattern: Optional[str] = None,
        specific_paths: Optional[List[str]] = None,
    ):
        self.root_dir = Path(root_dir).resolve()
        self.include_patterns = include_patterns or self.DEFAULT_CODE_PATTERNS
        self.exclude_dirs = (exclude_dirs or []) + self.DEFAULT_EXCLUDE_DIRS
        self.exclude_patterns = exclude_patterns or []
        self.max_depth = max_depth
        self.search_pattern = search_pattern
        self.specific_paths = [Path(p) for p in (specific_paths or [])]

    def _should_exclude_dir(self, dir_path: Path) -> bool:
        """Check if directory should be excluded"""
        dir_name = dir_path.name
        for pattern in self.exclude_dirs:
            if fnmatch.fnmatch(dir_name, pattern):
                return True
        return False

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included"""
        file_name = file_path.name

        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return False

        # Check include patterns
        for pattern in self.include_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True

        return False

    def _matches_search(self, file_path: Path) -> bool:
        """Check if file contains the search pattern"""
        if not self.search_pattern:
            return True

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return self.search_pattern in content
        except Exception:
            return False

    def _get_relative_path(self, path: Path) -> Path:
        """Get path relative to root directory"""
        try:
            return path.relative_to(self.root_dir)
        except ValueError:
            return path

    def _calculate_depth(self, path: Path) -> int:
        """Calculate depth of path relative to root"""
        try:
            rel_path = path.relative_to(self.root_dir)
            return len(rel_path.parts)
        except ValueError:
            return 0

    def _build_tree_structure(
        self, included_files: List[Path], all_files: List[Path]
    ) -> Dict[str, Any]:
        """Build a tree structure from file paths with inclusion status"""
        tree = {}
        included_set = set(str(self._get_relative_path(f)) for f in included_files)

        for file_path in all_files:
            rel_path = self._get_relative_path(file_path)
            rel_path_str = str(rel_path)
            parts = rel_path.parts
            is_included = rel_path_str in included_set

            current = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # It's a file
                    if "_files" not in current:
                        current["_files"] = []
                    current["_files"].append(
                        {"name": part, "included": is_included, "path": rel_path_str}
                    )
                else:
                    # It's a directory
                    if part not in current:
                        current[part] = {}
                    current = current[part]

        return tree

    def _scan_directory(self, directory: Path, collect_all: bool = False) -> List[Path]:
        """Recursively scan a directory for matching files

        Args:
            directory: Directory to scan
            collect_all: If True, collect all files regardless of filters (for tree display)
        """
        files = []

        try:
            for entry in sorted(directory.iterdir()):
                if entry.is_dir():
                    # Check depth limit
                    if self.max_depth is not None:
                        depth = self._calculate_depth(entry)
                        if depth > self.max_depth:
                            continue

                    # Check if directory should be excluded
                    if self._should_exclude_dir(entry):
                        continue

                    # Recursively scan subdirectory
                    files.extend(self._scan_directory(entry, collect_all))

                elif entry.is_file():
                    if collect_all:
                        # Collect all files for tree display
                        files.append(entry)
                    else:
                        # Check if file should be included
                        if self._should_include_file(entry):
                            # Check search pattern if specified
                            if self._matches_search(entry):
                                files.append(entry)

        except PermissionError:
            pass  # Skip directories we don't have permission to read

        return files

    def scan(self) -> Dict[str, Any]:
        """Scan the codebase and return structured data"""
        # Determine which directories to scan
        if self.specific_paths:
            scan_paths = [self.root_dir / p for p in self.specific_paths]
        else:
            scan_paths = [self.root_dir]

        # Collect all matching files (for content)
        included_files = []
        for path in scan_paths:
            if path.is_dir():
                included_files.extend(self._scan_directory(path, collect_all=False))
            elif path.is_file() and self._should_include_file(path):
                if self._matches_search(path):
                    included_files.append(path)

        # Collect all files (for tree display with status)
        all_files = []
        for path in scan_paths:
            if path.is_dir():
                all_files.extend(self._scan_directory(path, collect_all=True))
            elif path.is_file():
                all_files.append(path)

        # Remove duplicates and sort
        included_files = sorted(set(included_files))
        all_files = sorted(set(all_files))

        # Read file contents (only for included files)
        file_contents = {}
        for file_path in included_files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                rel_path = str(self._get_relative_path(file_path))
                file_contents[rel_path] = content
            except Exception as e:
                file_contents[str(self._get_relative_path(file_path))] = (
                    f"Error reading file: {e}"
                )

        # Build tree structure with inclusion status
        tree = self._build_tree_structure(included_files, all_files)

        return {
            "root_dir": str(self.root_dir),
            "file_count": len(included_files),
            "total_files": len(all_files),
            "files": [str(self._get_relative_path(f)) for f in included_files],
            "all_files": [str(self._get_relative_path(f)) for f in all_files],
            "tree": tree,
            "contents": file_contents,
        }
