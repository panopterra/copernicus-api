#!/usr/bin/env python
# coding: utf-8

# # Response
# 
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# This module contains utilities that help interpret the API response and extract
# additional information.

import numpy as np


def get_checksums(checksum_entry : list[dict]) -> tuple[str,str]:
    """
    Retrieves all available checksums from entry.
    NOTE: intended for use in pandas/geopandas .apply().
    
    Parameters
    ----------
    checksum_entry : list of dict
        The content of the 'Checksum' entry for a product.
    
    Returns
    -------
    str
        The MD5 checksum. If not available, returns None.
    str
        The BLAKE3 checksum. If not available, returns None.
    """

    if len(checksum_entry) > 0:
        if len(checksum_entry[0]) > 0:
            if 'MD5' in [item['Algorithm'].upper() for item in checksum_entry]:
                checksum_md5 = [item for item in checksum_entry if item['Algorithm'].upper() == 'MD5'][0]['Value']
            else:
                checksum_md5 = None
            if 'BLAKE3' in [item['Algorithm'].upper() for item in checksum_entry]:
                checksum_blake3 = [item for item in checksum_entry if item['Algorithm'].upper() == 'BLAKE3'][0]['Value']
            else:
                checksum_blake3 = None
            return checksum_md5, checksum_blake3
        else:
            return None, None
    else: return None, None


def get_cloud_cover(attributes : list[dict]) -> float:
    """
    Retrieves the cloud cover from attributes list of a product.
    NOTE: intended for use in pandas/geopandas .apply().
    
    Parameters
    ----------
    attributes : list of dict
        The attributes list as obtained from API result (from the 'Attributes' entry).
    
    Returns
    -------
    float
        The cloud cover percentage. Returns np.nan if no 'cloudCover' attribute was found.
    """

    if len(attributes) == 0:
        return np.nan
    else:
        for item in attributes:
            if 'Name' in item.keys():
                if item['Name'] == 'cloudCover':
                    return float(item['Value'])
        return np.nan


def get_product_type(attributes : list[dict]) -> float:
    """
    Retrieves the product type from attributes list of a product.
    NOTE: intended for use in pandas/geopandas .apply().
    
    Parameters
    ----------
    attributes : list of dict
        The attributes list as obtained from API result (from the 'Attributes' entry).
    
    Returns
    -------
    float
        The product type. Returns np.nan if no 'productType' attribute was found.
    """

    if len(attributes) == 0:
        return np.nan
    else:
        for item in attributes:
            if 'Name' in item.keys():
                if item['Name'] == 'productType':
                    return str(item['Value'])
        return np.nan


def determine_group_tile_identifier(name : str) -> str:
    """
    Retrieves the unique group/tile identification information from a product name.
    NOTE: intended for use in pandas/geopandas .apply().
    
    Parameters
    ----------
    name : str
        The full product name (from the 'Name' entry).
    
    Returns
    -------
    str
        The unique group tile identifier.

    Notes
    -----
    Currently only implemented for Sentinel-1, Sentinel-2, Sentinel-3 and Sentinel-5p
    products.
    """

    name_parts = [p for p in name.split('_') if len(p) > 0]
    name_parts = name.split('_')
    if name.startswith('S1'):
        if len(name_parts) > 7:
            return name_parts[7]
        else:
            return name_parts[-1]
    elif name.startswith('S2'):
        return '_'.join(name_parts[4:6])
    elif name.startswith('S3'):
        if '_SY_' in name:
            return '-'
        else:
            return '_'.join(name_parts[10:12])
    elif name.startswith('S5'):
        return name_parts[-4]

