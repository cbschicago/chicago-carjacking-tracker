from setuptools import setup

setup(
    name="gh_workflow",
    package_dir={"": "src"},
    install_requires=[
        "csvkit==1.0.6",
        "pandas==1.3.1",
        "geopandas==0.9.0",
        "Rtree==0.9.7",
        "datawrapper==0.4.6",
        "matplotlib==3.4.3",
        "matplotlib-inline==0.1.2",
    ],
)
