from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reliquary-sdk",
    version="1.0.0",
    author="ReliQuary Team",
    author_email="support@reliquary.io",
    description="Enterprise Python SDK for ReliQuary multi-agent consensus platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reliquary/sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/reliquary/sdk-python/issues",
        "Documentation": "https://docs.reliquary.io/sdk/python",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "typing_extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
)