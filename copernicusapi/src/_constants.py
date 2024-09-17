#!/usr/bin/env python
# coding: utf-8

# # Constants
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
# This module contains constants used in other parts of the code.
# 
# ---

# ### Constants

COLLECTIONS_SUPPORTING_CLOUD_COVER = ('SENTINEL-2', 'LANDSAT-5', 'LANDSAT-7', 'LANDSAT-8')


COLLECTION_PRODUCT_TYPE_MATCHES = {'SENTINEL-1': ('CARD-BS', 'CARD-COH6', 'RAW', 'SLC', 'GRD', 'GRDH', 'OCN'),
                                   'SENTINEL-2': ('S2MSI1C', 'S2MSI2A'),
                                   'SENTINEL-3': ('OL_1_EFR___', 'OL_1_ERR___', 'OL_2_WFR___', 'OL_2_WRR___', 'OL_2_LFR___', \
                                                  'OL_2_LRR___', 'SL_1_RBT___', 'SL_2_LST___', 'SL_2_WST___', 'SL_2_FRP___', \
                                                  'SR_1_SRA_A_', 'SR_1_SRA___', 'SR_1_SRA_BS', 'SR_2_LAN___', 'SR_2_LAN_HY', \
                                                  'SR_2_LAN_SI', 'SR_2_LAN_LI', 'SR_2_WAT___', \
                                                  'SY_2_SYN___', 'SY_2_VGP___', 'SY_2_VG1___', 'SY_2_V10___', 'SY_2_AOD___'),
                                   'SENTINEL-5P': ('L1B_RA_BD1', 'L1B_RA_BD2', 'L1B_RA_BD3', 'L1B_RA_BD4', 'L1B_RA_BD5', \
                                                   'L1B_RA_BD6', 'L1B_RA_BD7', 'L1B_RA_BD8', 'L1B_IR_SIR', 'L1B_IR_UVN', \
                                                   'L2__O3____', 'L2__O3_TCL', 'L2__O3__PR', 'L2__NO2___', 'L2__SO2___', \
                                                   'L2__CH4___', 'L2__HCHO__', 'L2__CLOUD_', 'L2__AER_AI', 'L2__AER_LH'),
                                   'SENTINEL-6': ('MW_2__AMR____', 'P4_1B_LR_____', 'P4_1B_HR_____', 'P4_2__LR_____', \
                                                  'P4_2__HR_____'),
                                   'SENTINEL-1-RTC': ('RTC', ),
                                   'GLOBAL-MOSAICS': ('S2MSI_L3__MCQ', 'S1SAR_L3_IW_MCM', 'S1SAR_L3_DH_MCM'),
                                   'SMOS': None,
                                   'MODIS': None,
                                   'ENVISAT': None,
                                   'LANDSAT-5': ('L1G', 'L1T'),
                                   'LANDSAT-7': ('L1G', 'L1T', 'L1GT', 'GTC_1P'),
                                   'LANDSAT-8': ('L1T', 'L1GT', 'L1TP', 'L2SP'),
                                   }

