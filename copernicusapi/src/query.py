#!/usr/bin/env python
# coding: utf-8

# # Query
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# This module contains utilities to prepare settings for a valid API query string.

def reduce_wkt_coordinate_precision(wkt_str : str,
                                    decimals : int = 4) -> str:
    """
    Reduces the coordinate precision of a WKT string.
    NOTE: currently only implemented for POINT and POLYGON objects.
    
    Parameters
    ----------
    wkt_str : str
        The original WKT string.
    decimals : int; default=4
        The number of decimals to keep.
        NOTE: decimal places are cut off, not rounded.
    
    Returns
    -------
    str
        The WKT string with reduced coordinate precision.
    """

    if wkt_str.strip().startswith('POLYGON'):
        coords_str = wkt_str.split('((')[-1].replace('))', '')
        coords_str_pairs = coords_str.split(', ')
        coords_pairs = [(float(x.split(' ')[0]), float(x.split(' ')[1])) for x in coords_str_pairs]

        if len(coords_pairs) == 1:
            return f'POINT ({coords_pairs[0][0]:.{decimals}f} {coords_pairs[0][1]:.{decimals}f})'
        else:
            coords_str_clipped = [f'{c[0]:.{decimals}f} {c[1]:.{decimals}f}' for c in coords_pairs]
            return f"POLYGON (({', '.join(coords_str_clipped)}))"
    elif wkt_str.strip().startswith('MULTIPOLYGON'):
        coords_str = wkt_str.split('(((')[-1].replace(')))', '')
        if ')),' in coords_str:
            polygons_str = coords_str.split(')),')
        else:
            polygons_str = [coords_str]
        polygons_str = [p.lstrip('( ').rstrip('), ') for p in polygons_str]
        coords_str_pairs = [p.split(', ') for p in polygons_str]
        coords_pairs = [[(float(x.split(' ')[0]), float(x.split(' ')[1])) for x in p] for p in coords_str_pairs]
        coords_str_clipped = [[f'{c[0]:.{decimals}f} {c[1]:.{decimals}f}' for c in p] for p in coords_pairs]
        polygons = [f"(({', '.join(p)}))" for p in coords_str_clipped]
        return f"MULTIPOLYGON ({', '.join(polygons)})"
    elif wkt_str.strip().startswith('POINT'):
        coords_str = wkt_str.strip().split('(')[-1].replace(')', '')
        coords_str_pair = coords_str.split(' ')
        return f"POINT ({float(coords_str_pair[0]):.{decimals}f} {float(coords_str_pair[1]):.{decimals}f})"


def convert_special_characters(attr : str) -> str:
    """
    Converts special characters in query attributes to ensure compatibility with ODATA API.
    
    Parameters
    ----------
    attr : str
        The attribute.
    
    Returns
    -------
    str
        The attribute with special characters replaced.
    """

    attr = attr.replace("'", "''")
    attr = attr.replace('%', "%25")
    attr = attr.replace('+', "%2B")
    attr = attr.replace('/', "%2F")
    attr = attr.replace('?', "%3F")
    attr = attr.replace('#', "%23")
    attr = attr.replace('&', "%26")

    return attr

