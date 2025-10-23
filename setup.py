from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="quantumtrader-mt5",
    version="2.0.0",
    author="Trần Trọng Hiếu",
    author_email="",
    description="Next-Generation Algorithmic Trading Platform for MetaTrader 5 with ML, ICT/SMC Strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thales1020/QuantumTrader-MT5",
    project_urls={
        "Bug Tracker": "https://github.com/thales1020/QuantumTrader-MT5/issues",
        "Documentation": "https://github.com/thales1020/QuantumTrader-MT5#readme",
        "Source Code": "https://github.com/thales1020/QuantumTrader-MT5",
        "Author": "https://github.com/thales1020",
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
            "quantumtrader=run_bot:main",
        ],
    },
    keywords="trading forex metatrader5 mt5 quantum machine-learning algorithmic-trading ict smc supertrend",
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
)