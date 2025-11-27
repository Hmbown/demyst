from setuptools import setup, find_packages
import os

# Read README if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="scilint",
    version="1.0.0",
    author="Scilint Team",
    description="The Scientific Integrity Platform for AI Research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scilint/scilint",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "torch": ["torch>=1.9.0"],
        "jax": ["jax>=0.3.0", "jaxlib>=0.3.0"],
        "tracking": ["wandb>=0.12.0", "mlflow>=1.20.0"],
        "all": [
            "torch>=1.9.0",
            "jax>=0.3.0",
            "jaxlib>=0.3.0",
            "wandb>=0.12.0",
            "mlflow>=1.20.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'scilint=scilint.cli:main',
        ],
    },
)
