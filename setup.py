from setuptools import setup, find_packages

setup(
    name="aicache",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "aicache = aicache.cli:main",
        ],
    },
    install_requires=[
        "PyYAML",
        "rank-bm25",
        "sentence-transformers",
        "numpy",
        "chromadb",
        "faiss-cpu",
        "nltk",
        "Pillow",
        "nbformat",
        "aiofiles",
        "aiosqlite",
        "msgpack",
        "ollama",
    ],
)
