"""
Output formatters for different formats
"""

import json
from typing import Dict, Any, Optional
from .colors import ColorScheme, get_color_scheme


class BaseFormatter:
    """Base class for formatters"""

    def format(
        self,
        data: Dict[str, Any],
        show_tree: bool = True,
        show_files: bool = True,
        line_numbers: bool = False,
    ) -> str:
        raise NotImplementedError


class TextFormatter(BaseFormatter):
    """Plain text formatter with color support"""

    def __init__(self, color_scheme: Optional[ColorScheme] = None):
        self.colors = color_scheme or get_color_scheme(enabled=False)

    def _format_tree(
        self, tree: Dict[str, Any], prefix: str = "", is_last: bool = True
    ) -> str:
        """Format tree structure as text with inclusion markers and colors"""
        lines = []
        items = [(k, v) for k, v in tree.items() if k != "_files"]
        files = tree.get("_files", [])

        # Process directories
        for i, (name, subtree) in enumerate(items):
            is_last_item = (i == len(items) - 1) and not files
            connector = "└── " if is_last_item else "├── "
            dir_line = f"{prefix}{self.colors.separator(connector)}{self.colors.directory(name + '/')}"
            lines.append(dir_line)

            extension = "    " if is_last_item else "│   "
            colored_extension = self.colors.separator(extension)
            lines.append(
                self._format_tree(subtree, prefix + colored_extension, is_last_item)
            )

        # Process files
        for i, file_info in enumerate(files):
            is_last_file = i == len(files) - 1
            connector = "└── " if is_last_file else "├── "

            # Handle both old format (string) and new format (dict)
            if isinstance(file_info, dict):
                filename = file_info["name"]
                included = file_info["included"]

                if included:
                    marker = self.colors.marker_logged("✓")
                    status = self.colors.success("LOGGED")
                    file_style = self.colors.file_logged(filename)
                else:
                    marker = self.colors.marker_skipped("✗")
                    status = self.colors.file_skipped("SKIPPED")
                    file_style = self.colors.file_skipped(filename)

                line = f"{prefix}{self.colors.separator(connector)}[{marker}] {file_style}  ({status})"
                lines.append(line)
            else:
                # Fallback for old format
                lines.append(f"{prefix}{self.colors.separator(connector)}{file_info}")

        return "\n".join(filter(None, lines))

    def _format_file_content(
        self, filepath: str, content: str, line_numbers: bool
    ) -> str:
        """Format file content with colors"""
        separator = self.colors.separator("=" * 80)
        file_label = self.colors.filepath(f"File: {filepath}")

        lines = [
            separator,
            file_label,
            separator,
        ]

        if line_numbers:
            content_lines = content.split("\n")
            width = len(str(len(content_lines)))
            for i, line in enumerate(content_lines, 1):
                line_num = self.colors.line_number(f"{i:>{width}}")
                # Color the actual content line in gray
                colored_line = self.colors.code_content(line)
                lines.append(f"{line_num} {self.colors.separator('|')} {colored_line}")
        else:
            # Color all content lines in gray
            content_lines = content.split("\n")
            colored_content = "\n".join(
                self.colors.code_content(line) for line in content_lines
            )
            lines.append(colored_content)

        lines.append("")
        return "\n".join(lines)

    def format(
        self,
        data: Dict[str, Any],
        show_tree: bool = True,
        show_files: bool = True,
        line_numbers: bool = False,
    ) -> str:
        """Format data as plain text with colors"""
        output = []

        # Header
        header_sep = self.colors.separator("=" * 80)
        output.append(header_sep)
        output.append(
            self.colors.header(f"📁 Codebase: ") + self.colors.info(data["root_dir"])
        )
        output.append(
            self.colors.stat_label("Files to be logged: ")
            + self.colors.stat_value(str(data["file_count"]))
        )
        output.append(
            self.colors.stat_label("Total files found: ")
            + self.colors.stat_value(str(data.get("total_files", data["file_count"])))
        )
        output.append(header_sep)
        output.append("")

        # Legend
        legend_text = (
            f"{self.colors.marker_logged('✓')} = {self.colors.success('LOGGED')} (included in output)  "
            f"{self.colors.marker_skipped('✗')} = {self.colors.file_skipped('SKIPPED')} (excluded)"
        )
        output.append(self.colors.legend(legend_text))
        output.append("")

        # Directory tree
        if show_tree:
            output.append(self.colors.section("📂 Directory Structure:"))
            output.append(self.colors.separator("-" * 80))
            output.append(self._format_tree(data["tree"]))
            output.append("")

        # File contents
        if show_files:
            output.append(self.colors.section("📄 File Contents:"))
            output.append(self.colors.separator("-" * 80))
            output.append("")

            for filepath in sorted(data["files"]):
                content = data["contents"].get(filepath, "")
                output.append(
                    self._format_file_content(filepath, content, line_numbers)
                )

        return "\n".join(output)


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter (no colors needed for markdown)"""

    def _format_tree(self, tree: Dict[str, Any], level: int = 0) -> str:
        """Format tree structure as markdown with inclusion markers"""
        lines = []
        indent = "  " * level

        items = [(k, v) for k, v in tree.items() if k != "_files"]
        files = tree.get("_files", [])

        # Process directories
        for name, subtree in items:
            lines.append(f"{indent}- **{name}/**")
            lines.append(self._format_tree(subtree, level + 1))

        # Process files
        for file_info in files:
            # Handle both old format (string) and new format (dict)
            if isinstance(file_info, dict):
                filename = file_info["name"]
                included = file_info["included"]
                if included:
                    marker = "✅"
                    status = "**LOGGED**"
                else:
                    marker = "❌"
                    status = "~~SKIPPED~~"
                lines.append(f"{indent}- {marker} {filename} {status}")
            else:
                # Fallback for old format
                lines.append(f"{indent}- {file_info}")

        return "\n".join(filter(None, lines))

    def _format_file_content(
        self, filepath: str, content: str, line_numbers: bool
    ) -> str:
        """Format file content as markdown"""
        # Detect language from file extension
        ext = filepath.split(".")[-1] if "." in filepath else ""
        lang_map = {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "h": "c",
            "hpp": "cpp",
            "cs": "csharp",
            "go": "go",
            "rs": "rust",
            "rb": "ruby",
            "php": "php",
            "swift": "swift",
            "kt": "kotlin",
            "sh": "bash",
            "bash": "bash",
            "sql": "sql",
            "html": "html",
            "css": "css",
            "json": "json",
            "yaml": "yaml",
            "yml": "yaml",
            "xml": "xml",
            "md": "markdown",
        }
        language = lang_map.get(ext, "")

        lines = [
            f"## 📄 {filepath}",
            "",
            f"```{language}",
        ]

        if line_numbers:
            content_lines = content.split("\n")
            width = len(str(len(content_lines)))
            for i, line in enumerate(content_lines, 1):
                lines.append(f"{i:>{width}} | {line}")
        else:
            lines.append(content)

        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def format(
        self,
        data: Dict[str, Any],
        show_tree: bool = True,
        show_files: bool = True,
        line_numbers: bool = False,
    ) -> str:
        """Format data as markdown"""
        output = []

        # Header
        output.append(f"# 📁 Codebase: {data['root_dir']}")
        output.append("")
        output.append(f"**Files to be logged:** {data['file_count']}")
        output.append(
            f"**Total files found:** {data.get('total_files', data['file_count'])}"
        )
        output.append("")
        output.append(
            "**Legend:** ✅ = LOGGED (included in output) | ❌ = SKIPPED (excluded)"
        )
        output.append("")

        # Directory tree
        if show_tree:
            output.append("## 📂 Directory Structure")
            output.append("")
            output.append(self._format_tree(data["tree"]))
            output.append("")

        # File contents
        if show_files:
            output.append("## 📄 File Contents")
            output.append("")

            for filepath in sorted(data["files"]):
                content = data["contents"].get(filepath, "")
                output.append(
                    self._format_file_content(filepath, content, line_numbers)
                )

        return "\n".join(output)


class JSONFormatter(BaseFormatter):
    """JSON formatter"""

    def format(
        self,
        data: Dict[str, Any],
        show_tree: bool = True,
        show_files: bool = True,
        line_numbers: bool = False,
    ) -> str:
        """Format data as JSON"""
        output_data = {
            "root_dir": data["root_dir"],
            "file_count": data["file_count"],
            "total_files": data.get("total_files", data["file_count"]),
            "files_logged": data["files"],
            "files_skipped": [
                f for f in data.get("all_files", []) if f not in data["files"]
            ],
        }

        if show_tree:
            output_data["tree"] = data["tree"]

        if show_files:
            if line_numbers:
                # Add line numbers to content
                contents_with_lines = {}
                for filepath, content in data["contents"].items():
                    lines = content.split("\n")
                    width = len(str(len(lines)))
                    numbered = "\n".join(
                        f"{i:>{width}} | {line}" for i, line in enumerate(lines, 1)
                    )
                    contents_with_lines[filepath] = numbered
                output_data["contents"] = contents_with_lines
            else:
                output_data["contents"] = data["contents"]

        return json.dumps(output_data, indent=2, ensure_ascii=False)
