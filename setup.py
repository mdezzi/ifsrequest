from setuptools import setup, find_packages

setup(
    name="ifsrequest",              
    version="0.1.0",
    packages=find_packages(),
    install_requires=['requests','urllib'],           # add dependencies here
    author="Matthew Dezzi",
    description="Requests wrapper that will handle IFS token retrieval automatically",
    python_requires=">=3.7",
)