import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="oom_investigate",
    version="1.0.0",
    description="Investigate out of memory (OOM) errors in log files",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/LukeShirnia/out-of-memory",
    author="Luke Shirnia",
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="OOM, oom, out-of-memory, investigate, log, files",
    py_modules=["oom_investigate"],
    python_requires=">=2.7, <4",
    # Entry points. The following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        "console_scripts": [
            "oom_investigate=oom_investigate:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/LukeShirnia/out-of-memory/issues",
        "Source": "https://github.com/LukeShirnia/out-of-memory",
    },
)
