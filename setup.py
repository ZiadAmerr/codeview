from setuptools import setup, find_packages

setup(
    name="codeview",
    version="0.0.5",
    description="A tool to visualize codebases for LLM interactions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ziad Amerr",
    author_email="ziad.amerr@example.com",
    url="https://github.com/ZiadAmerr/codeview",
    scripts=["bin/codeview"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    keywords="code, llm, visualization, development",
    install_requires=[],
)
