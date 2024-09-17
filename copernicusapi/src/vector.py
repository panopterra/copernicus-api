#!/usr/bin/env python
# coding: utf-8

# # Vector
# 
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# This file is part of the copernicusapi package and the copernicus-api repository
# (https://github.com/panopterra/copernicus-api). It is released under the Apache
# License Version 2.0. See the README.md file in the repository root directory or
# go to http://www.apache.org/licenses/ for full license details.
# 
# ---
# 
# This module contains utilities for operations on vector geometries.
# 
# ---

import pyproj
import shapely
from shapely.ops import transform


def reproject_geometry(geom : shapely.geometry, 
                       source_epsg : int, 
                       target_epsg : int) -> shapely.geometry:
    """
    Projects a given vector geometry object from one CRS to another.
    
    Parameters
    ----------
    geom : shapely.geometry object
        The geometry to reproject.
    source_epsg : int
        The EPSG of the source projection of the geometry.
    target_proj : str or int or float or pyproj.CRS
        The EPSG of the target projection of the geometry.

    Returns
    -------
    shapely.geometry object
        Projected version of geometry.
    """

    # skip process if source and target CRS are identical
    if source_epsg == target_epsg:
        return geom

    project = pyproj.Transformer.from_crs(source_epsg, target_epsg, always_xy=True).transform
    reprojected_geom = transform(project, geom)
    return reprojected_geom

