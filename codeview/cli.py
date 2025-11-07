#!/usr/bin/env python3
"""
Command-line interface for codeview
"""

import argparse
import sys
from pathlib import Path
from .scanner import CodebaseScanner
from .formatters import TextFormatter, MarkdownFormatter, JSONFormatter
from .colors import get_color_scheme


def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        prog="codeview",
        description="A tool to visualize codebases for LLM interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codeview                             # Show all code files in current directory
  codeview -i "*.py" -i "*.js"         # Only show Python and JavaScript files
  codeview -e node_modules -e .git     # Exclude node_modules and .git directories
  codeview -d 2                        # Only traverse 2 directory levels deep
  codeview -s "def main"               # Only show files containing 'def main'
  codeview -p src/models -p src/utils  # Only include specific directories
  codeview -m markdown -o codebase.md  # Output in markdown format to a file
  codeview --no-color                  # Disable colored output
        """,
    )

    parser.add_argument(
        "-i",
        "--include",
        action="append",
        dest="include_patterns",
        metavar="PATTERN",
        help="File patterns to include (can be used multiple times)",
    )

    parser.add_argument(
        "-e",
        "--exclude-dir",
        action="append",
        dest="exclude_dirs",
        metavar="DIR",
        help="Directories to exclude (can be used multiple times)",
    )

    parser.add_argument(
        "-x",
        "--exclude-file",
        action="append",
        dest="exclude_patterns",
        metavar="PATTERN",
        help="File patterns to exclude (can be used multiple times)",
    )

    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        metavar="DEPTH",
        help="Maximum directory depth to traverse",
    )

    parser.add_argument(
        "-t", "--no-tree", action="store_true", help="Don't show directory tree"
    )

    parser.add_argument(
        "-f", "--no-files", action="store_true", help="Don't show file contents"
    )

    parser.add_argument(
        "-n",
        "--line-numbers",
        action="store_true",
        help="Show line numbers in file contents",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="FILE",
        help="Write output to file instead of stdout",
    )

    parser.add_argument(
        "-s",
        "--search",
        type=str,
        metavar="PATTERN",
        help="Only include files containing the pattern",
    )

    parser.add_argument(
        "-p",
        "--path",
        action="append",
        dest="paths",
        metavar="DIR",
        help="Include specific directory (can be used multiple times)",
    )

    parser.add_argument(
        "-m",
        "--format",
        type=str,
        choices=["text", "markdown", "json"],
        default="text",
        metavar="FORMAT",
        help="Output format: text (default), markdown, json",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    parser.add_argument(
        "--force-color",
        action="store_true",
        help="Force colored output even when piping",
    )

    return parser


def main():
    """Main entry point for the CLI"""
    parser = create_parser()
    args = parser.parse_args()

    # Determine root directory
    root_dir = Path.cwd()

    # Create scanner with options
    scanner = CodebaseScanner(
        root_dir=root_dir,
        include_patterns=args.include_patterns,
        exclude_dirs=args.exclude_dirs,
        exclude_patterns=args.exclude_patterns,
        max_depth=args.max_depth,
        search_pattern=args.search,
        specific_paths=args.paths,
    )

    # Scan the codebase
    try:
        result = scanner.scan()
    except Exception as e:
        colors = get_color_scheme(enabled=not args.no_color)
        print(colors.error(f"Error scanning codebase: {e}"), file=sys.stderr)
        sys.exit(1)

    # Determine color support
    # Disable colors for non-text formats or when writing to file
    use_color = not args.no_color
    if args.force_color:
        use_color = True
    if args.format != "text" or args.output:
        use_color = False

    # Select formatter
    if args.format == "markdown":
        formatter = MarkdownFormatter()
    elif args.format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter(color_scheme=get_color_scheme(enabled=use_color))

    # Format output
    output = formatter.format(
        result,
        show_tree=not args.no_tree,
        show_files=not args.no_files,
        line_numbers=args.line_numbers,
    )

    # Write output
    if args.output:
        try:
            output_path = Path(args.output)
            output_path.write_text(output, encoding="utf-8")
            colors = get_color_scheme(enabled=not args.no_color)
            print(
                colors.success(f"✓ Output written to {args.output}"),
                file=sys.stderr,
            )
        except Exception as e:
            colors = get_color_scheme(enabled=not args.no_color)
            print(colors.error(f"Error writing to file: {e}"), file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == "__main__":
    main()
