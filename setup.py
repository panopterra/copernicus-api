from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='copernicusapi',
      version='0.0.1',
      description='A package to facilitate interactive construction of queries to the Copernicus Data Space Ecosystem repository.',
      package_dir={'copernicusapi': 'copernicusapi'},
      packages=find_packages(),
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/panopterra/copernicus-api',
      author='Panopterra UG',
      author_email='contact@panopterra.com',
      license='Apache 2.0',
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent',
      ],
      keywords='copernicus, data space, esa, satellite, download, remote sensing, earth observation',
      install_requires=['shapely>=2.0',
                        'numpy>=1.26',
                        'pandas>=2.0',
                        'geopandas>=0.14',
                        'pyproj>=3.6'],
      extras_require={
          'dev': ['pytest>=8.0', 'twine>=5.1']
      },
      python_requires='>=3.10'
      )