from setuptools import setup

version = "0.5.14"

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()


EXTRAS_REQUIRE = {
    "dependency-injector": ["dependency-injector"],
}

setup(
    name="alphaz-next",
    version=version,
    packages=[
        "alphaz_next",
        "alphaz_next.asyncio",
        "alphaz_next.auth",
        "alphaz_next.core",
        "alphaz_next.core.responses",
        "alphaz_next.libs",
        "alphaz_next.models",
        "alphaz_next.models.auth",
        "alphaz_next.models.config",
        "alphaz_next.models.config._base",
        "alphaz_next.tests",
        "alphaz_next.tests.utils",
        "alphaz_next.tests.utils.mocking",
        "alphaz_next.utils",
    ],
    install_requires=required_packages,
    extras_require=EXTRAS_REQUIRE,
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
