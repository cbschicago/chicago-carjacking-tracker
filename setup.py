from setuptools import setup

setup(
    name="crime-tracker",
    package_dir={"": "src"},
    install_requires=[
        "csvkit==1.0.6",
        "pandas==1.3.1",
        "geopandas==0.9.0",
        "Rtree==0.9.7",
    ],
)
