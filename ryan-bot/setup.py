from setuptools import setup, find_packages

setup(
    name="ryan_bot",
    version="0.1",
    packages=find_packages(),
    package_dir={
        "": "."
    },
    install_requires=[
        "nemoguardrails",
        "transformers",
        "torch",
        "peft",
        "ruamel.yaml"
    ],
)