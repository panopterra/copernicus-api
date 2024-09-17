#!/usr/bin/env python
# coding: utf-8

# # Copernicus Query and Download Test
# 
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# This file is part of the copernicusapi package and the copernicus-api repository
# (https://github.com/panopterra/copernicus-api). It is released under the Apache
# License Version 2.0. See the README.md file in the repository root directory or
# go to http://www.apache.org/licenses/ for full license details.
# 
# ---

# #### Load packages and modules

import os
import pytest


# ### Import packages and modules for unit testing

from datetime import datetime

import geopandas as gpd
import numpy as np

from copernicusapi.src.query_constructor import QueryConstructor


# ### Setting up packages and modules (optional)

# ---
# ## Unit test preparation

# ### Helper functions

def configure_query_constructor(query_constructor, settings_dict):
    """
    Configures a QueryConstructor instance based on provided settings.
    """

    for key, value in settings_dict.items():
        if key == 'collection':
            query_constructor.add_collection_filter(value)
        elif key == 'publication_date':
            query_constructor.add_publication_date_filter(*value)
        elif key == 'sensing_start_date':
            query_constructor.add_sensing_start_date_filter(*value)
        elif key == 'sensing_end_date':
            query_constructor.add_sensing_end_date_filter(*value)
        elif key == 'aoi':
            query_constructor.add_aoi_filter(value)
        elif key == 'cloud_cover':
            query_constructor.add_cloud_cover_filter(value)
        elif key == 'product_type':
            query_constructor.add_product_type_filter(value)
        elif key == 'attribute':
            for item in value:
                query_constructor.add_attribute_filter(**item)
    
    return query_constructor


# ### Test cases

@pytest.fixture
def create_query_constructor_test_case(test_resources_dir):
    """
    Creates test cases for use in QueryConstructor tests.
    """

    def _test_case(test_case):
        if test_case == 'test_case1':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi1_point.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                     'collection': 'sentinel-2',
                                     'product_type': 'l2a',
                                     'sensing_start_date': (datetime(2023, 7, 5), '2023-10-28T19:33:12.021Z'),
                                     'cloud_cover': 35
                                    }
            test_case['n_products'] = 9
            test_case['aoi_coverage'] = 1.0
            test_case['nans'] = 0.04
        elif test_case == 'test_case2':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi1_point.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                     'collection': 's2',
                                     'product_type': 'level1c',
                                     'sensing_end_date': ('2020-05-01T03:24:33.998Z', '2020-08-11T22:00:11.633Z'),
                                     'cloud_cover': (10, 22),
                                    }
            test_case['n_products'] = 4
            test_case['aoi_coverage'] = 1.0
            test_case['nans'] = 0.07
        elif test_case == 'test_case3':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi2_polygon.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                    'collection': 's1',
                                    'product_type': 'grd',
                                    'sensing_end_date': (datetime(2016, 9, 28), datetime(2016, 10, 23, 21, 31, 22)),
                                    'attribute': [{'name': 'orbitDirection', 'operator': 'eq', 'value': 'ASCENDING', 'attribute_type': 'String'}]
                                    }
            test_case['n_products'] = 7
            test_case['aoi_coverage'] = 0.999
            test_case['nans'] = 0.04
        elif test_case == 'test_case4':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi3_self_intersecting_polygon.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                     'collection': 'sentinel-1',
                                     'product_type': 'slc',
                                     'sensing_end_date': (datetime(2018, 8, 7, 0, 52, 11), datetime(2018, 8, 12)),
                                     'attribute': [{'name': 'polarisationChannels', 'operator': 'eq', 'value': 'VV&VH', 'attribute_type': 'String'}]
                                    }
            test_case['n_products'] = 5
            test_case['aoi_coverage'] = 0.467
            test_case['nans'] = 0.04
        elif test_case == 'test_case5':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi4_multipolygon1.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                    'collection': 'sentinel-3',
                                    'product_type': 'OL_2 lfr',
                                    'sensing_end_date': (datetime(2018, 8, 22, 0, 3, 56), datetime(2018, 9, 2, 23, 59, 59)),
                                    'attribute': [{'name': 'orbitDirection', 'operator': 'eq', 'value': 'DESCENDING', 'attribute_type': 'String'},
                                                {'name': 'processingLevel', 'operator': 'eq', 'value': '2', 'attribute_type': 'String'}
                                                ]
                                    }
            test_case['n_products'] = 20
            test_case['aoi_coverage'] = 1.0
            test_case['nans'] = 0.1
        elif test_case == 'test_case6':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi5_multipolygon2.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                    'collection': 'sentinel-5p',
                                    'product_type': 'L2CH4',
                                    'sensing_end_date': (datetime(2021, 12, 15), datetime(2022, 1, 5, 23, 59, 59)),
                                    }
            test_case['n_products'] = 44
            test_case['aoi_coverage'] = 1.0
            test_case['nans'] = 0.08
        elif test_case == 'test_case7':
            test_case = {}
            gdf = gpd.read_file(os.path.join(test_resources_dir, 'aoi1_point.geojson'))
            test_case['settings'] = {'aoi': gdf['geometry'].values.tolist()[0],
                                    'collection': 'l8',
                                    'product_type': 'L1 GT',
                                    'sensing_end_date': ('2015-05-05T19:33:12.021Z', datetime(2015, 6, 28)),
                                    }
            test_case['n_products'] = 6
            test_case['aoi_coverage'] = 1.0
            test_case['nans'] = 0.13
        elif test_case == 'test_case8':
            test_case = {}
            test_case['settings'] = {'product_names': ['S2B_MSIL1C_20230101T102339_N0509_R065_T32UNU_20230101T105601.SAFE',
                                                       'S1A_IW_GRDH_1SDV_20240208T053520_20240208T053545_052463_065842_F89D.SAFE',
                                                       'S1A_IW_GRDH_1SDV_20240208T053520_20240208T053545_052463_065842_F89D-.SAFE', # deliberately wrong name
                                                       'S3A_OL_2_WFR____20190228T092807_20190228T093107_20190301T190540_0179_042_036_2160_MAR_O_NT_002.SEN3']
                                    }
            test_case['n_products'] = 3
            test_case['aoi_coverage'] = 0.
            test_case['nans'] = 0.05

        return test_case
    
    return _test_case


# ---
# ## Unit test definition

# ### QueryConstructor

@pytest.mark.timeout(300)
@pytest.mark.integration_test
@pytest.mark.parametrize("test_case", ['test_case1',
                                       'test_case2',
                                       'test_case3',
                                       'test_case4',
                                       'test_case5',
                                       'test_case6',
                                       'test_case7',
                                       'test_case8',
                                       ])
def test_query_constructor(test_case, create_query_constructor_test_case):
    """
    Tests the QueryConstructor class.
    """

    test_case = create_query_constructor_test_case(test_case)
    
    qc = QueryConstructor()
    # special handling of query_by_name
    if 'product_names' in test_case['settings'].keys():
        products, _ = qc.query_by_name(test_case['settings']['product_names'])
    else:
        qc = configure_query_constructor(qc, test_case['settings'])
        products, _ = qc.send_query()
    assert len(products) == test_case['n_products']
    assert qc.aoi_coverage >= test_case['aoi_coverage']

    # check that products dataframe does not contain a large number of NaNs (may
    # indicate problems with extracting additional columns)
    assert float(np.sum(products.isna().values) / products.values.size) <= test_case['nans']

    # verify that products property is the same as what is returned
    products2 = qc.products
    products[products.isna()] = 0.
    products = products.sort_values('Name').reset_index(drop=True)
    products2[products2.isna()] = 0.
    products2 = products2.sort_values('Name').reset_index(drop=True)
    assert np.sum((products == products2).values) == products.values.size

