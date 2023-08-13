from setuptools import setup, find_packages

setup(
    name="cbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
        "pyperclip",
        "langchain",
    ],
    entry_points={
        "console_scripts": [
            "cbot = cbot.__main__:main",
        ],
    },
)
