from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codeview",
    version="1.0.0",
    author="Ziad Amerr",
    author_email="Ziad.amerr@yahoo.com",
    description="A powerful tool to visualize codebases for LLM interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZiadAmerr/codeview",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "codeview=codeview.cli:main",
        ],
    },
    keywords="code visualization llm ai development documentation codebase",
    project_urls={
        "Bug Reports": "https://github.com/ZiadAmerr/codeview/issues",
        "Source": "https://github.com/ZiadAmerr/codeview",
    },
)
