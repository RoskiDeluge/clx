from setuptools import setup, find_packages

setup(
    name="clx-cli",
    version="0.6.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        'tomli>=2.0.1; python_version < "3.11"',
    ],
)
