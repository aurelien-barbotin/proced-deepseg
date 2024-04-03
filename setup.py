import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

thelibFolder = os.path.dirname(os.path.realpath(__file__))

requirementPath = thelibFolder + '/lib/requirements.txt'
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
        
setuptools.setup(
    name="proced_deepseg", # Replace with your own username
    version="1",
    author="Aurélien Barbotin",
    description="Collection of scripts to use deep learning models for segmentation and analysis of bacterial images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPL v3.0",
        "Operating System :: OS Independent",
    ],
    py_modules=[],
    python_requires=">=3.8",
    install_requires=install_requires,
)
