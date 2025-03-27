from setuptools import setup, find_packages

setup(
    name='s2reader',
    version='0.1',
    packages=find_packages(),  # Automatically finds and includes all packages in the project
    install_requires=[
        'geopandas==1.0.1',
        'numpy==2.0.0',
        'pandas==2.2.2',
        'rasterio==1.3.10',
        'rioxarray==0.16.0',
        'xarray==2024.6.0',
        'scipy==1.14.0',
    ],
    python_requires='==3.11.9',  # Specify the minimum Python version
    #entry_points={},
)