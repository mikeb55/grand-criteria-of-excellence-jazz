"""
Open Triad Engine v1.0 - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="open-triad-engine",
    version="1.0.0",
    author="GCE-Jazz Project",
    author_email="",
    description="A modular generative engine for open triad voicings, voice leading, and musical pattern generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gce-jazz/open-triad-engine",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "pdf": [
            "weasyprint>=60.0",
        ],
        "midi": [
            "mido>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "open-triad-demo=examples.demo_all_modes:main",
        ],
    },
    include_package_data=True,
    keywords=[
        "music",
        "triads",
        "voice-leading",
        "jazz",
        "harmony",
        "composition",
        "music-theory",
        "musicxml",
    ],
)

