from setuptools import setup, find_packages

if __name__ == "__main__":
    version = "0.0.1"

    with open("README.md", "r") as readme_file:
        long_description = readme_file.read()

    setup(
        name="jdoc",
        version=version,
        description="Automatically generate documentation from Python docstrings",
        url="https://github.com/jonathangjertsen/jdoc",
        author="Jonathan Reichelt Gjertsen",
        author_email="jonath.re@gmail.com",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=find_packages(exclude=["test", "test.*", "*.test.*", "*.test"]),
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: Implementation :: CPython",
        ],
        license="MIT",
        zip_safe=False,
        project_urls={
            "Documentation": "https://github.com/jonathangjertsen/jdoc",
            "Source": "https://github.com/jonathangjertsen/jdoc",
        },
    )
