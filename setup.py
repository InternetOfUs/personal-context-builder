import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().split("\n")

setuptools.setup(
    name="personal_context_builder",
    version="0.0.6",
    author="Idiap - William Droz",
    author_email="william.droz@idiap.ch",
    description="Personal Context Builder for the Wenet project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=requirements,
)
