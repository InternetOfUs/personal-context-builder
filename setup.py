import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    all_lines = f.read().split("\n")
    requirements = [line for line in all_lines if "@" not in line]
    requirements_git = [
        line.replace("-e", line.split("=")[-1] + " @")
        for line in all_lines
        if "@" in line
    ]
    requirements += requirements_git

setuptools.setup(
    name="personal_context_builder",
    version="2.0.0",
    license="Apache-2.0",
    author="Idiap - William Droz",
    author_email="william.droz@idiap.ch",
    description="Personal Context Builder for the Wenet project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=requirements,
)
