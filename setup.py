from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ml-supertrend-mt5",
    version="1.0.0",
    author="xPOURY4",
    author_email="",
    description="Advanced SuperTrend trading bot for MetaTrader 5 with Machine Learning clustering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xPOURY4/ML-SuperTrend-MT5",
    project_urls={
        "Bug Tracker": "https://github.com/xPOURY4/ML-SuperTrend-MT5/issues",
        "Documentation": "https://github.com/xPOURY4/ML-SuperTrend-MT5#readme",
        "Source Code": "https://github.com/xPOURY4/ML-SuperTrend-MT5",
        "Twitter": "https://twitter.com/TheRealPourya",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ml-supertrend=run_bot:main",
        ],
    },
    keywords="trading forex metatrader5 mt5 supertrend machine-learning algorithmic-trading",
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
)