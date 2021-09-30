from setuptools import setup

setup(
    name="gh_workflow",
    package_dir={"": "src"},
    install_requires=[
        "csvkit==1.0.6",
        "datawrapper==0.4.6",
        "folium==0.12.1",
        "geopandas==0.9.0",
        "matplotlib==3.4.3",
        "matplotlib-inline==0.1.2",
        "openpyxl==3.0.7",
        "pandas==1.3.1",
        "pysftp==0.2.9",
        "Rtree==0.9.7",
        "tabulate==0.8.9",
        "XlsxWriter==3.0.1",
    ],
)
