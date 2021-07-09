import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jk",
    version="1.0.0",
    author="Jak Bin",
    description="A python package for better update and manage your debian packages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jakbin/jk",
    project_urls={
        "Bug Tracker": "https://github.com/jakbin/jk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #packages=setuptools.find_packages(),
    python_requires=">=3.6",
    
    install_requires=['rich==10.3.0'],
    
    packages=["jk"],
    
    package_data={
        "jk":[
            "a.txt"
        ]
    },
    
    entry_points={
        "console_scripts":[
            "jk = jk:main"
        ]
    }
)
