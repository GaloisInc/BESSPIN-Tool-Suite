import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cyberphyslib", # Replace with your own username
    version="0.0.1",
    author=("Ethan Lew", "Michal Podhradsky", "Steven Osborn", "Kristopher Dobelstein"),
    author_email=("elew@galois.com", "mpodhradsky@galois.com ", "steven@lolsborn.com", "kris.dobelstein@agilehardwarenwllc.com"),
    description="BESSPIN Cyberphys Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=['tests*']),
    python_requires=">=3.6",
    include_package_data=True
)