"""
Utility functions
"""

from pathlib import Path
from typing import List


def is_binary_file(filepath: Path) -> bool:
    """Check if a file is binary"""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk
    except Exception:
        return True


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes"""
    try:
        return filepath.stat().st_size
    except Exception:
        return 0


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
