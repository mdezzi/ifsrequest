from setuptools import setup, find_packages

setup(
    name="ifsrequest",              
    version="0.2.0",
    packages=find_packages(),
    install_requires=['requests'],  
    author="Matthew Dezzi",
    description="Requests wrapper that will handle IFS token retrieval automatically",
    python_requires=">=3.7",
)