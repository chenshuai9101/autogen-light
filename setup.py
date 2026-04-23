from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="autogen-light",
    version="2.0.0",
    description="轻量级多智能体协作框架 - 3行定义Agent，5行跑起团队协作",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="牧云野",
    packages=find_packages(exclude=["examples*", "docs*", "tests*"]),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
