
# Copernicus API

This module is designed to facilitate interaction with the [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
APIs (specifically the OData API). It offers the user a Pythonic interface to
interactively construct and send queries, and retrieve and organize the API responses.
It takes away much of the complexity and pitfalls involved in the process of
creating API calls.

---

<br>

> **Known bugs and limitations**<br>
>
> * Currently, only the ODATA API is supported. Support for the STAC API may follow
in the future, however, at this time (late 2024), the STAC API is not yet final and
feature-complete.

---

<br>

## 1. Installation

The `copernicusapi` package can be installed via `pip` using the following command:

```Bash
pip install copernicusapi
```

<br>

## 2. Usage

At the core of this package is the `QueryConstructor` class that facilitates creation
of queries to the Data Space OData Catalog API. Please refer to the 
[documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html)
for details on API options and behavior.

Each method of the `CopernicusQueryConstructor` class adds a different type of filter
to a query for a step-wise construction of the full query string. The filters can
be combined in any order as needed. A full list of all options is provided under
[Filter methods](#31-filter-methods).

At any stage in the process, the current query can be obtained via the `query`
property. The current query settings (as provided by the user and used to construct
the query) can be accessed via the property `query_settings`. The results of
the latest call of `send_query()` are also accessible via the `products` and
`api_response` properties.

>**IMPORTANT:** All filter methods usually overwrite any previously defined settings.
This means that calling, for example, the `add_collection_filter` method a second
time will simply remove the previous filter and replace it with the new one. The
`add_attribute_filter` method is the only method that can be applied multiple
times with different settings. _Due to the way the API is designed, all filters
are always combined via boolean `AND`._


### 2.1 Initialization

The `CopernicusQueryConstructor` class can be initialized without any arguments.

```Python
from copernicusapi import QueryConstructor

query_constructor = QueryConstructor()
```

There is also the option of an `interactive` mode, where the current query is automatically
sent to the API after any method is called, retrieving the number of products in the
query and returing the products count as indicated by the API (see `check_query()` below).
This helps avoid errors in the query since a faulty query will become evident
immediately after each method call. However, this may also slow down the process
and cause many superfluous calls to the API.

There are also some additional settings that affect the behavior of the query process:
`max_retries` determines how many times failed API requests are repeated. This is
important since the Copernicus API may occasionally be down or unresponsive.
The `request_timeout` parameter determines how long a single API request is allowed
to take before timing out. These settings should usually be left at their default values.
Lastly, the `decimals` parameter determines the coordinate precision in AOI filters
(i.e. the number of decimal places of coordinate values). The default is 6, which
is sufficient in most cases.

>**NOTE:** For complex AOIs with many vertices, the query string can get very long
and may exceed the maximum allowed string length when using higher coordinate
precision. Cutting off superfluous decimals by reducing the `decimals` value can
alleviate that. If very high precision is required, one can increase the `decimals`
parameter up to whatever the precision of the original AOI is.

### 2.2 A standard query for Sentinel-2 L2A products

As a simple example, a query for Sentinel-2 L2A products is constructed below.
Four methods are needed for this.

```Python
from shapely.geometry import Polygon

# define AOI
aoi = Polygon([(9.43111261, 50.16247502),
               (10.83966524, 50.16247502),
               (10.83966524, 48.43995062),
               (9.43111261, 48.439950626),
               (9.43111261, 50.16247502)])

# define the collection
query_constructor.add_collection_filter('sentinel-2')

# define product type
query_constructor.add_product_type_filter('l2a')

# define AOI via a shapely geometry Point or Polygon in WGS84 (optionally, 
# decimal precision can be provided here as well)
query_constructor.add_aoi_filter(aoi)

# define the timeframe based on sensing start date
query_constructor.add_sensing_start_date_filter(datetime(2023, 7, 5), datetime(2023, 8, 25))
```

>**IMPORTANT:** 
>1. The way collections and product types can be defined is very flexible,
and the process supports many aliases for the default collection and product type
names. Currently, all Sentinel and Landsat, as well as many additional collections
are supported. Please refer to [Collection and product type names](#32-collection-and-product-type-names)
for a full overview.
>2. AOIs are expected to be shapely geometries (esp. `Point`, `Polygon` or
`MultiPolygon`) or lists of such geometries, in WGS84 (EPSG:4326). Other reference systems are
not supported. All geometries other than single `Point` or `Polygon` objects
will be converted to a single `(Multi)Polygon` via `unary_union`.
>3. All date filters (publication date, sensing start date, sensing end date)
can be defined via `datetime.datetime` objects or time `strings` in the format
`YYYY-MM-DDThh:mm:ss.000Z` (the last three zeros representing milliseconds).

### 2.3 Filter by cloud cover

It is possible to filter by maximum cloud cover or a range of cloud cover percentage.

```Python
# search for products with a cloud cover <= 25%
query_constructor.add_cloud_cover_filter(25)

# search for products with a cloud cover between 10% and 22.5%
query_constructor.add_cloud_cover_filter((10, 22.5))
```


### 2.4 Check query

The `check_query()` method sends the query in its current form to the OData API and
checks if any errors or exceptions occur. It returns the number of products in the
query. This method is also automatically called when setting `interactive=True`
during initialization.

>**IMPORTANT:** This method does not retrieve all results. For this, use the `send_query()`
method instead (see next example).

>**NOTE:** Since `check_query()` is much faster and light-weight, esp. for queries
resulting in large numbers of matching products, it is recommended to call `check_query()`
before calling `send_query()`. This way, you can see how many products match the
current search and potentially narrow it down.

```Python
# Assuming the query has been constructed following the previous examples
n_products = query_constructor.check_query()
print(n_products)

-> Out: 14
```

### 2.5 Send query

Other than `check_query()`, the `send_query()` method retrieves all results from the
query to the OData API, and allows for use of the keyword arguments `skip` (skipping
the first N entries), `n_entries` (return first N items in the results) and `orderby`
(order results). For details please refer to the [ODATA API Documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html#orderby-option).

This method returns two objects: a `gpd.GeoDataFrame` containing all products in the
query result arranged in a table with some additional columns (see also
[Products GeoDataFrame](#33-products-geodataframe) for details), and the original
"raw" API response JSON `dict` object. These outputs are also accessible via the
`products` and `api_response` properties.

```Python
products, result = query_constructor.send_query()

-> Out: Retrieved 14 products (13.83 GB, 100.00% online).
```

The information about the total size (`13.83 GB` in the example above) is calculated
from the `ContentLength` information provided by the API for each product.
Unfortunately, these values are not available for all products. Thus, the value
given here should only be considered to be an estimate.

>**IMPORTANT:** The `send_query()` method will always retrieve the full list of
products matching the query, even if the result contains 1000s of items that must
be downloaded in batches (happens automatically in the background). If your query
results in a very large number of matching products, the process may take quite long.
_It is therefore recommended to call `check_query()` first and potentially narrowing
down the search before calling `send_query()`._

>**NOTE:** Once a query was sent (and if an AOI was set previously), one can use
the property `aoi_coverage` to see the total AOI coverage of all products in the
current query as a fraction. This can be used to confirm if the entire study area
is covered by at least one product in the result.

### 2.6 Filter by attribute

For even more detailed control, one can also filter by any of the attributes 
available for the products via the `add_attribute_filter` method. This is the only
method that can be applied multiple times with different settings. It is a generic
interface to applying arbitrary attribute filters and is a bit more low-level than
the other methods. It takes the name of the attribute, the logical operator used in
the comparison (supported: `eq`, `lt`, `le`, `gt`, `ge`), the value of the attribute 
that should be present, and the attribute type (`string`, `integer`, `double`, 
`datetimeoffset`).
Please refer to the [API documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-by-attributes)
for details.

>**NOTE:** The `add_attribute_filter` method will not accept the `cloudCover` and
`productType` attributes. Please use the corresponding methods instead.

```Python
# Example of filtering by "orbitDirection" (available in Sentinel-1 products)

# default method call
query_constructor.add_attribute_filter('orbitDirection', 'eq', 'ASCENDING', 'string')

# detailed keyword-based method call
query_constructor.add_attribute_filter(name='orbitDirection', 
                                       operator='eq',
                                       value='ASCENDING',
                                       attribute_type='string')
```


### 2.7 Query by product names

As an alternative to the query construction process, one can also directly query
for specific products by name via the `query_by_name()` method. The only parameter
is a list of product names as `str` (incl. file extensions such as `.SAFE`).

>**IMPORTANT:** This method is not compatible with any of the filter methods above
but intended solely for use on its own.

```Python
products, result = query_constructor.query_by_name(
        ['S1A_IW_GRDH_1SDV_20141031T161924_20141031T161949_003076_003856_634E.SAFE',
         'S2A_MSIL1C_20230106T102411_N0509_R065_T32UNU_20230106T122023.SAFE'])

-> Out: Retrieved 2 products (2.37 GB, 100.00% online).
```

<br>

## 3. Technical description

### 3.1 Filter methods

1. `add_collection_filter`: adds a filter by data collection (e.g., `sentinel-2`).
It is not case-sensitive and supports also alternative notation such as `sentinel2`
or `s2`. See [Collection and product type names](#32-collection-and-product-type-names)
for details.
2. `add_product_type_filter`: adds a filter by type of product (e.g., `GRD`, `L2A`).
It is not case-sensitive and also supports some alternative notations such as `level2a`
or `level-2a`. See [Collection and product type names](#32-collection-and-product-type-names)
for details.
3. `add_aoi_filter`: adds a filter by a specific location point or polygon (area
of interest). _**NOTE:** The term "AOI" is used loosely here for any kind of geographic
filter geometry._
4. `add_sensing_start_date_filter`: adds a filter by the start time of the acquisition
(i.e., the actual observation time; in many cases more or less equivalent to
sensing end date).
5. `add_sensing_end_date_filter`: adds a filter by the end time of the acquisition
(i.e., the actual observation time; in many cases more or less equivalent to
sensing start date).
6. `add_publication_date_filter`: adds a filter by publication date of a product (i.e.,
the time it has been published in the data repository).
7. `add_cloud_cover_filter`: adds a filter by (minimum and) maximum cloud cover (only
relevant for optical products).
8. `add_attribute_filter`: adds a filter by any available attribute (_**NOTE:**
this is the only filter that can be applied multiple times_).

### 3.2 Collection and product type names

Any collection or product type names passed to the `add_collection_filter` and
`add_product_type_filter` methods will be first homogenized by converting them to
lower-case and removing any white space, `-` and `_` from the string. This means
that `Sentinel-2` will work just as well as `sentinel-2`, `sentinel2` or `SENTINEL 2`,
for example. The same is true for `OL_1_EFR___`, `OL1EFR`, `OL 1 efr` etc.

To further facilitate the search, most collection and product type names have
aliases (see tables below). The same homogenization is applied to these as well.

#### Collections

| Mission                                 | Collection Name  | Aliases                                                     |
| --------------------------------------- | ---------------- | ----------------------------------------------------------- |
| Sentinel-1                              | `SENTINEL-1`     | `S1`                                                        |
| Sentinel-1 RTC                          | `SENTINEL-1-RTC` | `S1RTC`                                                     |
| Sentinel-2                              | `SENTINEL-2`     | `S2`                                                        |
| Sentinel-3                              | `SENTINEL-3`     | `S3`                                                        |
| Sentinel-5p                             | `SENTINEL-5P`    | `S5P`                                                       |
| Sentinel-6                              | `SENTINEL-6`     | `S6`                                                        |
| Copernicus Contributing Missions (CCM)  | `CCM`            | `Copernicus Contributing Missions`, `Contributing Missions` |
| Copernicus DEM                          | `COP-DEM`        | `Copernicus DEM`, `Cop DEM`                                 |
| Envisat                                 | `ENVISAT`        | `-`                                                         |
| Global Mosaics                          | `GLOBAL-MOSAICS` | `Mosaics`                                                   |
| Landsat-5                               | `LANDSAT-5`      | `L5`, `LS5`                                                 |
| Landsat-7                               | `LANDSAT-7`      | `L7`, `LS7`                                                 |
| Landsat-5                               | `LANDSAT-8`      | `L8`, `LS8`                                                 |
| MODIS Terra/Aqua                        | `TERRAAQUA`      | `Terra`, `Aqua`, `MODIS`                                    |
| Sentinel-2 Global Land Cover            | `S2GLC`          | `Global Land Cover`, `GLC`                                  |
| Soil Moisture and Ocean Salinity (SMOS) | `SMOS`           | `-`                                                         |

#### Product types

| Mission/Sensor                          | Product                                                                              | Product Type Name | Aliases                                                                    |
| --------------------------------------- | ------------------------------------------------------------------------------------ | ----------------- | -------------------------------------------------------------------------- |
| Sentinel-1                              | Level-0 RAW (IW and EW)                                                              | `RAW`             | `Level-0`, `L0`                                                            |
|                                         | Level-1 Single Look Complex (IW and EW)                                              | `SLC`             | `Single Look Complex`, `Level-1 SLC`, `L1 SLC`                             |
|                                         | Level-1 Ground Range Detected (IW and EW)                                            | `GRD`             | `Ground Range Detected`, `Level-1 GRD`, `L1 GRD`                           |
|                                         | Level-1 Ground Range Detected High-Resolution (IW and EW)                            | `GRDH`            | `Ground Range Detected High-Resolution`, `Level-1 GRDH`, `L1 GRDH`         |
|                                         | Level-2 Ocean                                                                        | `OCN`             | `Ocean`, `Level-2`, `L2`                                                   |
|                                         | Backscatter                                                                          | `CARD-BS`         | `CARD Backscatter`, `Backscatter`                                          |
|                                         | Coherence                                                                            | `CARD-COH6`       | `CARD Coherence6`, `CARD Coherence`, `Coherence6`, `Coherence`, `CARD-COH` |
| Sentinel-1 RTC                          | Radiometric Terrain Corrected                                                        | `RTC`             | `Radiometric Terrain Corrected`                                            |
| Sentinel-2                              | Level-1C                                                                             | `S2MSI1C`         | `Level-1C`, `L1C`, `TOA`                                                   |
|                                         | Level-2A                                                                             | `S2MSI2A`         | `Level-2A`, `L2A`, `BOA`                                                   |
| Sentinel-3 OLCI                         | Earth Observation Full Resolution                                                    | `OL_1_EFR___`     | `EFR`, `OLCI EFR`                                                          |
|                                         | Earth Observation Reduced Resolution                                                 | `OL_1_ERR___`     | `ERR`, `OLCI ERR`                                                          |
|                                         | Land and Atmosphere Full Resolution                                                  | `OL_2_LFR___`     | `LFR`, `OLCI LFR`                                                          |
|                                         | Land and Atmosphere Reduced Resolution                                               | `OL_2_LRR___`     | `LRR`, `OLCI LRR`                                                          |
|                                         | Water and Atmosphere Full Resolution                                                 | `OL_2_WFR___`     | `WFR`, `OLCI WFR`                                                          |
|                                         | Water and Atmosphere Reduced Resolution                                              | `OL_2_WRR___`     | `WRR`, `OLCI WRR`                                                          |
| Sentinel-3 SLSTR                        | Radiance and Brightness Temperature                                                  | `SL_1_RBT___`     | `RBT`, `SLSTR RBT`                                                         |
|                                         | Land Surface Temperature                                                             | `SL_2_LST___`     | `LST`, `SLSTR LST`                                                         |
|                                         | Water Surface Temperature                                                            | `SL_2_WST___`     | `WST`, `SLSTR WST`                                                         |
|                                         | Fire Radiative Power                                                                 | `SL_2_FRP___`     | `FRP`, `SLSTR FRP`                                                         |
| Sentinel-3 SRAL                         | Level-1A                                                                             | `SR_1_SRA_A_`     | `SRA_A`, `SRAL SRA_A`, `L1A`                                               |
|                                         | Level-1B                                                                             | `SR_1_SRA___`     | `SRA`, `SRAL SRA`, `L1B`                                                   |
|                                         | Level-1B-S                                                                           | `SR_1_SRA_BS`     | `SRA_BS`, `SRAL SRA_BS`, `L1BS`                                            |
|                                         | Hydrology Thematic Products                                                          | `SR_2_LAN_HY`     | `SRAL LAN_HY`, `Hydrology`                                                 |
|                                         | Sea Ice Thematic Products                                                            | `SR_2_LAN_SI`     | `SRAL LAN_SI`, `Sea Ice`                                                   |
|                                         | Land Ice Thematic Products                                                           | `SR_2_LAN_LI`     | `SRAL LAN_LI`, `Land Ice`                                                  |
|                                         | Land Products (not generated anymore)                                                | `SR_2_LAN___`     | `SRAL LAN`, `Land`                                                         |
|                                         | Water Products (generated by the Marine Centre)                                      | `SR_2_WAT___`     | `SRAL WAT`, `Water`                                                        |
| Sentinel-3 Synergy                      | Surface Reflectance and Aerosol Parameters (over land)                               | `SY_2_SYN`        | `SYN`, `Synergy`                                                           |
|                                         | VEGETATION-like 1 km product (VGT-P) - TOA Reflectance                               | `SY_2_VGP`        | `VGP`, `Vegetation P`                                                      |
|                                         | VEGETATION-like 1 km product (VGT-S1) 1-day synthesis surface reflectance and NDVI   | `SY_2_VG1`        | `VG1`, `Vegetation S1`                                                     |
|                                         | VEGETATION-like 1 km product (VGT-S10) 10-day synthesis surface reflectance and NDVI | `SY_2_V10`        | `V10`, `Vegetation S10`                                                    |
|                                         | Global Aerosol Parameter on super pixel resolution (4.5 km x 4.5 km)                 | `SY_2_AOD`        | `AOD`, `Aerosol`, `Aerosol Optical Depth`, `Optical Depth`                 |
| Sentinel-5p                             | Radiance product bands 1-8                                                           | `L1B_RA_BDx`      | `RA_BDx`                                                                   |
|                                         | Irradiance product UVN module                                                        | `L1B_IR_UVN`      | `IR_UVN`                                                                   |
|                                         | Irradiance product SWIR module                                                       | `L1B_IR_SIR`      | `IR_SIR`                                                                   |
| Sentinel-6                              | Advanced Microwave Radiometer for Climate Level-2                                    | `MW_2__AMR____`   | `S-6 MW_2_AMR`, `MW_2_AMR`                                                 |
|                                         | Poseidon-4 Altimetry Level-1B High Resolution                                        | `P4_1B_HR_____`   | `S-6 P4_1B_HR`, `P4_1B_HR`                                                 |
|                                         | Poseidon-4 Altimetry Level 1B Low Resolution                                         | `P4_1B_LR_____`   | `S-6 P4_1B_LR`, `P4_1B_LR`                                                 |
|                                         | Poseidon-4 Altimetry Level-2 High Resolution                                         | `P4_2__HR_____`   | `S-6 P4_2__HR`, `P4_2__HR`                                                 |
|                                         | Poseidon-4 Altimetry Level-2 Low Resolution                                          | `P4_2__LR_____`   | `S-6 P4_2__LR`, `P4_2__LR`                                                 |
| Copernicus Contributing Missions (CCM)  | -                                                                                    | `-`               | `-`                                                                        |
| Copernicus DEM                          | -                                                                                    | `-`               | `-`                                                                        |
| Envisat                                 | All available products (standard naming)                                             | `-`               | `-`                                                                        |
| Global Mosaics                          | Sentinel-1 IW Monthly Mosaics                                                        | `S1SAR_L3_IW_MCM` | `S-1 IW monthly`, `S-1 IW monthly mosaic`                                  |
|                                         | Sentinel-1 DH Monthly Mosaics                                                        | `S1SAR_L3_DH_MCM` | `S-1 DH monthly`, `S-1 DH monthly mosaic`                                  |
|                                         | Sentinel-2 Quarterly Mosaics                                                         | `S2MSI_L3__MCQ`   | `S-2 quarterly`, `S-2 quarterly mosaic`                                    |
| Landsat-5                               | Level-1 Ground                                                                       | `L1G`             | `Level-1G`, `Ground`, `Georeferenced`                                      |
|                                         | Level-1 Terrain Corrected                                                            | `L1T`             | `Level-1T`, `Terrain`, `Terrain Corrected`                                 |
| Landsat-7                               | Level-1 Ground                                                                       | `L1G`             | `Level-1G`, `Ground`, `Georeferenced`                                      |
|                                         | Level-1 Terrain Corrected                                                            | `L1T`             | `Level-1T`, `Terrain`, `Terrain Corrected`                                 |
|                                         | Level-1 Geocorrected and Terrain Corrected                                           | `L1GT`            | `Level-1GT`, `Geocorrected Terrain`, `Geocorrected Terrain Corrected`      |
|                                         | Global Land Survey 1-arc second Panchromatic                                         | `GTC_1P`          | `Global Land Survey`, `Panchromatic`, `Global Land Survey Panchromatic`    |
| Landsat-8                               | Level-1 Terrain Corrected                                                            | `L1T`             | `Level-1T`, `Terrain`, `Terrain Corrected`                                 |
|                                         | Level-1 Geocorrected and Terrain Corrected                                           | `L1GT`            | `Level-1GT`, `Geocorrected Terrain`, `Geocorrected Terrain Corrected`      |
|                                         | Level-1 Precision Terrain Corrected (incl. QA Band)                                  | `L1TP`            | `Level-1TP`, `Precision Terrain`, `Precision Terrain Corrected`            |
|                                         | Level-2 Surface Reflectance                                                          | `L2SP`            | `Level-2SP`, `Surface Reflectance`, `SR`                                   |
| MODIS Terra/Aqua                        | All available products (standard naming)                                             | `-`               | `-`                                                                        |
| Sentinel-2 Global Land Cover            | -                                                                                    | `-`               | `-`                                                                        |
| Soil Moisture and Ocean Salinity (SMOS) | All available products (standard naming)                                             | `-`               | `-`                                                                        |


### 3.3 Products GeoDataFrame

The `send_query()` method returns a `gpd.GeoDataFrame` that contains all information
that was returned by the API. Further, it contains some additional columns:

1. `aoi_coverage`: fraction of the AOI covered by this product (if no AOI was defined, will be 0.).
2. `centroid`: the centroid of the product footprint.
3. `checksum_blake3`: the Blake3 checksum (if available).
4. `checksum_md5`: the MD5 checksum (if available).
5. `cloud_cover`: the cloud cover percentage (taken from product attributes, if available).
6. `download_url`: the full download URL of the product.
7. `file_name`: equivalent to `Name` column.
8. `file_size`: the file size in MB (calculated from `ContentLength` if available).
9.  `footprint_size`: the total area of the footprint in km² (in Web Mercator, EPSG:3857).
10. `geometry`: the footprint used as the `geometry` column of the `GeoDataFrame`.
11. `group_tile_id`: a custom unique identifier of tiles (only supported for
Sentinel-1/-2/-3/-5p products). This is using parts of the product name and is not
to be confused with the `productGroupId` attribute.
12. `product_type` the type of a product (taken from product attributes, if available).
12.  `publication_date`: publication date as a `datetime.datetime`/`pd.TimeStamp`
object (obtained from `PublicationDate`).
13.  `sensing_end_date`: sensing end date as a `datetime.datetime`/`pd.TimeStamp`
object (obtained from `ContentDate`).
14.  `sensing_start_date`: sensing start date as a `datetime.datetime`/`pd.TimeStamp`
object (obtained from `ContentDate`).

>**IMPORTANT:** Some of these columns may be empty (`NaN`/`None`) for some collections
or product types. Occasionally, some of the extracted information is missing for certain
products (e.g. not all products have checksums).