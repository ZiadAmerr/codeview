from setuptools import setup, find_packages

setup(
    name="codeview",
    version="0.0.1",
    description="A tool to visualize codebases for LLM interactions",
    author="Ziad Amerr",
    author_email="ziad.amerr@example.com",
    url="https://github.com/ZiadAmerr/",
    scripts=["bin/codeview"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
