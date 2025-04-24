import os
import json
import tempfile
import subprocess
import unittest
import shutil
import json


CODEVIEW_CMD = "codeview"


class CodeViewTestCase(unittest.TestCase):
    """Base test class for CodeView tests"""

    def setUp(self):
        """Set up a temporary directory with test files"""
        self.test_dir = tempfile.mkdtemp()

        # Create a simple test project structure
        self.project_structure = {
            "src": {
                "main.py": "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()",
                "utils.py": "def helper():\n    return 'I am a helper function'\n",
                "models": {
                    "user.py": "class User:\n    def __init__(self, name):\n        self.name = name\n",
                    "product.py": "class Product:\n    def __init__(self, name, price):\n        self.name = name\n        self.price = price\n",
                },
            },
            "tests": {
                "test_main.py": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_main(self):\n        pass\n",
                "test_utils.py": "import unittest\n\nclass TestUtils(unittest.TestCase):\n    def test_helper(self):\n        pass\n",
            },
            "README.md": "# Test Project\n\nThis is a test project for CodeView.\n",
            ".git": {"HEAD": "ref: refs/heads/main\n"},
            "node_modules": {
                "package": {"index.js": "console.log('Hello from package');\n"}
            },
            "build.py": "# This should be included\n",
            "setup.cfg": "# Configuration file\n",
            "data.bin": b"\x00\x01\x02\x03",  # Binary file
            "requirements.txt": "pytest==7.3.1\npytest-cov==4.1.0\n",
        }

        self._create_file_structure(self.test_dir, self.project_structure)

        # Save current working directory and change to test directory
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up the temporary directory"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def _create_file_structure(self, base_path, structure):
        """Create a file structure based on dictionary representation"""
        for name, content in structure.items():
            path = os.path.join(base_path, name)

            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                self._create_file_structure(path, content)
            else:
                # Ensure directory exists
                os.makedirs(os.path.dirname(path), exist_ok=True)

                # Write content to file
                mode = "wb" if isinstance(content, bytes) else "w"
                with open(path, mode) as f:
                    f.write(content)

    def run_codeview(self, args=None):
        """Run the codeview command with given arguments"""
        cmd = [CODEVIEW_CMD]
        if args:
            cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        return result


class BasicFunctionalityTests(CodeViewTestCase):
    """Test basic functionality of CodeView"""

    def test_default_output(self):
        """Test the default output of codeview"""
        result = self.run_codeview()

        # Check exit code
        self.assertEqual(result.returncode, 0)

        # Check that standard files are included
        self.assertIn("src/main.py", result.stdout)
        self.assertIn("def main():", result.stdout)
        self.assertIn("README.md", result.stdout)

        # Directory structure should be shown
        self.assertIn("Directory Structure:", result.stdout)

    def test_include_pattern(self):
        """Test including specific file patterns"""
        result = self.run_codeview(["-i", "*.py"])

        # Check exit code
        self.assertEqual(result.returncode, 0)

        # Python files should be included
        self.assertIn("src/main.py", result.stdout)

        # Check for file content
        self.assertIn("def main():", result.stdout)

    def test_exclude_dir(self):
        """Test excluding specific directories"""
        result = self.run_codeview(["-e", "tests"])

        print(json.dumps(result.__dict__, indent=4))

        # Check that test files are excluded
        self.assertNotIn("./tests/test_main.py", result.stdout)

        # Other files should still be included
        self.assertIn("./src/main.py", result.stdout)

    def test_exclude_file(self):
        """Test excluding specific file patterns"""
        result = self.run_codeview(["-x", "*.md"])

        # Check for files that should still be included
        self.assertIn("src/main.py", result.stdout)

        # Look for content from README.md that should be excluded
        self.assertNotIn("Test Project", result.stdout)

    def test_max_depth(self):
        """Test maximum directory depth"""
        result = self.run_codeview(["-d", "1"])

        # Files in subdirectories beyond depth 1 should not be included as content
        self.assertNotIn("class User", result.stdout)
        self.assertNotIn("class Product", result.stdout)

    def test_no_tree(self):
        """Test that we can hide the tree view"""
        result = self.run_codeview(["-t"])

        # Directory structure visualization should not be included
        self.assertNotIn("├──", result.stdout)

        # File contents should still be shown
        self.assertIn("def main():", result.stdout)

    def test_no_files(self):
        """Test that we can hide file contents"""
        result = self.run_codeview(["-f"])

        # Directory structure visualization should be included
        self.assertIn("Directory Structure:", result.stdout)

        # File contents should not be shown
        self.assertNotIn("def main():", result.stdout)

    def test_line_numbers(self):
        """Test showing line numbers"""
        result = self.run_codeview(["-n"])

        print(json.dumps(result.__dict__, indent=4))

        self.assertIn("1\tdef main():", result.stdout)


class OutputFormatTests(CodeViewTestCase):
    """Test different output formats"""

    def test_text_format(self):
        """Test the text output format"""
        result = self.run_codeview(["-m", "text"])

        # Check that format is correct - adapted to actual output
        self.assertIn("**./src/main.py", result.stdout)
        self.assertIn("def main():", result.stdout)

    def test_markdown_format(self):
        """Test the markdown output format"""
        result = self.run_codeview(["-m", "markdown"])

        # Check that format is correct
        self.assertIn("## ./src/main.py", result.stdout)
        self.assertIn("```py", result.stdout)
        self.assertIn("def main():", result.stdout)
        self.assertIn("```", result.stdout)

    def test_json_format(self):
        """Test the JSON output format"""
        result = self.run_codeview(["-m", "json"])

        # Just check for JSON-like structure without parsing
        self.assertIn('"files":', result.stdout)
        self.assertIn('"path":', result.stdout)
        self.assertIn('"content":', result.stdout)


class FileOperationTests(CodeViewTestCase):
    """Test file operations"""

    def test_output_to_file(self):
        """Test writing output to a file"""
        output_file = os.path.join(self.test_dir, "output.txt")
        result = self.run_codeview(["-o", output_file])

        # Check that the command succeeded
        self.assertEqual(result.returncode, 0)

        # Check that the file was created
        self.assertTrue(os.path.exists(output_file))

        # Check file contents
        with open(output_file, "r") as f:
            content = f.read()
            self.assertIn("main.py", content)

    def test_search_pattern(self):
        """Test searching for specific content"""
        result = self.run_codeview(["-s", "helper"])

        # Files containing the pattern should be included
        self.assertIn("I am a helper function", result.stdout)

        # Files not containing the pattern should be excluded
        self.assertNotIn("print('Hello, world!')", result.stdout)

    def test_include_path(self):
        """Test including specific paths"""
        result = self.run_codeview(["-p", "src/models"])

        # Check for content from the models directory
        self.assertIn("class User", result.stdout)
        self.assertIn("class Product", result.stdout)

        # Files not in the specified path should be excluded
        self.assertNotIn("def main():", result.stdout)


class EdgeCaseTests(CodeViewTestCase):
    """Test edge cases and error handling"""

    def test_empty_directory(self):
        """Test running on an empty directory"""
        # Create a new empty directory
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)

        # Change to the empty directory
        os.chdir(empty_dir)

        result = self.run_codeview()

        # Check that it runs without error
        self.assertEqual(result.returncode, 0)

    def test_invalid_format(self):
        """Test with invalid output format"""
        result = self.run_codeview(["-m", "invalid_format"])

        # Should return an error
        self.assertEqual(result.returncode, 1)
        self.assertIn("error", result.stderr.lower())

    def test_nonexistent_path(self):
        """Test with a non-existent path"""
        result = self.run_codeview(["-p", "nonexistent"])

        # Just verify it runs without exception
        # The command might succeed but provide different output
        pass

    def test_binary_file_filtering(self):
        """Test handling of binary files with explicit exclusion"""
        result = self.run_codeview(["-x", "*.bin"])

        # Binary files should be excluded from file content
        self.assertNotIn("data.bin", result.stdout)


class ComplexTests(CodeViewTestCase):
    """Test complex scenarios"""

    def test_multiple_filter_combinations(self):
        """Test using multiple include/exclude filters together"""
        result = self.run_codeview(["-i", "*.py", "-e", "tests", "-x", "setup.py"])

        # Should include Python files
        self.assertIn("src/main.py", result.stdout)

        # Should exclude test directory files
        self.assertNotIn("test_main.py", result.stdout)

        # Should exclude specific excluded Python file
        self.assertNotIn("setup.py", result.stdout)
    
    def test_unicode_content(self):
        """Test handling files with Unicode characters"""
        # Create a file with Unicode content
        with open(os.path.join(self.test_dir, "unicode_file.py"), "w", encoding="utf-8") as f:
            f.write(
                '# -*- coding: utf-8 -*-\n\ndef unicode_func():\n    return "こんにちは世界"\n')

        result = self.run_codeview(["-i", "unicode_file.py"])
        self.assertIn("こんにちは世界", result.stdout)
    
    def test_large_file_handling(self):
        """Test handling of relatively large files"""
        # Create a large Python file
        with open(os.path.join(self.test_dir, "large_file.py"), "w") as f:
            f.write("# Large file test\n")
            for i in range(1000):
                f.write(f"# Line {i}\ndef func_{i}():\n    return {i}\n\n")

        # Just verify it runs without error
        result = self.run_codeview(["-i", "large_file.py"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("large_file.py", result.stdout)

    def test_different_language_highlighting(self):
        """Test syntax highlighting for different languages"""
        # Create files with different extensions
        with open(os.path.join(self.test_dir, "script.js"), "w") as f:
            f.write("function hello() { return 'world'; }\n")
        with open(os.path.join(self.test_dir, "styles.css"), "w") as f:
            f.write("body { color: red; }\n")

        # Check markdown output uses correct language tags
        result = self.run_codeview(["-i", "*.js", "-i", "*.css", "-m", "markdown"])
        self.assertIn("```js", result.stdout)
        self.assertIn("```css", result.stdout)
    
    def test_json_output_validity(self):
        """Test that JSON output is actually valid JSON"""
        result = self.run_codeview(["-m", "json", "-t"])

        # Try to parse the output as JSON
        try:
            parsed = json.loads(result.stdout)
            self.assertIn("files", parsed)
            self.assertTrue(isinstance(parsed["files"], list))
        except json.JSONDecodeError:
            self.fail("JSON output is not valid JSON")
    
    def test_empty_files(self):
        """Test handling of empty files"""
        # Create an empty file
        with open(os.path.join(self.test_dir, "empty.py"), "w") as f:
            pass

        result = self.run_codeview(["-i", "empty.py"])
        self.assertIn("empty.py", result.stdout)


    def test_files_with_special_chars(self):
        """Test handling of files with special characters in names"""
        # Create a file with special characters in the name
        special_filename = "special@#$%^&.py"
        with open(os.path.join(self.test_dir, special_filename), "w") as f:
            f.write("# File with special characters in name\n")

        result = self.run_codeview(["-i", special_filename])
        self.assertIn(special_filename, result.stdout)
    
    def test_command_line_args_from_shell(self):
        """Test running codeview with shell-style arguments"""
        # This simulates how the command would be used in a shell
        cmd = CODEVIEW_CMD + " -i '*.py' -e 'tests' -m markdown"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("```py", result.stdout)

    def test_different_language_highlighting(self):
        """Test syntax highlighting for different languages"""
        # Create files with different extensions
        with open(os.path.join(self.test_dir, "script.js"), "w") as f:
            f.write("function hello() { return 'world'; }\n")
        with open(os.path.join(self.test_dir, "styles.css"), "w") as f:
            f.write("body { color: red; }\n")

        # Check markdown output uses correct language tags
        result = self.run_codeview(["-i", "*.js", "-i", "*.css", "-m", "markdown"])
        self.assertIn("```js", result.stdout)
        self.assertIn("```css", result.stdout)
    
    def test_no_colors_in_output_if_output_file(self):
        """Test that colors are not included in output if writing to a file"""
        output_file = os.path.join(self.test_dir, "output.txt")
        result = self.run_codeview(["-o", output_file])

        # Check that the command succeeded
        self.assertEqual(result.returncode, 0)

        # Check that the file was created
        self.assertTrue(os.path.exists(output_file))

        # Check file contents
        with open(output_file, "r") as f:
            content = f.read()
            self.assertNotIn("\033[", content)

if __name__ == "__main__":
    unittest.main()
