from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="human-autoclicker",
    version="0.1.1",
    author="Will Bosch-Bello",
    author_email="williamsbosch@gmail.com",
    description="A simple auto clicker with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/will-abb/click-bot",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyautogui",
        "pynput",
        "tkhtmlview",
        "markdown",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "human-autoclicker=human_autoclicker.human_autoclicker_gui:main",
        ],
    },
)
