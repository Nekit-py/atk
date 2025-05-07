from setuptools import setup, find_packages

setup(
    name="atk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
    ],
    author="Nekit-py",
    author_email="nekit-py@yandex.ru",
    description="Инструменты для автоматизации",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nekit-py/atk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
