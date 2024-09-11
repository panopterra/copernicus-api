#!/usr/bin/env python
# coding: utf-8

# # Query Test
# 
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# ---

# #### Load packages and modules




# ### Import packages and modules for unit testing

from copernicusapi.src.query import interpret_collection_name, interpret_product_type


# ### Setting up packages and modules (optional)

# ---
# ## Unit test preparation

# ### Test cases

PRODUCT_TYPE_TEST_CASES = {
                            # Sentinel-1 
                            'backscatter': 'CARD-BS',
                            'CardBS': 'CARD-BS',
                            'Cardcoh': 'CARD-COH6',
                            'Coherence': 'CARD-COH6',
                            'raw': 'RAW',
                            'level0': 'RAW',
                            'slc': 'SLC',
                            'Single Look Complex': 'SLC',
                            'grd': 'GRD',
                            'Ground Range Detected': 'GRD',
                            'ocn': 'OCN',
                            'Ocean': 'OCN',

                            # Sentinel-2
                            'l1c': 'S2MSI1C',
                            'level1c': 'S2MSI1C',
                            'toa': 'S2MSI1C',
                            'l2a': 'S2MSI2A',
                            'level2a': 'S2MSI2A',
                            'boa': 'S2MSI2A',

                            # Sentinel-3 OLCI
                            'ol1efr': 'EFR',
                            'err': 'ERR',
                            'ol2-wfr': 'WFR',
                            'OLCIwrr': 'WRR',
                            'olci LFR': 'LFR',
                            'lrr': 'LRR',

                            # Sentinel-3 SLSTR
                            'rbt': 'RBT',
                            'sl2lst': 'LST',
                            'slstrwst': 'WST',
                            'wct': 'WCT',
                            'sl2frp': 'FRP',

                            # Sentinel-3 SRAL
                            'sr1sra': 'SRA',
                            'sraa': 'SRA_A',
                            'SRALsrabs': 'SRA_BS',
                            'lan': 'LAN',
                            'LAN-HY': 'LAN_HY',
                            'LAN SI': 'LAN_SI',
                            'SRAL LAN LI': 'LAN_LI',
                            'wat': 'WAT',

                            # Sentinel-3 Synergy
                            'Synergy': 'SYN',
                            'Vegetationp': 'VGP',
                            'vG1': 'VG1',
                            'Vegetation S10': 'VG10',
                            'Aerosol Optical Depth': 'AOD',

                            # Sentinel-5p
                            'l1bra1': 'L1B_RA_BD1',
                            'RA3': 'L1B_RA_BD3',
                            'L1B RA5': 'L1B_RA_BD5',
                            'IR SIR': 'IR_SIR',
                            'L1B IRUVN': 'IR_UVN',
                            'L2 O3': 'L2__O3____',
                            'O3 TCL': 'L2__O3_TCL',
                            'O3pr': 'L2__O3__PR',
                            'NO2': 'L2__NO2___',
                            'so2': 'L2__SO2___',
                            'l2 CH4': 'L2__CH4___',
                            'HCHo': 'L2__HCHO__',
                            'L2cloud': 'L2__CLOUD_',
                            'L2 AER AI': 'L2__AER_AI',
                            'aer Lh': 'L2__AER_LH',

                            # Landsat-5
                            'l1g': 'L1G',
                            'level1g': 'L1G',
                            'level1t': 'L1T',
                            'terrain-corrected': 'L1T',

                            # Landsat-7
                            'Level1 GT': 'L1GT',
                            'Geocorrected Terrain Corrected': 'L1GT',
                            'Global Land Survey': 'GTC_1P',

                            # Landsat-8
                            'Level-1 TP': 'L1TP',
                            'Surface Reflectance': 'L2SP'
                            }


# ---
# ## Unit test definition

# ### interpret_collection_name

def test_interpret_collection_name():
    """
    Tests interpret_collection_name.
    """

    # Sentinel missions
    for mission_number in ('1', '2', '3', '5P', '6', '1-rtc'):
        for collection_root in ('Sentinel', 'sentiNEL-', 'S', 's'):
            assert interpret_collection_name(f'{collection_root}{mission_number}') == f'SENTINEL-{mission_number.upper()}'

    # Mosaics
    for collection in ('globalmosaics', 'Global-Mosaics'):
        assert interpret_collection_name(collection) == 'GLOBAL-MOSAICS'

    # SMOS
    assert interpret_collection_name('Smos') == 'SMOS'

    # ENVISAT
    for collection in ('envi-sat', 'MERIS'):
        assert interpret_collection_name(collection) == 'ENVISAT'

    # Landsat missions
    for mission_number in ('5', '7', '8'):
        for collection_root in ('Landsat', 'LandSAT-', 'L', 'Ls'):
            assert interpret_collection_name(f'{collection_root}{mission_number}') == f'LANDSAT-{mission_number}'
    
    # Copernicus DEM
    for collection in ('cop DEM', 'CopernicusDEM'):
        assert interpret_collection_name(collection) == 'COP-DEM'

    # MODIS
    for collection in ('Terra', 'AQUA', 'Terra_Aqua', 'Modis'):
        assert interpret_collection_name(collection) == 'TERRAAQUA'

    # Global Land Cover
    for collection in ('S-2 GLC', 'Global Land Cover', 'GLC'):
        assert interpret_collection_name(collection) == 'S2GLC'

    # CCM
    for collection in ('ccm', 'Copernicus Contributing Missions'):
        assert interpret_collection_name(collection) == 'CCM'


# ### interpret_product_type

def test_interpret_product_type():
    """
    Tests interpret_product_type.
    """

    for input_name, output_name in PRODUCT_TYPE_TEST_CASES.items():
        assert interpret_product_type(input_name) == output_name

