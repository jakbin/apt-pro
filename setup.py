import setuptools
from apt_pro import __version__

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="apt-pro",
    version=__version__,
    author="Jak Bin",
    description="A python package for better update and manage your debian packages.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/jakbin/apt-pro",
    project_urls={
        "Bug Tracker": "https://github.com/jakbin/apt-pro/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='python-apt,apt,package-manager,debian,apt-pro',
    python_requires=">=3.6",
    install_requires=['rich'],
    packages=["apt_pro"],
    package_data={
        "apt_pro":[
            "apt-pro.db"
        ]
    },
    entry_points={
        "console_scripts":[
            "apt-pro = apt_pro:cli.main"
        ]
    }
)
