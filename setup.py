from setuptools import setup, find_packages
import os

# 确保 README.md 文件存在
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "本地知识管理与检索系统，支持多种文档格式，提供向大语言模型的知识集成"

setup(
    name="local-knowledge",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=[
        "mcp",
    ],
    entry_points={
        'console_scripts': [
            'local-knowledge=local_knowledge.__main__:main',
        ],
    },
    author="Your Organization",
    author_email="contact@example.com",
    description="本地知识管理服务，用于保存和向大模型提供本地知识",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="knowledge, LLM, local, RAG, retrieval, document",
    url="https://github.com/yourusername/local-knowledge",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.json', '*.yaml', '*.yml'],
        'local_knowledge': ['*'],
    },
    zip_safe=False,
)
