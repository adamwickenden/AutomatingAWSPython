# run: python setup.py bdist_wheel to package into a distributable module

from setuptools import setup

setup(
    name="Webotron",
    version="1.0",
    author="Adam Wickenden",
    author_email="adam@wickenden.com",
    description="Automation of bucket/static site creation",
    license="GPLv3+",
    packages=["webotron"],
    url="https://github.com/adamwickenden/AutomatingAWSPython",
    install_requires=["click", "boto3"],
    entry_points="""
        [console_scripts]
        webotron=webotron.webotron:cli
    """,
)
