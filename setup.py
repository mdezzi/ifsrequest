"""Packaging configuration for the *ifsrequest* library.

The ``setup.py`` script follows the classic ``setuptools`` layout while
exposing a helpful ``long_description`` pulled from the project's README.
This improves the package's appearance on PyPI and mirrors the suggestions
from the earlier review (item 13).
"""

from pathlib import Path
from setuptools import find_packages, setup

# ---------------------------------------------------------------------------
# Helper to read the README – fallback to a short description if the file is
# missing (e.g. when building in a minimal CI environment).
# ---------------------------------------------------------------------------
here = Path(__file__).parent
readme_path = here / "README.md"
if readme_path.is_file():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = (
        "Requests wrapper that handles IFS token retrieval automatically."
    )

setup(
    name="ifsrequest",
    version="0.3.4b",
    packages=find_packages(),
    install_requires=["requests"],
    author="Matthew Dezzi",
    description="Requests wrapper that will handle IFS token retrieval automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/mdezzi/ifsrequest",  # replace with actual repo URL if any
)