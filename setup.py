from setuptools import setup, find_packages

version = "0.1.3.1"

setup(
    name="alphaz-next",
    version=version,
    packages=find_packages("alphaz_next"),
    install_requires=[
        "sqlalchemy",
        "httpx",
        "python-jose",
        "dependency-injector",
        "python-multipart",
        "fastapi==0.100.0",
        "pydantic_settings",
        "pydantic==2.3",
        "sqlalchemy == 1.4.41",
        "sqlalchemy_utils",
        "pytz",
        "email-validator",
    ],
    license="MIT",
    author="Maxime MARTIN",
    author_email="maxime.martin02@hotmail.fr",
    description="A project to make a lib to start FASTAPI quickly",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/STDef200mm/alphaz-next",
    download_url="https://github.com/STDef200mm/alphaz-next/archive/refs/tags/%s.tar.gz"
    % version,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
