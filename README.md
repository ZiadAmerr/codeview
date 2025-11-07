# CodeView

A powerful tool to visualize codebases for LLM interactions and documentation purposes.

## Features

- 🌳 **Directory Tree Visualization**: Display your codebase structure in a clear, hierarchical format
- 📄 **File Content Display**: Show the contents of all code files with optional line numbers
- 🔍 **Smart Filtering**: Include/exclude files and directories with pattern matching
- 🎯 **Search Functionality**: Find files containing specific patterns
- 📊 **Multiple Output Formats**: Text, Markdown, and JSON formats
- 🚀 **Fast and Lightweight**: No external dependencies, uses only Python standard library

## Installation

### From PyPI (when published)

```bash
pip install codeview
```

### From Source

```bash
git clone https://github.com/ZiadAmerr/codeview.git
cd codeview
pip install -e .
```

## Usage

### Basic Usage

Show all code files in the current directory:

```bash
codeview
```

### Common Examples

Only show Python and JavaScript files:

```bash
codeview -i "*.py" -i "*.js"
```

Exclude specific directories:

```bash
codeview -e node_modules -e .git
```

Limit directory traversal depth:

```bash
codeview -d 2
```

Search for files containing a specific pattern:

```bash
codeview -s "def main"
```

Include only specific directories:

```bash
codeview -p src/models -p src/utils
```

Output to a markdown file:

```bash
codeview -m markdown -o codebase.md
```

Show line numbers:

```bash
codeview -n
```

### All Options

```
Options:
  -h, --help                 Show this help message
  -i, --include PATTERN      File patterns to include (can be used multiple times)
  -e, --exclude-dir DIR      Directories to exclude (can be used multiple times)
  -x, --exclude-file PATTERN File patterns to exclude (can be used multiple times)
  -d, --max-depth DEPTH      Maximum directory depth to traverse
  -t, --no-tree              Don't show directory tree
  -f, --no-files             Don't show file contents
  -n, --line-numbers         Show line numbers in file contents
  -o, --output FILE          Write output to file instead of stdout
  -s, --search PATTERN       Only include files containing the pattern
  -p, --path DIR             Include specific directory (can be used multiple times)
  -m, --format FORMAT        Output format: text (default), markdown, json
```

## Use Cases

### 1. LLM Context Preparation

Prepare your codebase for sharing with LLMs like ChatGPT or Claude:

```bash
codeview -m markdown -o codebase.md
```

### 2. Code Documentation

Generate documentation of your project structure:

```bash
codeview -t -m markdown -o structure.md
```

### 3. Code Review

Extract specific parts of your codebase for review:

```bash
codeview -p src/critical -n -o review.txt
```

### 4. Project Analysis

Get a JSON representation for programmatic analysis:

```bash
codeview -m json -o analysis.json
```

## Default Behavior

### Included File Types

By default, CodeView includes common code file types:
- Python (*.py)
- JavaScript/TypeScript (*.js, *.jsx, *.ts, *.tsx)
- Java (*.java)
- C/C++ (*.c, *.cpp, *.h, *.hpp)
- And many more...

### Excluded Directories

By default, CodeView excludes common non-code directories:
- Version control (.git, .svn, .hg)
- Dependencies (node_modules, venv, .venv)
- Build artifacts (dist, build, *.egg-info)
- IDE files (.idea, .vscode)

## Python API

You can also use CodeView programmatically:

```python
from pathlib import Path
from codeview import CodebaseScanner, MarkdownFormatter

# Create scanner
scanner = CodebaseScanner(
    root_dir=Path.cwd(),
    include_patterns=["*.py"],
    exclude_dirs=["tests"]
)

# Scan codebase
result = scanner.scan()

# Format output
formatter = MarkdownFormatter()
output = formatter.format(result, show_tree=True, show_files=True)

print(output)
```

## File Status Indicators

CodeView now shows which files will be logged (included in output) and which will be skipped:

### Text Format
```
Directory Structure:
--------------------------------------------------------------------------------
├── [✓] main.py  (LOGGED)
├── [✗] test.txt  (SKIPPED)
└── src/
    ├── [✓] utils.py  (LOGGED)
    └── [✗] backup.bak  (SKIPPED)
```

### Markdown Format
```markdown
## Directory Structure

- ✅ main.py **LOGGED**
- ❌ test.txt ~~SKIPPED~~
- **src/**
  - ✅ utils.py **LOGGED**
  - ❌ backup.bak ~~SKIPPED~~
```

### JSON Format
```json
{
  "file_count": 2,
  "total_files": 4,
  "files_logged": ["main.py", "src/utils.py"],
  "files_skipped": ["test.txt", "src/backup.bak"],
  "tree": {
    "_files": [
      {"name": "main.py", "included": true, "path": "main.py"},
      {"name": "test.txt", "included": false, "path": "test.txt"}
    ]
  }
}
```

This makes it easy to see at a glance which files match your filters and will be included in the output.

## Colored Output

CodeView supports beautiful colored terminal output to make the information easier to read and parse visually.

### Color Features

- **Headers**: Bright cyan for main headers, blue for subheaders
- **Directories**: Bold blue for directory names
- **Logged Files**: Green for files that will be included in output
- **Skipped Files**: Dimmed gray for files that will be excluded
- **Markers**: Bright green ✓ for logged, bright red ✗ for skipped
- **Statistics**: Yellow for numbers, white for labels
- **File Paths**: Magenta for file paths in content sections
- **Line Numbers**: Dimmed yellow for line numbers
- **Separators**: Dimmed gray for visual separators

### Color Control

```bash
# Default: Auto-detect color support
codeview

# Explicitly disable colors
codeview --no-color

# Force colors even when piping
codeview --force-color | less -R

# Colors are automatically disabled when:
# - Output is redirected to a file (-o option)
# - Output format is markdown or json
# - NO_COLOR environment variable is set
# - Terminal doesn't support ANSI colors
```

### Environment Variables

- `NO_COLOR`: Set to any value to disable colors
- `FORCE_COLOR`: Set to any value to force enable colors
- `TERM`: Used to detect color support (set to 'dumb' to disable)

### Example Output

When colors are enabled, you'll see:
- 📁 **Bright cyan** codebase header
- 📂 **Blue** directory structure section
- **Green** ✓ for files that will be logged
- **Red** ✗ for files that will be skipped
- **Magenta** file paths in content sections
- **Yellow** statistics and line numbers

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Ziad Amerr - Ziad.amerr@yahoo.com
