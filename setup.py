import setuptools
from pathlib import Path

README = (Path(__file__).parent / "README.md").read_text()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fusion_addin_framework",
    version="0.0.1",
    description="A framewotk to simplify the creation of Addins for Fusion360",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m0dd0/fusion_addin_framework",
    author="Moritz Hesche",
    author_email="mo.hesche@gmail.com",
    licence="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_package_data=True,
    install_requires=[],
)