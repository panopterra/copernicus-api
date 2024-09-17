#!/usr/bin/env python
# coding: utf-8

# # Query Test
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
                            'ol1efr': 'OL_1_EFR___',
                            'err': 'OL_1_ERR___',
                            'ol2-wfr': 'OL_2_WFR___',
                            'OLCIwrr': 'OL_2_WRR___',
                            'olci LFR': 'OL_2_LFR___',
                            'lrr': 'OL_2_LRR___',

                            # Sentinel-3 SLSTR
                            'rbt': 'SL_1_RBT___',
                            'sl2lst': 'SL_2_LST___',
                            'slstrwst': 'SL_2_WST___',
                            'sl2frp': 'SL_2_FRP___',

                            # Sentinel-3 SRAL
                            'sr1sra': 'SR_1_SRA___',
                            'sraa': 'SR_1_SRA_A_',
                            'SRALsrabs': 'SR_1_SRA_BS',
                            'lan': 'SR_2_LAN___',
                            'LAN-HY': 'SR_2_LAN_HY',
                            'LAN SI': 'SR_2_LAN_SI',
                            'SRAL LAN LI': 'SR_2_LAN_LI',
                            'wat': 'SR_2_WAT___',

                            # Sentinel-3 Synergy
                            'Synergy': 'SY_2_SYN___',
                            'Vegetationp': 'SY_2_VGP___',
                            'vG1': 'SY_2_VG1___',
                            'Vegetation S10': 'SY_2_V10___',
                            'Aerosol Optical Depth': 'SY_2_AOD___',

                            # Sentinel-5p
                            'l1bra1': 'L1B_RA_BD1',
                            'RA3': 'L1B_RA_BD3',
                            'L1B RA5': 'L1B_RA_BD5',
                            'IR SIR': 'L1B_IR_SIR',
                            'L1B IRUVN': 'L1B_IR_UVN',
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

                            # Sentinel-6
                            'S-6 MW2 AMR': 'MW_2__AMR____',
                            'S-6 P4 1B lr': 'P4_1B_LR_____',
                            'S-6 P4 1B Hr': 'P4_1B_HR_____',
                            'P4 2 LR': 'P4_2__LR_____',
                            'S-6 P4 2hr': 'P4_2__HR_____',

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
    for collection in ('envi-sat', ):
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

