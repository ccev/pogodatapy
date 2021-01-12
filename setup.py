from setuptools import setup

version = "0.0.2"

setup(
    name="pogodata",
    author="ccev",
    url="https://github.com/ccev/pogodata",
    version=version,
    install_requires=["requests"],
    packages=["pogodata", "pogodata.pogoinfo"],
    long_description="For documentation, plase visit https://github.com/ccev/pogodata",
    description="Easy and up-to-date Pogo Data"
)