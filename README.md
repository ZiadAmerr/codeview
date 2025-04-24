# CodeView

[![PyPI version](https://img.shields.io/pypi/v/codeview.svg)](https://pypi.org/project/codeview/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/codeview.svg)](https://pypi.org/project/codeview/)

## Overview

CodeView is a powerful command-line utility designed to help developers effectively communicate their codebases to Large Language Models (LLMs) like ChatGPT, Claude, and Gemini. It solves the common problem of needing to share multiple files and directory structures with LLMs in a clean, organized format.

**Key Features:**

- 📁 Visualizes directory structures with customizable depth
- 📝 Displays file contents with optional syntax highlighting and line numbers
- 🔍 Flexible filtering by file type, directory, or content patterns
- 📤 Multiple output formats (text, markdown, JSON) for different LLM platforms
- 💾 Save output to a file or display in terminal
- 🚀 Easy to install and use with intuitive CLI interface

## Installation

### Prerequisites

- Python 3.6 or higher
- The `tree` command:
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install tree`
  - **macOS**: `brew install tree`
  - **Windows**: Available via [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/) or [Git Bash](https://gitforwindows.org/)

### Install from PyPI

```bash
pip install codeview
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/codeview.git
cd codeview

# Install in development mode
pip install -e .
```

## Quick Start

Generate a view of your entire codebase:

```bash
codeview
```

Create a Markdown file for sharing with an LLM:

```bash
codeview -m markdown -o my_project.md
```

Focus on specific file types:

```bash
codeview -i "*.py" -i "*.js"
```

## Detailed Usage

```
codeview [options]
```

### Options

| Option | Long Form | Description | Example |
|--------|-----------|-------------|---------|
| `-h` | `--help` | Display help message | `codeview -h` |
| `-i PATTERN` | `--include PATTERN` | File patterns to include (can use multiple times) | `codeview -i "*.py" -i "*.js"` |
| `-e DIR` | `--exclude-dir DIR` | Directories to exclude (can use multiple times) | `codeview -e node_modules -e .venv` |
| `-x PATTERN` | `--exclude-file PATTERN` | File patterns to exclude (can use multiple times) | `codeview -x "*.pyc" -x "*.log"` |
| `-d DEPTH` | `--max-depth DEPTH` | Maximum directory depth to traverse | `codeview -d 2` |
| `-t` | `--no-tree` | Don't show directory tree | `codeview -t` |
| `-f` | `--no-files` | Don't show file contents | `codeview -f` |
| `-n` | `--line-numbers` | Show line numbers in file contents | `codeview -n` |
| `-o FILE` | `--output FILE` | Write output to file instead of stdout | `codeview -o project.txt` |
| `-s PATTERN` | `--search PATTERN` | Only include files containing the pattern | `codeview -s "def main"` |
| `-p DIR` | `--path DIR` | Include specific directory (can use multiple times) | `codeview -p src/models -p tests` |
| `-m FORMAT` | `--format FORMAT` | Output format: text, markdown, json | `codeview -m markdown` |

### Default Values

- **Include Patterns**: `*.py`, `*.md`, `*.js`, `*.html`, `*.css`, `*.json`, `*.yaml`, `*.yml`
- **Exclude Directories**: `myenv`, `venv`, `.venv`, `node_modules`, `.git`, `__pycache__`, `.pytest_cache`, `build`, `dist`
- **Exclude Files**: `*.pyc`, `*.pyo`, `*.pyd`, `*.so`, `*.dll`, `*.class`, `*.egg-info`, `*.egg`
- **Max Depth**: No limit
- **Output Format**: text

## Use Cases

### Working with LLMs on Your Projects

```bash
# Generate a Markdown overview of your Python project
codeview -i "*.py" -m markdown -o project_for_llm.md

# Then upload the markdown file to your favorite LLM platform
```

### Focusing on Specific Components

```bash
# Show only model and controller files
codeview -p src/models -p src/controllers -i "*.py"

# View only files containing authentication logic
codeview -s "def authenticate" -s "class Auth"
```

### Collaborating with Team Members

```bash
# Create a JSON representation for programmatic use
codeview -m json -o project_structure.json

# Generate documentation of the core modules
codeview -p src/core -m markdown -o core_modules.md
```

## Output Formats

### Text (Default)

```
**./src/main.py**
def main():
    print("Hello, world!")
    
if __name__ == "__main__":
    main()
```

### Markdown

````markdown
## ./src/main.py

```python
def main():
    print("Hello, world!")
    
if __name__ == "__main__":
    main()
```
````

### JSON

```json
{
  "files": [
    {
      "path": "./src/main.py",
      "content": "def main():\n    print(\"Hello, world!\")\n    \nif __name__ == \"__main__\":\n    main()"
    }
  ]
}
```

## Effective Use with LLMs

1. **Filter appropriately**: Only include relevant files to stay within token limits
2. **Use markdown format** for better readability with most LLMs
3. **Include line numbers** (`-n`) when discussing specific code sections
4. **Exclude large/binary files** to avoid token waste
5. **Limit depth** (`-d`) for large projects to focus on high-level structure

## Troubleshooting

### Common Issues

#### "Command not found: tree"

- Install the `tree` command using your package manager:

  ```bash
  # Debian/Ubuntu
  sudo apt-get install tree
  
  # macOS
  brew install tree
  ```

#### "Files not showing up"

- Check your include/exclude patterns
- Make sure you're running from the correct directory
- Use the `-v` flag for verbose output to see what's happening

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-amazing-feature`)
3. Commit your changes (`git commit -m 'Add some new amazing feature'`)
4. Push to the branch (`git push origin feature/new-amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits
Inspired by the need to efficiently share code with LLMs

---

If you find CodeView useful, please consider ⭐ starring the repository on GitHub!
