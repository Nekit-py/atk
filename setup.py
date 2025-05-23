# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="atk",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "pydantic[email]>=2.0.0",
        "aiosmtplib>=2.0.0",
        "pandas>=2.0.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "development": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    author="Nekit-py",
    author_email="nekit-py@yandex.ru",
    description="Инструменты для автоматизации",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nekit-py/atk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
