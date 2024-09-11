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


def interpret_collection_name(collection_name : str) -> str:
    """
    Interprets collection name and translates different aliases to standard names
    for queries.
    
    Parameters
    ----------
    collection_name : str
        Collection name or alias.
    
    Returns
    -------
    str
        Standard collection name for use in query.
    """

    collection_name = collection_name.lower().replace('-', '').replace('_', '').replace(' ', '')

    if collection_name in ('sentinel1', 's1'):
        return 'SENTINEL-1'
    elif collection_name in ('sentinel2', 's2'):
        return 'SENTINEL-2'
    elif collection_name in ('sentinel3', 's3'):
        return 'SENTINEL-3'
    elif collection_name in ('sentinel5p', 's5p'):
        return 'SENTINEL-5P'
    elif collection_name in ('sentinel6', 's6'):
        return 'SENTINEL-6'
    elif collection_name in ('sentinel1rtc', 's1rtc'):
        return 'SENTINEL-1-RTC'
    elif collection_name in ('globalmosaics',):
        return 'GLOBAL-MOSAICS'
    elif collection_name in ('smos',):
        return 'SMOS'
    elif collection_name in ('envisat', 'meris'):
        return 'ENVISAT'
    elif collection_name in ('landsat5', 'l5', 'ls5'):
        return 'LANDSAT-5'
    elif collection_name in ('landsat7', 'l7', 'ls7'):
        return 'LANDSAT-7'
    elif collection_name in ('landsat8', 'l8', 'ls8'):
        return 'LANDSAT-8'
    elif collection_name in ('copdem', 'copernicusdem'):
        return 'COP-DEM'
    elif collection_name in ('terraaqua', 'terra', 'aqua', 'modis'):
        return 'TERRAAQUA'
    elif collection_name in ('s2glc', 'globallandcover', 'glc'):
        return 'S2GLC'
    elif collection_name in ('ccm', 'copernicuscontributingmissions'):
        return 'CCM'
    else:
        return None


def interpret_product_type(product_type_name : str) -> str:
    """
    Interprets product types and translates different aliases to standard names
    for queries.
    
    Parameters
    ----------
    product_type_name : str
        Collection name or alias.
    
    Returns
    -------
    str
        Standard product type name for use in query.
    """

    product_type_name = product_type_name.lower().replace('-', '').replace('_', '').replace(' ', '')

    # Sentinel-1
    if product_type_name in ('cardbs', 'cardbackscatter', 'backscatter'):
        return 'CARD-BS'
    elif product_type_name in ('cardcoh6', 'cardcoh', 'cardcoherence6', 'cardcoherence', 'coherence6', 'coherence'):
        return 'CARD-COH6'
    elif product_type_name in ('raw', 'l0', 'level0'):
        return 'RAW'
    elif product_type_name in ('slc', 'singlelookcomplex', 'level1slc'):
        return 'SLC'
    elif product_type_name in ('grd', 'groundrangedetected', 'level1grd'):
        return 'GRD'
    elif product_type_name in ('ocn', 'ocean', 'l2', 'level2'):
        return 'OCN'

    # Sentinel-2
    elif product_type_name in ('l1c', 'level1c', 's2msi1c', 'toa'):
        return 'S2MSI1C'
    elif product_type_name in ('l2a', 'level2a', 's2msi2a', 'boa'):
        return 'S2MSI2A'
    
    # Sentinel-3 OLCI
    elif product_type_name in ('ol1efr', 'efr', 'olciefr'):
        return 'EFR'
    elif product_type_name in ('ol1err', 'err', 'olcierr'):
        return 'ERR'
    elif product_type_name in ('ol2wfr', 'wfr', 'olciwfr'):
        return 'WFR'
    elif product_type_name in ('ol2wrr', 'wrr', 'olciwrr'):
        return 'WRR'
    elif product_type_name in ('ol2lfr', 'lfr', 'olcilfr'):
        return 'LFR'
    elif product_type_name in ('ol2lrr', 'lrr', 'olcilrr'):
        return 'LRR'
    
    # Sentinel-3 SLSTR
    elif product_type_name in ('sl1rbt', 'rbt', 'slstrrbt'):
        return 'RBT'
    elif product_type_name in ('sl2lst', 'lst', 'slstrlst'):
        return 'LST'
    elif product_type_name in ('sl2wst', 'wst', 'slstrwst'):
        return 'WST'
    elif product_type_name in ('sl2wct', 'wct', 'slstrwct'):
        return 'WCT'
    elif product_type_name in ('sl2frp', 'frp', 'slstrfrp'):
        return 'FRP'
    
    # Sentinel-3 SRAL (Altimetry)
    elif product_type_name in ('sr1sra', 'sra', 'sralsra'):
        return 'SRA'
    elif product_type_name in ('sr1sraa', 'sraa', 'sralsraa'):
        return 'SRA_A'
    elif product_type_name in ('sr1srabs', 'srabs', 'sralsrabs'):
        return 'SRA_BS'
    elif product_type_name in ('lan', 'srallan'):
        return 'LAN'
    elif product_type_name in ('lanhy', 'srallanhy'):
        return 'LAN_HY'
    elif product_type_name in ('lansi', 'srallansi'):
        return 'LAN_SI'
    elif product_type_name in ('lanli', 'srallanli'):
        return 'LAN_LI'
    elif product_type_name in ('wat', 'sralwat'):
        return 'WAT'

    # Sentinel-3 Synergy
    elif product_type_name in ('syn', 'synergy'):
        return 'SYN'
    elif product_type_name in ('vgp', 'vegetationp'):
        return 'VGP'
    elif product_type_name in ('vg1', 'vegetations1'):
        return 'VG1'
    elif product_type_name in ('vg10', 'v10', 'vegetations10'):
        return 'VG10'
    elif product_type_name in ('aod', 'aerosol', 'aerosolopticaldepth', 'opticaldepth'):
        return 'AOD'
    
    # Sentinel-5p
    elif product_type_name.startswith(('l1bra', 'ra')):
        band_id = product_type_name[-1]
        return f'L1B_RA_BD{band_id}'
    elif product_type_name in ('l1birsir', 'irsir'):
        return 'IR_SIR'
    elif product_type_name in ('l1biruvn', 'iruvn'):
        return 'IR_UVN'
    elif product_type_name in ('l2o3', 'o3'):
        return 'L2__O3____'
    elif product_type_name in ('l2o3tcl', 'o3tcl'):
        return 'L2__O3_TCL'
    elif product_type_name in ('l2o3pr', 'o3pr'):
        return 'L2__O3__PR'
    elif product_type_name in ('l2no2', 'no2'):
        return 'L2__NO2___'
    elif product_type_name in ('l2so2', 'so2'):
        return 'L2__SO2___'
    elif product_type_name in ('l2ch4', 'ch4'):
        return 'L2__CH4___'
    elif product_type_name in ('l2hcho', 'hcho'):
        return 'L2__HCHO__'
    elif product_type_name in ('l2cloud', 'cloud'):
        return 'L2__CLOUD_'
    elif product_type_name in ('l2aerai', 'aerai'):
        return 'L2__AER_AI'
    elif product_type_name in ('l2aerlh', 'aerlh'):
        return 'L2__AER_LH'
    
    # Landsat-5
    elif product_type_name in ('l1g', 'level1g', 'ground', 'georeferenced'):
        return 'L1G'
    elif product_type_name in ('l1t', 'level1t', 'terrain', 'terraincorrected'):
        return 'L1T'
    
    # Landsat-7
    elif product_type_name in ('l1gt', 'level1gt', 'geocorrectedterrain', 'geocorrectedterraincorrected'):
        return 'L1GT'
    elif product_type_name in ('gtc1p', 'globallandsurvey', 'panchromatic', 'globallandsurveypanchromatic'):
        return 'GTC_1P'
    
    # Landsat-8
    elif product_type_name in ('l1tp', 'level1tp', 'terrainp', 'terraincorrectedp'):
        return 'L1TP'
    elif product_type_name in ('l2sp', 'level2sp', 'surfacereflectance', 'sr'):
        return 'L2SP'
    
    else:
        return None

