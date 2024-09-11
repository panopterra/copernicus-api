#!/usr/bin/env python
# coding: utf-8

# # Copernicus Query and Download
# 
# (c) 2024 Panopterra UG (haftungsbeschraenkt)
# 
# ---

# ## Load packages and modules

import time
import requests
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely.wkt
from shapely import Point, Polygon, MultiPolygon, make_valid
from shapely.ops import unary_union

from .response import get_checksums, get_cloud_cover, determine_group_identifier
from .query import reduce_wkt_coordinate_precision, convert_special_characters
from .vector import reproject_geometry


# ---
# ## Internal functions

warnings.simplefilter(action='ignore', category=UserWarning)


# ### Custom Errors

class CopernicusQueryConstructorError(Exception):
    """
    A custom error class for query check fails.
    """

    pass


class CopernicusQueryAttributeError(Exception):
    """
    A custom error class for cases where an attribute filter is set for a 
    pre-defined attribute.
    """

    pass


# ## Query

# ### QueryConstructor

class QueryConstructor:
    """
    Allows easy step-by-step construction of an ODATA query to Copernicus DataSpace.
    See Notes for details on behavior.
    
    Parameters
    ----------
    interactive : bool; default=False
        If True, enables automatic 'testing' of the query. This means that whenever
        a new filter is added, the query is sent to the API and the number of products 
        in the current query is reported in logs.
        NOTE: the testing is only run when at least three filter criteria have been
        added to avoid excessive query runs for generic filters like 'Sentinel-2'
        resulting in 1000s of products.
    request_timeout : int; default=60
        The maximum time to wait for a response from the API for any request/download
        sent (in seconds).
    max_retries : int; default=3
        The number of retries in case of any issues during API requests.
    decimals : int; default=6
        The number of decimals to use in AOI coordinates (i.e. coordinate precision).
        NOTE: decimal places are cut off, not rounded.

    Attributes
    ----------
    _n_filters : int
        The number of filters applied so far (to avoid checking too unspecific
        queries; see interactive parameter description above).
    _query_parts : dict
        Contains the individual filter settings parts of the query as individual
        strings.
    _query_settings : dict
        Contains the individual filter settings provided by the user.
    interactive : bool
        See __init__.
    max_retries : int
        See __init__.
    request_timeout : int
        See __init__.

    Notes
    -----
    Way of operation:
    Each method adds a different type of filter to the query. If the same method
    is called multiple times, it overwrites the previous settings. The only exception
    to this is the add_attribute_filter method where each call will add an additional
    filter to the list.
    Due to the way the ODATA API works, all filters are combined via boolean AND.

    Limitation:
    This class is purely intended for constructing the main filter part of the
    query. Options relating to queries for specific products (by name/ID) or
    selecting query results (like top/skip etc.) are handled separately as needed
    in other functions/classes.

    For details on the OpenData API, please refer to the documentation:
    https://documentation.dataspace.copernicus.eu/APIs/OData.html
    """

    def __init__(self, 
                 interactive : bool = False,
                 request_timeout : int = 60,
                 max_retries : int = 3,
                 decimals : int = 6) -> None:

        self.interactive = interactive
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.decimals = decimals
        self._n_filters = 0
        self._products = None
        self._query_parts = {}
        self._query_settings = {'aoi': None,
                                'collection': None,
                                'product_type': None,
                                'publication_date': None,
                                'sensing_start_date': None,
                                'sensing_end_date': None,
                                'cloud_cover': None,
                                'attributes': None}
    
    ### INTERNAL METHODS

    def _create_products_geodataframe(self, 
                                      products : list[dict]) -> gpd.GeoDataFrame:
        """
        Creates a GeoDataFrame from products received from API, does some preparations
        and creates a few additional (unified) columns for later use.
        
        Parameters
        ----------
        products : list of dic
            The products as returned by the API.
        
        Returns
        -------
        gpd.GeoDataFrame
            Contains all metadata from products, incl. additional columns produced.
        """

        # create a simple pd.DataFrame from products list
        df = pd.DataFrame(products)

        # extract/unify some information from existing columns
        df['file_name'] = df['Name']
        df['file_size'] = df['ContentLength'].apply(lambda x: x / 1024 / 1024)
        df['group_id'] = df['Name'].apply(determine_group_identifier)
        df['cloud_cover'] = df['Attributes'].apply(get_cloud_cover)
        df[['checksum_md5', 'checksum_blake3']] = list(df['Checksum'].apply(get_checksums))
        df['download_path'] = df['Id'].apply(lambda x: f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({x})/$value")
        df['geometry'] = df['Footprint'].apply(lambda x: shapely.wkt.loads(x.split(';')[-1].strip("'\"")).buffer(0))

        # convert date strings to datetime objects; omitting milliseconds for compatibility
        df['publication_date'] = df['PublicationDate'].apply(lambda x: datetime.strptime(x.split('.')[0], '%Y-%m-%dT%H:%M:%S'))
        df['sensing_start_date'] = df['ContentDate'].apply(lambda x: datetime.strptime(x['Start'].split('.')[0], '%Y-%m-%dT%H:%M:%S'))
        df['sensing_end_date'] = df['ContentDate'].apply(lambda x: datetime.strptime(x['End'].split('.')[0], '%Y-%m-%dT%H:%M:%S'))
                                             
        # convert to gpd.GeoDataFrame in WGS84
        gdf = gpd.GeoDataFrame(df, crs='epsg:4326')

        # additional geometry columns; calculating footprint_size and aoi_coverage
        # in web mercator projection (3857)
        gdf_web_mercator = gdf.to_crs('epsg:3857')
        gdf['centroid'] = gdf['geometry'].centroid
        gdf['footprint_size'] = gdf_web_mercator['geometry'].area / 1e6

        # AOI coverage
        if self.query_settings['aoi'] is not None:
            aoi = reproject_geometry(self.query_settings['aoi'], 4326, 3857)
            gdf['aoi_coverage'] = gdf_web_mercator.intersection(aoi).area / aoi.area
        else:
            gdf['aoi_coverage'] = 1.
        
        return gdf
    

    ### PROPERTIES
    
    @property
    def aoi_coverage(self):
        """
        Returns the total AOI coverage of all products in the current query as
        a fraction. If no products are found or no AOI was set, returns 0.
        """
        
        if self._products is None or self.query_settings['aoi'] is None:
            print('No products found or no AOI set. AOI coverage of 0.')
            return 0.
        elif len(self._products) == 0:
            print('No products found. AOI coverage of 0.')
            return 0.
        else:
            if self.query_settings['aoi'].area == 0:
                return 1.
            else:
                return np.round(self._products.unary_union.intersection(self.query_settings['aoi']).area / self.query_settings['aoi'].area, 5)
    
    @property
    def products(self):
        """
        Returns the current products GeoDataFrame. If not available, will call
        send_query() and update internal attributes.
        In other words: always returns the current version of the products table
        and ensures the latest results are stored.
        """

        if self._products is None:
            products, result = self.send_query()
            products = products
            self._latest_result = result
            self._products = products
            return products.sort_values('Name').reset_index(drop=True)
        else:
            return self._products.sort_values('Name').reset_index(drop=True)
    
    @property
    def query(self) -> str:
        """
        Returns the current version of the query.
        """

        query = 'https://catalogue.dataspace.copernicus.eu/odata/v1/Products?'

        # add filters
        query += '$filter='
        other_filters = [self._query_parts[k] for k in self._query_parts.keys() if k != 'attributes']
        query += ' and '.join(other_filters)

        # handle attribute filters separately
        if 'attributes' in self._query_parts.keys():
            attributes_filter = ' and '.join(self._query_parts['attributes'])
            query += f' and {attributes_filter}'

        return query
    
    @property
    def query_settings(self) -> dict:
        """
        Returns the current query settings.
        """

        return self._query_settings
    

    ### EXTERNAL METHODS

    def add_aoi_filter(self, 
                       aoi : Point|Polygon|MultiPolygon|list[Point|Polygon|MultiPolygon],
                       decimals : int = None) -> None:
        """
        Filters for a specific AOI (point of polygon).
        
        Parameters
        ----------
        aoi : shapely.Point/shapely.Polygon/shapely.MultiPolygon or list of shapely.Point/shapely.Polygon/shapely.MultiPolygon
            The area of interest. Must be in WGS84.
            NOTE: any input that is not a single Point or Polygon will be converted
            to a (Multi)Polygon via unary_union.
        decimals : int; default=None
            The number of decimals to use in AOI coordinates (i.e. coordinate precision).
            If None, uses the number of decimals provided during initialization
            (default: 6).
            NOTE: decimal places are cut off, not rounded.

        Returns
        -------
        None
        """

        # convert other geometry types or lists of geometries to Polygon/MultiPolygon
        if not isinstance(aoi, Point) and not isinstance(aoi, Polygon):
            aoi = unary_union(aoi)
        
        # make invalid geometries valid
        if not aoi.is_valid:
            aoi = make_valid(aoi)

        # determine decimal precision
        if decimals is None:
            decimals = self.decimals

        wkt_str = reduce_wkt_coordinate_precision(aoi.wkt, decimals=self.decimals)
        if len(wkt_str) > 2000:
            print(f'AOI WKT string is very long ({len(wkt_str)}). Consider simplifying the AOI polygon to reduce risk of exceeding query string limit.')
        print(f'Adding AOI filter: {wkt_str}')
        # only increment filter count if the same filter has not already been set before
        if 'aoi' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['aoi'] = f"ODATA.CSC.Intersects(area=geography'SRID=4326;{wkt_str}')"
        self._query_settings['aoi'] = aoi

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_attribute_filter(self, 
                             name : str,
                             operator : str,
                             value : str|int|float,
                             attribute_type : str) -> None:
        """
        Filters for a specific attribute.
        For further details, please refer to the OpenData API documentation:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-by-attributes

        NOTE: this method supports filtering for any available attribute, except
        cloudCover and productType (use corresponding methods instead).
        
        Parameters
        ----------
        name : str
            Name of the attribute.
        operator : str
            The boolean operator to use for the query. The API supports the following
            operators (depending on the attribute type, see API documentation):
            eq: equal;
            lt: lower than;
            le: lower than or equal;
            gt: greater than;
            ge: greater than or equal.
        value : str or int or float
            The value expected for the operator (data type of this parameter should
            be in accordance to the attribute type).
        attribute_type : str
            Type of attribute. Options:
            string: StringAttribute;
            integer: IntegerAttribute;
            double: DoubleAttribute;
            datetimeoffset: DateTimeOffsetAttribute.
        
        Returns
        -------
        None
        """

        if name == 'cloudCover':
            raise CopernicusQueryAttributeError(f"To filter by cloud cover, please use the add_cloud_cover_filter method instead.")
        elif name == 'productType':
            raise CopernicusQueryAttributeError(f"To filter by product type, please use the add_product_type_filter method instead.")
        
        # convert special characters in attributes before creating query
        name = convert_special_characters(name)
        value = convert_special_characters(value)

        print(f'Adding attribute filter: {name} {operator} {value} ({attribute_type})')
        if 'attributes' not in self._query_parts.keys():
            self._query_parts['attributes'] = []
            self._query_settings['attributes'] = []

        self._query_parts['attributes'].append(f"Attributes/OData.CSC.{attribute_type.capitalize()}Attribute/any(att:att/Name eq '{name}' and att/OData.CSC.{attribute_type.capitalize()}Attribute/Value {operator} '{value}')")
        self._query_settings['attributes'].append((name, operator, value, attribute_type))
        self._n_filters += 1

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_cloud_cover_filter(self,
                               ccover : int|float|tuple[int]|tuple[float]) -> None:
        """
        Filters by cloud cover.
        
        Parameters
        ----------
        ccover : int/float or tuple of int/float
            If a single int/float is provided, will be interpreted as the maximum
            allowed cloud cover. If a tuple of two ints/floats is provided, will
            be interpreted as (minimum, maximum).
            NOTE: values in percentage between 0 and 100. Maximum accuracy of 
            query is 2 decimal places (e.g., 10.35764 would be queried as 10.35).
        
        Returns
        -------
        None
        """

        # verify compatibility with collection
        if self._query_settings['collection'] is not None:
            if self._query_settings['collection'].lower() != 'sentinel-2':
                raise CopernicusQueryConstructorError(f"Collection of name '{self._query_settings['collection'].upper()}' does not support cloud cover filter.")

        if isinstance(ccover, float) or isinstance(ccover, int):
            ccover_max = ccover
            ccover_min = 0
        else:
            ccover_min, ccover_max = ccover

        print(f'Adding cloud cover filter: {ccover_min} to {ccover_max}')
        # only increment filter count if the same filter has not already been set before
        if 'cloud_cover' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['cloud_cover'] = f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value ge {ccover_min:.2f}) and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le {ccover_max:.2f})"
        self._query_settings['cloud_cover'] = ccover

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_collection_filter(self, 
                              collection : str) -> None:
        """
        Filters for a specific collection.
        
        Parameters
        ----------
        collection : str
            The collection to query.
        
        Returns
        -------
        None
        """

        # verify compatibility with collection
        if self._query_settings['cloud_cover'] is not None:
            if collection.lower() != 'sentinel-2':
                raise CopernicusQueryConstructorError(f"Collection of name '{collection.upper()}' does not support cloud cover filter.")

        print(f'Adding collection filter: {collection}')
        # only increment filter count if the same filter has not already been set before
        if 'collection' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['collection'] = f"Collection/Name eq '{collection.upper()}'"
        self._query_settings['collection'] = collection

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_product_type_filter(self, 
                                product_type : str) -> None:
        """
        Filters for a specific product type.
        
        Parameters
        ----------
        product_type : str
            The product type.
        
        Returns
        -------
        None
        """

        print(f'Adding product type filter: {product_type.upper()}')
        # only increment filter count if the same filter has not already been set before
        if 'product_type' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['product_type'] = f"Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{product_type.upper()}')"
        self._query_settings['product_type'] = product_type

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_publication_date_filter(self, 
                                    start : str|datetime, 
                                    end : str|datetime) -> None:
        """
        Filters for a publication date range.
        
        Parameters
        ----------
        start : str or datetime.datetime
            The start date as either a string of format 'YYYY-MM-DDThh:mm:ss.000Z'
            or a datetime object.
        end : str or datetime.datetime
            The end date as either a string of format 'YYYY-MM-DDThh:mm:ss.000Z'
            or a datetime object.
        
        Returns
        -------
        None
        """

        if isinstance(start, datetime):
            start_str = datetime.strftime(start, '%Y-%m-%dT%H:%M:%S.000Z')
        else:
            start_str = start
        if isinstance(end, datetime):
            end_str = datetime.strftime(end, '%Y-%m-%dT%H:%M:%S.000Z')
        else:
            end_str = end

        print(f'Adding publication date filter: {start_str} to {end_str}')
        # only increment filter count if the same filter has not already been set before
        if 'publication_date' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['publication_date'] = f'PublicationDate ge {start_str} and PublicationDate le {end_str}'
        self._query_settings['publication_date'] = (start, end)

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_sensing_end_date_filter(self,
                                    start : str|datetime, 
                                    end : str|datetime) -> None:
        """
        Filters for a sensing end date range.
        
        Parameters
        ----------
        start : str or datetime.datetime
            The start date as either a string of format 'YYYY-MM-DDThh:mm:ss.000Z'
            or a datetime object.
        end : str or datetime.datetime
            The end date as either a string of format 'YYYY-MM-DDThh:mm:ss.000Z'
            or a datetime object.
        
        Returns
        -------
        None
        """

        if isinstance(start, datetime):
            start_str = datetime.strftime(start, '%Y-%m-%dT%H:%M:%S.000Z')
        else:
            start_str = start
        if isinstance(end, datetime):
            end_str = datetime.strftime(end, '%Y-%m-%dT%H:%M:%S.000Z')
        else:
            end_str = end

        print(f'Adding sensing end date filter: {start_str} to {end_str}')
        # only increment filter count if the same filter has not already been set before
        if 'sensing_end_date' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['sensing_end_date'] = f'ContentDate/End ge {start_str} and ContentDate/End le {end_str}'
        self._query_settings['sensing_end_date'] = (start, end)

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()

    def add_sensing_start_date_filter(self,
                                      start : str|datetime, 
                                      end : str|datetime) -> None:
        """
        Filters for a sensing start date range.
        
        Parameters
        ----------
        start : str or datetime.datetime
            The start date as either a string of format 'YYYY-MM-DDThh:mm:ss.000Z'
            or a datetime object.
        end : str or datetime.datetime
            The end date as either a string of format 'YYYY-MM-DDThh:mm:ss.000Z'
            or a datetime object.
        
        Returns
        -------
        None
        """

        if isinstance(start, datetime):
            start_str = datetime.strftime(start, '%Y-%m-%dT%H:%M:%S.000Z')
        else:
            start_str = start
        if isinstance(end, datetime):
            end_str = datetime.strftime(end, '%Y-%m-%dT%H:%M:%S.000Z')
        else:
            end_str = end

        print(f'Adding sensing start date filter: {start_str} to {end_str}')
        # only increment filter count if the same filter has not already been set before
        if 'sensing_start_date' not in self._query_parts.keys():
            self._n_filters += 1
        self._query_parts['sensing_start_date'] = f'ContentDate/Start ge {start_str} and ContentDate/Start le {end_str}'
        self._query_settings['sensing_start_date'] = (start, end)

        if self.interactive and self._n_filters >= 3:
            _ = self.check_query()
    
    def check_query(self) -> int:
        """
        Checks the query as it is currently defined by sending the current version
        of the query to the API, not retrieving all results in detail. For that,
        please use send_query() instead.

        Parameters
        ----------
        None
        
        Returns
        -------
        int
            The number of products in the query.
        """

        result = requests.get(self.query+'&$count=True&$top=1').json()
        if '@odata.count' not in result.keys():
            raise CopernicusQueryConstructorError(f'Error or empty query result: {result}')
        n_products = result['@odata.count']
        print(f'Current query contains {n_products} products.')
        return n_products
    
    def create_copy(self):
        """
        Creates a copy of itself (new instance with same settings).
        Primarily intended when used in other classes that may modify settings in
        the instance.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        QueryConstructor
            New instance (copy).
        """

        new_instance = QueryConstructor(self.interactive)
        new_instance._n_filters = self._n_filters
        new_instance._query_parts = self._query_parts.copy()
        new_instance._query_settings = self._query_settings.copy()
        return new_instance
    
    def query_by_name(self, 
                      product_names : list[str]) -> tuple[gpd.GeoDataFrame,dict]:
        """
        Retrieves a list of specific products by name.

        Parameters
        ----------
        product_names : list of str
            Contains the names of products to retrieve from Catalog API (incl.
            extensions such as '.SAFE').
            NOTE: ideally, the list should not be longer than a few dozen items.
        
        Returns
        -------
        gpd.GeoDataFrame
            Contains information about all products in the query.
        dict
            The raw result as returned by the API.

        Notes
        -----
        This methods uses the GET command for retrieving individual items from
        the Catalog API. The best practice would be to use a POST command
        instead (as recommended in the API documentation), however, that option
        does not seem to allow to expand Assets and Attributes resulting in issues
        with subsequent steps.
        As a result, long lists of product names can lead to large numbers of 
        API calls.
        """
        
        # send the query, retrieve results
        products = []
        for name in product_names:
            result = requests.get(f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?&$count=True&$expand=Attributes&$expand=Assets&$filter=Name eq '{name}'", timeout=self.request_timeout).json()
            if '@odata.count' in result.keys():
                products.extend(result['value'])

        # if the full result contains any products, prepare results and update
        # internal attribautes
        if len(products) > 0:
            products = self._create_products_geodataframe(products)
            total_file_size = np.sum(products['file_size'].values) / 1024
            percentage_online = np.sum(products['Online']) / len(products)
            print(f'Retrieved {len(products)} products ({total_file_size:.2f} GB, {percentage_online*100:.2f}% online).')
            # update internal attributes with current result
            self._products = products
            self._latest_result = result

            return products, result
        else:
            raise CopernicusQueryConstructorError('No products matching query.')

    def send_query(self,
                   skip : int = 0,
                   n_entries : int = 1000,
                   orderby : str = None) -> tuple[gpd.GeoDataFrame,dict]:
        """
        Sends the query in its current form to the API. Stores current results in
        attributes.

        Parameters
        ----------
        skip : int; default=0
            Number of items to skip in query, e.g. to only consider later
            results.
        n_entries : int; default=1000
            Number of items to retrieve in a single API call.
        orderby : str; default=None
            The field to order results. For details and limitations, please refer 
            to API documentation:
            https://documentation.dataspace.copernicus.eu/APIs/OData.html#orderby-option
        
        Returns
        -------
        gpd.GeoDataFrame
            Contains information about all products in the query.
        dict
            The raw result as returned by the API.

        Notes
        -----
        Handling of large product lists:
        Each query returns the number of products in the entire query result 
        ('count=True') but only n_entries are returned with each request. If n_entries
        is smaller than the total number of products in the query, this method will
        auromatically run further API calls to retrieve all products.

        Updates to internal attributes:
        Each time this method is called, it updates the internal _latest_result
        attribute based on the results obtained from the API call. Only exception: 
        if the product list is empty, the result is not stored.
        """
        
        print('Sending query.')
        
        # get query and add additional parameters as required
        query = self.query
        if skip is not None:
            query += f'&$skip={skip}'
        if n_entries is not None:
            query += f'&$top={n_entries}'
        if orderby is not None:
            query += f'&$orderby={orderby[0]} {orderby[1]}'

        # send the query, retrieve results; attempt retries if API is unresponsive
        for _ in range(self.max_retries):
            try:
                result = requests.get(query+'&$count=True&$expand=Attributes&$expand=Assets&$expand=Locations', timeout=self.request_timeout).json()
                if '@odata.count' not in result.keys():
                    raise CopernicusQueryConstructorError(f'Error or empty query result: {result}')
                products = result['value']
                break
            except Exception as e:
                print(f'Request failed (waiting for retry). -> {type(e).__name__}: {e}')
                time.sleep(5)

        # run additional API calls to obtain all pages of results if number of
        # products is larger than n_entries
        while '@odata.nextLink' in result.keys():
            query = result['@odata.nextLink']
            query = query.split('&$count')[0]
            result = requests.get(query, timeout=self.request_timeout).json()
            products.extend(result['value'])
        
        # if the full result contains any products, prepare results and update
        # internal attribautes
        if len(products) > 0:
            products = self._create_products_geodataframe(products)
            total_file_size = np.sum(products['file_size'].values) / 1024
            percentage_online = np.sum(products['Online']) / len(products)
            print(f'Retrieved {len(products)} products ({total_file_size:.2f} GB, {percentage_online*100:.2f}% online).')
            # update internal attributes with current result
            self._products = products
            self._latest_result = result

            return products, result
        else:
            raise CopernicusQueryConstructorError('No products matching query.')

