
# Copernicus API

This module is designed to facilitate interaction with the [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
APIs (specifically the OData API). It offers the user a Pythonic interface to
interactively construct and send queries, and retrieve and organize the API responses.
It takes and takes away much of the complexity and pitfalls involved in the process
of creating API calls.

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

The `copernicusapi` package can simply be install via the following command:

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
[Filter methods](#31-filter-methods)

At any stage in the process, the current query can be obtained via the `query`
property. The current query settings (as provided by the user and used to construct
the query) can be accessed via the property `query_settings`.

>**IMPORTANT:** All filter methods usually overwrite any previously defined settings.
This means that calling, for example, the `add_collection_filter` method a second
time will simply remove the previous filter and replace it with the new one. The
`add_attribute_filter` method is the only method that can be applied multiple
times with different settings.

>**NOTE:** Due to the way the API is designed, all filters are always combined
via boolean `AND`.


### 2.1 Initialization

The `CopernicusQueryConstructor` class can be initialized without any arguments.

```Python
query_constructor = QueryConstructor()
```

The `CopernicusQueryConstructor` class can be initialized without any arguments.
The only option is the `interactive` parameter. In `interactive` mode, the current
query is sent to the API after any method is called, logging the number of products
in the query and returning the products count alongside the raw result as returned
by the API (see `check_query()` below). This helps avoid errors in the query since
a faulty query will become evident immediately after each method call.

There is also the option of an `interactive` mode, where the current query is automatically
sent to the API after any method is called, logging the number of products in the
query and returning the products count returned by the API (see `check_query()` below).
This helps avoid errors in the query since a faulty query will become evident
immediately after each method call. However, this may also slow down the process
and cause many superfluous calls to the API.

There are also some additional settings that affect the behavior of the query process:
`max_retries` determines how many times failed API requests are repeated. This is
important since the Copernicus API may occasionally be down or unresponsive.
The `request_timeout` parameter determines how long a single API request is allowed
to take before timing out. These settings should usually be left at their default values.
Lastly, the `decimals` parameter determines the coordinate precision in AOI filters
(i.e. the number of decimal places of coordinate values). The default is 4, which
is sufficient in most cases.

>**NOTE:** For complex AOIs with many vertices, the query string can get very long
and may exceed the maximum allowed string length when using higher coordinate
precision. Cutting off superfluous decimals can alleviate that. If very high precision
is required, one can increase the `decimals` parameter up to whatever the precision
of the original AOI is.

### 2.2 A standard query for Sentinel-2 L2A products

Four methods are needed to construct this search.

>**IMPORTANT:** AOIs are expected to be shapely geometries (esp. `Point`, `Polygon` or
`MultiPolygon`) or lists of such geometries, in WGS84. Other reference systems are
not supported. All geometries other than single `Point` or `Polygon` objects
will be converted to a single `(Multi)Polygon` via `unary_union`.

>**NOTE:** All date filters (publication date, sensing start date, sensing end date)
can be defined via `datetime.datetime` objects or time `strings` in the format
`YYYY-MM-DDThh:mm:ss.000Z` (the last three zeros representing milliseconds).

```Python
# define the collection (this is NOT case-sensitive)
query_constructor.add_collection_filter('sentinel-2')

# define product type (this is NOT case-sensitive)
query_constructor.add_product_type_filter('l2a')

# define AOI via a shapely geometry Point or Polygon in WGS84 (optionally, 
# decimal precision can be provided here as well)
query_constructor.add_aoi_filter(aoi)

# define the timeframe based on sensing start date
query_constructor.add_sensing_start_date_filter(datetime(2023, 6, 1), datetime(2023, 9, 1))
```

### 2.3 Filter by cloud cover

It is possible to filter by maximum cloud cover or a range of cloud cover percentage.

```Python
# search for products with a cloud cover <= 25%
query_constructor.add_cloud_cover_filter(25)

# search for products with a cloud cover between 10% and 22.5%
query_constructor.add_cloud_cover_filter((10, 22.5))
```

### 2.4 Filter by attribute

The `add_attribute_filter` method is the only method that can be applied multiple
times with different settings. It is a generic interface to applying arbitrary
attribute filters and is a bit more low-level than the other methods. It takes
the name of the attribute, the logical operator used in the comparison (supported:
`eq`, `lt`, `le`, `gt`, `ge`), the value of the attribute that should be present,
and the attribute type (`string`, `integer`, `double`, `datetimeoffset`).
Please refer to the [API documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-by-attributes)
for details.

>**NOTE:** The `add_attribute_filter` method will not accept the `cloudCover` and
`productType` attributes. Please use the corresponding methods instead.

```Python
query_constructor.add_attribute_filter('orbitDirection', 'eq', 'ASCENDING', 'string')

# detailed keyword-based method call
query_constructor.add_attribute_filter(name='orbitDirection', 
                                       operator='eq',
                                       value='ASCENDING',
                                       attribute_type='string')
```

### 2.5 Check query

The `check_query()` method sends the query in its current form to the ODATA API and
checks if any errors or exceptions occur. It returns the number of products in the
query. This method is also automatically called when setting `interactive=True`
during initialization.

>**NOTE:** This method does not retrieve all results. For this, use the `send_query()`
method instead (see next example).

```Python
n_products = query_constructor.check_query()
```

### 2.6 Send query

Similar to `check_query()`, the `send_query()` method sends the query to the ODATA API.
The main difference is, however, that it returns all results and allows for use of
the keyword arguments `skip` (skipping the first n entries), `n_entries` (return first
N items in the results) and `orderby` (order results). For details please refer to
the [ODATA API Documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html#skip-option).

```Python
products, result = query_constructor.send_query()
```

>**NOTE:** Once a query was sent (and if an AOI was set previously), one can use
the property `aoi_coverage` to see the total AOI coverage of all products in the
current query as a fraction. This can be used to confirm if the entire study area
is covered by at least one product in the result.

### 2.7 Query by product names

As an alternative to the query construction process, one can also directly query
for specific products by name via the `query_by_name()` method. The only parameter
is a list of product names as `str` (incl. file extensions such as `.SAFE` etc.).

>**IMPORTANT:** This method is not compatible with any of the filter methods above
but intended solely for use on its own.

```Python
products, result = copqc.query_by_name(['S1A_IW_GRDH_1SDV_20141031T161924_20141031T161949_003076_003856_634E.SAFE',
                                        'S2A_MSIL1C_20230106T102411_N0509_R065_T32UNU_20230106T122023.SAFE'])
```

<br>

## 3. Technical description

### 3.1 Filter methods

1. `add_collection_filter`: adds a filter by data collection (e.g., `sentinel-2`).
It is not case-sensitive and supports also alternative notation such as `sentinel2`
or `s2`.
2. `add_publication_date_filter`: adds a filter by publication date of a product (i.e.,
the time it has been published in the data repository).
3. `add_sensing_start_date_filter`: adds a filter by the start time of the acquisition
(i.e., the actual observation time; in many cases more or less equivalent to
sensing end date).
4. `add_sensing_end_date_filter`: adds a filter by the end time of the acquisition
(i.e., the actual observation time; in many cases more or less equivalent to
sensing start date).
5. `add_aoi_filter`: adds a filter by a specific location point or polygon (area
of interest).
6. `add_cloud_cover_filter`: adds a filter by (minimum and) maximum cloud cover (only
relevant for optical products).
7. `add_product_type_filter`: adds a filter by type of product (e.g., `GRD`, `L2A`).
It is not case-sensitive and also supports some alternative notations such as `level2a`
or `level-2a`.
8. `add_attribute_filter`: adds a filter by any available attribute (**NOTE:**
this is the only filter that can be applied multiple times).
