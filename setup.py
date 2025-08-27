from setuptools import setup, find_packages

setup(
    name="datareplicator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pandas>=2.1.1",
        "numpy>=1.26.0",
        "scikit-learn>=1.3.2",
        "sqlalchemy>=2.0.23",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
        "python-multipart>=0.0.6",
        "httpx>=0.25.0",
        "faker>=19.13.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
    ],
    author="DataReplicator Team",
    author_email="team@datareplicator.com",
    description="A tool for analyzing clinical trial datasets and generating additional synthetic data",
    keywords="clinical-trials, data-generation, synthetic-data",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)
