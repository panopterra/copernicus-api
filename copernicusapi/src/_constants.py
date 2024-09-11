#!/usr/bin/env python
# coding: utf-8

# # Constants
# 
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# ---

# ### Constants

COLLECTIONS_SUPPORTING_CLOUD_COVER = ('SENTINEL-2', 'LANDSAT-5', 'LANDSAT-7', 'LANDSAT-8')


COLLECTION_PRODUCT_TYPE_MATCHES = {'SENTINEL-1': ('CARD-BS', 'CARD-COH6', 'RAW', 'SLC', 'GRD', 'OCN'),
                                   'SENTINEL-2': ('S2MSI1C', 'S2MSI2A'),
                                   'SENTINEL-3': ('EFR', 'ERR', 'WFR', 'WRR', 'LFR', 'LRR', 'RBT', 'LST', 'WST', 'WCT', \
                                                  'FRP', 'SRA', 'SRA_A', 'SRA_BS', 'LAN', 'LAN_HY', 'LAN_SI', 'LAN_LI', \
                                                  'WAT', 'SYN', 'VGP', 'VG1', 'VG10', 'AOD'),
                                   'SENTINEL-5P': ('L1B_RA_BD1', 'L1B_RA_BD2', 'L1B_RA_BD3', 'L1B_RA_BD4', 'L1B_RA_BD5', \
                                                   'L1B_RA_BD6', 'L1B_RA_BD7', 'L1B_RA_BD8', 'IR_SIR', 'IR_UVN', \
                                                   'L2__O3____', 'L2__O3_TCL', 'L2__O3__PR', 'L2__NO2___', 'L2__SO2___', \
                                                   'L2__CH4___', 'L2__HCHO__', 'L2__CLOUD_', 'L2__AER_AI', 'L2__AER_LH'),
                                   'LANDSAT-5': ('L1G', 'L1T'),
                                   'LANDSAT-7': ('L1G', 'L1T', 'L1GT', 'GTC_1P'),
                                   'LANDSAT-8': ('L1T', 'L1GT', 'L1TP', 'L2SP'),
                                   }

