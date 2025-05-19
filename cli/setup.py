from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="unify-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="CLI tool for managing the Shoe Production Manager application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shoe-production-manager",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.4.0",
        "rich>=10.0.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "unify=unify_cli.__main__:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
