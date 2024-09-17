from setuptools import find_packages, setup

# load README.md as long description for PyPI
with open('README.md', 'r') as f:
    long_description = f.read()

# run setup
setup(name='copernicusapi',
      version='0.1.1',
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
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Topic :: Scientific/Engineering :: GIS',
          'Topic :: Utilities'
      ],
      keywords='copernicus, data space, esa, satellite, download, remote sensing, earth observation',
      install_requires=['geopandas>=0.14',
                        'numpy>=1.26',
                        'pandas>=2.0',
                        'pyproj>=3.6',
                        'shapely>=2.0',
                        ],
      extras_require={
          'dev': ['black>=24.0',
                  'flake>=7.0',
                  'pytest-cov>=4.1',
                  'twine>=5.1',
                  'pytest>=8.0']
                  },
      python_requires='>=3.10'
      )