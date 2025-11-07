"""
Unit tests for codeview
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from codeview.scanner import CodebaseScanner
from codeview.formatters import TextFormatter, MarkdownFormatter, JSONFormatter
from codeview.colors import get_color_scheme, ColorScheme


class TestCodebaseScanner(unittest.TestCase):
    """Test the CodebaseScanner class"""

    def setUp(self):
        """Create a temporary test directory structure"""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test structure
        (self.test_dir / "src").mkdir()
        (self.test_dir / "src" / "main.py").write_text("print('hello')")
        (self.test_dir / "src" / "utils.py").write_text("def helper(): pass")

        (self.test_dir / "tests").mkdir()
        (self.test_dir / "tests" / "test_main.py").write_text("def test(): pass")

        (self.test_dir / "README.md").write_text("# Test Project")
        (self.test_dir / "node_modules").mkdir()
        (self.test_dir / "node_modules" / "package.js").write_text("// ignored")

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir)

    def test_basic_scan(self):
        """Test basic scanning functionality"""
        scanner = CodebaseScanner(self.test_dir)
        result = scanner.scan()

        self.assertIn("file_count", result)
        self.assertIn("files", result)
        self.assertIn("tree", result)
        self.assertIn("contents", result)

    def test_include_patterns(self):
        """Test file inclusion patterns"""
        scanner = CodebaseScanner(self.test_dir, include_patterns=["*.py"])
        result = scanner.scan()

        # Should only include .py files
        for filepath in result["files"]:
            self.assertTrue(filepath.endswith(".py"))

    def test_exclude_dirs(self):
        """Test directory exclusion"""
        scanner = CodebaseScanner(self.test_dir)
        result = scanner.scan()

        # node_modules should be excluded by default
        for filepath in result["files"]:
            self.assertNotIn("node_modules", filepath)

    def test_max_depth(self):
        """Test maximum depth limiting"""
        scanner = CodebaseScanner(self.test_dir, max_depth=0)
        result = scanner.scan()

        # Should only get files at root level
        for filepath in result["files"]:
            self.assertEqual(filepath.count("/"), 0)

    def test_search_pattern(self):
        """Test search pattern functionality"""
        scanner = CodebaseScanner(self.test_dir, search_pattern="hello")
        result = scanner.scan()

        # Should only include files containing "hello"
        self.assertTrue(any("main.py" in f for f in result["files"]))
        self.assertFalse(any("utils.py" in f for f in result["files"]))

    def test_file_status_in_tree(self):
        """Test that tree shows file inclusion status"""
        scanner = CodebaseScanner(self.test_dir, include_patterns=["*.py"])
        result = scanner.scan()

        # Check that tree contains file status information
        def check_tree_has_status(tree):
            if "_files" in tree:
                for file_info in tree["_files"]:
                    if isinstance(file_info, dict):
                        self.assertIn("name", file_info)
                        self.assertIn("included", file_info)
                        self.assertIn("path", file_info)

            for key, value in tree.items():
                if key != "_files" and isinstance(value, dict):
                    check_tree_has_status(value)

        check_tree_has_status(result["tree"])

    def test_total_vs_included_files(self):
        """Test that total_files and file_count are tracked separately"""
        scanner = CodebaseScanner(self.test_dir, include_patterns=["*.py"])
        result = scanner.scan()

        # total_files should be greater than file_count (included files)
        # because we have .md files that aren't included
        self.assertIn("total_files", result)
        self.assertIn("file_count", result)
        self.assertGreaterEqual(result["total_files"], result["file_count"])


class TestFormatters(unittest.TestCase):
    """Test the formatter classes"""

    def setUp(self):
        """Create sample data for formatting"""
        self.data = {
            "root_dir": "/test/project",
            "file_count": 2,
            "total_files": 2,
            "files": ["src/main.py", "README.md"],
            "all_files": ["src/main.py", "README.md"],
            "tree": {
                "src": {
                    "_files": [
                        {"name": "main.py", "included": True, "path": "src/main.py"}
                    ]
                },
                "_files": [
                    {"name": "README.md", "included": True, "path": "README.md"}
                ],
            },
            "contents": {"src/main.py": "print('hello')", "README.md": "# Test"},
        }

    def test_text_formatter(self):
        """Test text formatter"""
        formatter = TextFormatter(color_scheme=get_color_scheme(enabled=False))
        output = formatter.format(self.data)

        self.assertIn("Codebase:", output)
        self.assertIn("Files to be logged:", output)
        self.assertIn("Total files found:", output)
        self.assertIn("Directory Structure:", output)
        self.assertIn("File Contents:", output)

    def test_markdown_formatter(self):
        """Test markdown formatter"""
        formatter = MarkdownFormatter()
        output = formatter.format(self.data)

        self.assertIn("# 📁 Codebase:", output)
        self.assertIn("## 📂 Directory Structure", output)
        self.assertIn("## 📄 File Contents", output)
        self.assertIn("```", output)

    def test_json_formatter(self):
        """Test JSON formatter"""
        formatter = JSONFormatter()
        output = formatter.format(self.data)

        import json

        parsed = json.loads(output)

        self.assertIn("root_dir", parsed)
        self.assertIn("file_count", parsed)
        self.assertIn("files_logged", parsed)
        self.assertIn("files_skipped", parsed)


class TestColors(unittest.TestCase):
    """Test color functionality"""

    def test_color_scheme_creation(self):
        """Test creating color schemes"""
        from codeview.colors import ColorScheme, get_color_scheme

        # Test auto-detection
        scheme1 = get_color_scheme()
        self.assertIsInstance(scheme1, ColorScheme)

        # Test forced enable
        scheme2 = get_color_scheme(enabled=True)
        self.assertIsInstance(scheme2, ColorScheme)

        # Test forced disable
        scheme3 = get_color_scheme(enabled=False)
        self.assertIsInstance(scheme3, ColorScheme)
        self.assertFalse(scheme3.enabled)

    def test_color_application(self):
        """Test that colors are applied correctly"""
        from codeview.colors import ColorScheme

        # With colors enabled - force it by creating ColorScheme directly
        colors_on = ColorScheme(enabled=True)
        # Manually set enabled to True to bypass environment detection
        colors_on.enabled = True
        colored_text = colors_on.header("Test")
        self.assertIn("\033[", colored_text)  # Should contain ANSI codes
        self.assertIn("Test", colored_text)

        # With colors disabled
        colors_off = ColorScheme(enabled=False)
        plain_text = colors_off.header("Test")
        self.assertEqual(plain_text, "Test")  # Should be plain text
        self.assertNotIn("\033[", plain_text)  # Should not contain ANSI codes

    def test_all_color_methods(self):
        """Test that all color methods work"""
        from codeview.colors import ColorScheme

        colors = ColorScheme(enabled=True)
        colors.enabled = True  # Force enable

        # Test all color methods
        methods = [
            "header",
            "subheader",
            "section",
            "directory",
            "file_logged",
            "file_skipped",
            "success",
            "warning",
            "error",
            "info",
            "marker_logged",
            "marker_skipped",
            "filepath",
            "line_number",
            "separator",
            "code_content",
            "stat_label",
            "stat_value",
            "legend",
        ]

        for method_name in methods:
            method = getattr(colors, method_name)
            result = method("test")
            self.assertIsInstance(result, str)
            self.assertIn("test", result)

    def test_formatter_with_colors(self):
        """Test that formatter uses colors correctly"""
        from codeview.colors import ColorScheme

        data = {
            "root_dir": "/test",
            "file_count": 1,
            "total_files": 1,
            "files": ["test.py"],
            "all_files": ["test.py"],
            "tree": {
                "_files": [{"name": "test.py", "included": True, "path": "test.py"}]
            },
            "contents": {"test.py": "print('hello')"},
        }

        # With colors - force enable
        color_scheme = ColorScheme(enabled=True)
        color_scheme.enabled = True  # Force enable
        formatter_color = TextFormatter(color_scheme=color_scheme)
        output_color = formatter_color.format(data)
        self.assertIn("\033[", output_color)  # Should contain ANSI codes

        # Without colors
        formatter_plain = TextFormatter(color_scheme=ColorScheme(enabled=False))
        output_plain = formatter_plain.format(data)
        self.assertNotIn("\033[", output_plain)  # Should not contain ANSI codes

    def test_formatter_shows_status(self):
        """Test that formatters show file status"""
        scanner_data = {
            "root_dir": "/test",
            "file_count": 1,
            "total_files": 2,
            "files": ["included.py"],
            "all_files": ["included.py", "excluded.txt"],
            "tree": {
                "_files": [
                    {"name": "included.py", "included": True, "path": "included.py"},
                    {"name": "excluded.txt", "included": False, "path": "excluded.txt"},
                ]
            },
            "contents": {"included.py": "print('test')"},
        }

        # Test text formatter
        text_formatter = TextFormatter(color_scheme=get_color_scheme(enabled=False))
        text_output = text_formatter.format(scanner_data)
        self.assertIn("✓", text_output)  # Should show included marker
        self.assertIn("✗", text_output)  # Should show excluded marker
        self.assertIn("LOGGED", text_output)
        self.assertIn("SKIPPED", text_output)

        # Test markdown formatter
        md_formatter = MarkdownFormatter()
        md_output = md_formatter.format(scanner_data)
        self.assertIn("✅", md_output)  # Should show included marker
        self.assertIn("❌", md_output)  # Should show excluded marker

        # Test JSON formatter
        json_formatter = JSONFormatter()
        json_output = json_formatter.format(scanner_data)
        self.assertIn("files_logged", json_output)
        self.assertIn("files_skipped", json_output)

        import json

        parsed = json.loads(json_output)
        self.assertEqual(len(parsed["files_logged"]), 1)
        self.assertEqual(len(parsed["files_skipped"]), 1)


if __name__ == "__main__":
    unittest.main()
