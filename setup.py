from setuptools import setup, find_packages

setup(
    name="hexpect",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "nibabel==5.3.2",
        "numpy==2.3.2",
        "packaging==25.0",
        "setuptools==80.10.2"
    ]
)