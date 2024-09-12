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
    elif collection_name in ('envisat', ):
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
    elif collection_name in ('ccm', 'copernicuscontributingmissions', 'contributingmissions'):
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
    elif product_type_name in ('slc', 'singlelookcomplex', 'level1slc', 'l1slc'):
        return 'SLC'
    elif product_type_name in ('grd', 'groundrangedetected', 'level1grd', 'l1grd'):
        return 'GRD'
    elif product_type_name in ('grdh', 'groundrangedetectedhighresolution', 'level1grdh', 'l1grdh'):
        return 'GRDH'
    elif product_type_name in ('ocn', 'ocean', 'l2', 'level2'):
        return 'OCN'

    # Sentinel-2
    elif product_type_name in ('l1c', 'level1c', 's2msi1c', 'toa'):
        return 'S2MSI1C'
    elif product_type_name in ('l2a', 'level2a', 's2msi2a', 'boa'):
        return 'S2MSI2A'
    
    # Sentinel-3 OLCI
    elif product_type_name in ('ol1efr', 'efr', 'olciefr'):
        return 'OL_1_EFR___'
    elif product_type_name in ('ol1err', 'err', 'olcierr'):
        return 'OL_1_ERR___'
    elif product_type_name in ('ol2wfr', 'wfr', 'olciwfr'):
        return 'OL_2_WFR___'
    elif product_type_name in ('ol2wrr', 'wrr', 'olciwrr'):
        return 'OL_2_WRR___'
    elif product_type_name in ('ol2lfr', 'lfr', 'olcilfr'):
        return 'OL_2_LFR___'
    elif product_type_name in ('ol2lrr', 'lrr', 'olcilrr'):
        return 'OL_2_LRR___'
    
    # Sentinel-3 SLSTR
    elif product_type_name in ('sl1rbt', 'rbt', 'slstrrbt'):
        return 'SL_1_RBT___'
    elif product_type_name in ('sl2lst', 'lst', 'slstrlst'):
        return 'SL_2_LST___'
    elif product_type_name in ('sl2wst', 'wst', 'slstrwst'):
        return 'SL_2_WST___'
    elif product_type_name in ('sl2frp', 'frp', 'slstrfrp'):
        return 'SL_2_FRP___'
    
    # Sentinel-3 SRAL (Altimetry)
    elif product_type_name in ('sr1sraa', 'sraa', 'sralsraa', 'l1a', 'level1a'):
        return 'SR_1_SRA_A_'
    elif product_type_name in ('sr1sra', 'sra', 'sralsra', 'l1b', 'level1b'):
        return 'SR_1_SRA___'
    elif product_type_name in ('sr1srabs', 'srabs', 'sralsrabs', 'l1bs', 'level1bs'):
        return 'SR_1_SRA_BS'
    elif product_type_name in ('sr2lan', 'lan', 'srallan', 'land'):
        return 'SR_2_LAN___'
    elif product_type_name in ('sr2lanhy', 'lanhy', 'srallanhy', 'hydrology'):
        return 'SR_2_LAN_HY'
    elif product_type_name in ('sr2lansi', 'lansi', 'srallansi', 'seaice'):
        return 'SR_2_LAN_SI'
    elif product_type_name in ('sr2lanli', 'lanli', 'srallanli', 'landice'):
        return 'SR_2_LAN_LI'
    elif product_type_name in ('sr2wat', 'wat', 'sralwat', 'water'):
        return 'SR_2_WAT___'

    # Sentinel-3 Synergy
    elif product_type_name in ('sy2syn', 'syn', 'synergy'):
        return 'SY_2_SYN___'
    elif product_type_name in ('sy2vgp', 'vgp', 'vegetationp'):
        return 'SY_2_VGP___'
    elif product_type_name in ('sy2vg1', 'vg1', 'vegetations1'):
        return 'SY_2_VG1___'
    elif product_type_name in ('sy2v10', 'vg10', 'v10', 'vegetations10'):
        return 'SY_2_V10___'
    elif product_type_name in ('aod', 'aerosol', 'aerosolopticaldepth', 'opticaldepth', 'sy2aod'):
        return 'SY_2_AOD___'
    
    # Sentinel-5p
    elif product_type_name.startswith(('l1bra', 'ra')):
        band_id = product_type_name[-1]
        return f'L1B_RA_BD{band_id}'
    elif product_type_name in ('l1birsir', 'irsir'):
        return 'L1B_IR_SIR'
    elif product_type_name in ('l1biruvn', 'iruvn'):
        return 'L1B_IR_UVN'
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
    
    # Sentinel-6
    elif product_type_name in ('s6mw2amr', 'mw2amr'):
        return 'MW_2__AMR____'
    elif product_type_name in ('s6p41blr', 'p41blr'):
        return 'P4_1B_LR_____'
    elif product_type_name in ('s6p41bhr', 'p41bhr'):
        return 'P4_1B_HR_____'
    elif product_type_name in ('s6p42lr', 'p42lr'):
        return 'P4_2__LR_____'
    elif product_type_name in ('s6p42hr', 'p42hr'):
        return 'P4_2__HR_____'
    
    # Sentinel-1 RTC
    elif product_type_name in ('rtc', 'radiometricterraincorrected'):
        return 'RTC'
    
    # Global Mosaics
    elif product_type_name in ('s2msil3mcq', 's2quarterly', 's2quarterlymosaic'):
        return 'S2MSI_L3__MCQ'
    elif product_type_name in ('s1sarl3iwmcm', 's1iwmonthly', 's1iwmonthlymosaic'):
        return 'S1SAR_L3_IW_MCM'
    elif product_type_name in ('s1sarl3dhmcm', 's1dhmonthly', 's1dhmonthlymosaic'):
        return 'S1SAR_L3_DH_MCM'

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
    elif product_type_name in ('l1tp', 'level1tp', 'precisionterrain', 'precisionterraincorrected'):
        return 'L1TP'
    elif product_type_name in ('l2sp', 'level2sp', 'surfacereflectance', 'sr'):
        return 'L2SP'
    
    else:
        return None

