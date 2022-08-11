with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="SESMG",
    version="0.1.1",
    license="MIT",
    author="Christian Klemm",
    author_email="christian.klemm@fh-muenster.de",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9'],
    extras_require={
        "dev":
            ["pytest", "sphinx", "sphinx_rtd_theme"]
    },  
)

