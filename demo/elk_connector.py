from elasticsearch import Elasticsearch, AsyncElasticsearch, exceptions, NotFoundError
from elastic_transport import (
    ApiError,
    ConnectionError,
    ConnectionTimeout,
    TransportError,
)
import ssl
import time


class ELKConnector():
    
    def __init__(self, persistent=False, **elk_credentials):
        """
        Initialize the Elasticsearch connector.
        :param host: Elasticsearch host URL.
        :param user: Username for authentication.
        :param pass: Password for authentication.
        :param certs: Path to the bundle of certificates for SSL verification.
        """
        self.host = elk_credentials['host']
        self.username = elk_credentials['user']
        self.password = elk_credentials['pass']
        self.bundle_certs = elk_credentials['cert']
        self.client = None
        self.connected = 0
        self.max_retries = 25
        self.persistent = persistent
        self.retrieve_retries = 4
        self.update_retries = 4
        self.append_retries = 4
        self.get_client_timeout = 25
        self.ssl_context = self.create_ssl_context()
        print(f"Used Elasticsearch Host {self.host} with User {self.username}")
    
    def create_ssl_context(self):
        """
        Create the SSL context for connecting to Elasticsearch using the CA and client certificates.
        """
        ssl_context = ssl.create_default_context(cafile=self.bundle_certs['ca_cert'])
        ssl_context.load_cert_chain(certfile=self.bundle_certs['client_cert'], keyfile=self.bundle_certs['client_key'])
        return ssl_context
    
    def is_alive(self):
        try:
            ping = self.client.info()
            return True
        except:
            return False
    
    def verify_client_alive(self):
        """
        Verify if the Elasticsearch client is alive and reachable.

        Raises:
            ConnectionError: If the Elasticsearch client is not alive.
        """
        if not self.is_alive():
            self.client = self.connect()

    def connect(self):
        """
        Establish a connection to the Elasticsearch cluster.

        This method will attempt to connect to Elasticsearch repeatedly with a delay
        until the connection is established or maximum retry attempts are reached.

        Returns:
            Elasticsearch: A connected Elasticsearch client instance.

        Raises:
            ConnectionError: If the connection cannot be established after retries.
            ConnectionTimeout: If the connection times out repeatedly.
            TransportError: For other transport-level issues.
        """
        self.retry_attempts = 0

        while self.persistent or self.retry_attempts < self.max_retries:
            try:
                self.client = Elasticsearch(
                    hosts=[self.host],
                    basic_auth=(self.username, self.password),
                    ssl_context=self.ssl_context
                )
                if self.client.ping():
                    print(f"Connected to Elasticsearch Successfully :: host {self.host}")
                    return self.client
                else:
                    raise ConnectionError("Elasticsearch client ping failed after connection.")

            except (ConnectionError, ConnectionTimeout) as e:
                print(ConnectionError)
                print(f"[Attempt {self.retry_attempts+1}] Connection issue: {type(e).__name__}: {str(e)}. Retrying in 3 seconds...")
            except TransportError as e:
                print(f"Transport Error while connecting to Elasticsearch: {str(e)}")
                raise
            except Exception as e:
                print(f"Unexpected error: {type(e).__name__}: {str(e)}")
                raise

            self.retry_attempts += 1

            if self.retry_attempts == 10:
                print("Still trying to connect to Elasticsearch after 10 attempts...")
            if self.retry_attempts == self.max_retries and not self.persistent:
                print("Maximum retries reached. Could not connect to Elasticsearch. Giving up!")
                raise ConnectionError("Maximum retry attempts reached. Could not connect to Elasticsearch.")

            time.sleep(3)
    
    def close(self):
        """
        Close the connection to the Elasticsearch cluster.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            self.client.close()
            print("Connection closed successfully")
        except Exception as e:
            print(f"Error closing connection: {str(e)}")
            raise Exception(f"Error closing connection: {str(e)}")

    def info(self):
        """
        Retrieve information about the Elasticsearch cluster.

        Returns:
            dict: Information about the cluster.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            info = self.client.info()
            print(f"Cluster Name: {info['cluster_name']}")
            print(f"Version: {info['version']['number']}")
            print(f"Tagline: {info['tagline']}")
            return info
        except Exception as e:
            print(f"Error fetching cluster info: {str(e)}")
            raise Exception(f"Error fetching cluster info: {str(e)}")

    def health(self):
        """
        Retrieve the health of the Elasticsearch cluster.

        Returns:
            dict: Health status of the cluster.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            health = self.client.cluster.health()
            print(f"======================================================")
            print(f"Cluster Name: {health['cluster_name']}")
            print(f"Status: {health['status']}")
            print(f"Number of Nodes: {health['number_of_nodes']}")
            print(f"Number of Data Nodes: {health['number_of_data_nodes']}")
            print(f"Active Primary Shards: {health['active_primary_shards']}")
            print(f"Active Shards: {health['active_shards']}")
            print(f"Relocating Shards: {health['relocating_shards']}")
            print(f"Initializing Shards: {health['initializing_shards']}")
            print(f"Unassigned Shards: {health['unassigned_shards']}")
            print(f"======================================================")
            return health
        except Exception as e:
            print(f"Error fetching cluster health: {str(e)}")
            raise Exception(f"Error fetching cluster health: {str(e)}")
    
    def create_index(self, index_name, index_body):
        """
        Create an index in Elasticsearch.

        Args:
            index_name (str): Name of the index to be created.
            index_body (dict): Index settings and mappings.

        Returns:
            bool: True if the index is created successfully, False otherwise.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if self.client.indices.exists(index=index_name):
            print(f"Index '{index_name}' already exists.")
            return {"acknowledged": "index exists"}
        
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            response = self.client.indices.create(index=index_name, body=index_body)
            print(f"Index created successfully: {response}")
            return True
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            raise Exception(f"Error creating index: {str(e)}")
    
    def delete_index(self, index_name):
        """
        Delete an index from Elasticsearch.

        Args:
            index_name (str): Name of the index to be deleted.

        Returns:
            bool: True if the index is deleted successfully, False otherwise.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            response = self.client.indices.delete(index=index_name)
            print(f"Index deleted successfully: {response}")
            return True
        except Exception as e:
            print(f"Error deleting index: {str(e)}")
            raise Exception(f"Error deleting index: {str(e)}")
        
    def index_document(self, index_name, document_body):
        """
        Index a document in Elasticsearch.

        Args:
            index_name (str): Name of the index where the document will be indexed.
            document_id (str): Unique identifier for the document.
            document_body (dict): Document data to be indexed.

        Returns:
            bool: True if the document is indexed successfully, False otherwise.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            response = self.client.index(index=index_name,  body=document_body)
            print(f"Document indexed successfully: {response}")
            return True
        except Exception as e:
            print(f"Error indexing document: {str(e)}")
            raise Exception(f"Error indexing document: {str(e)}")
    
    def put_alias_for_index(self, index_name, alias_name):
        """
        Create an alias for an index in Elasticsearch.

        Args:
            index_name (str): Name of the index for which the alias will be created.
            alias_name (str): Name of the alias to be created.

        Returns:
            bool: True if the alias is created successfully, False otherwise.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            response = self.client.indices.put_alias(index=index_name, name=alias_name)
            print(f"Alias created successfully: {response}")
            return True
        except Exception as e:
            print(f"Error creating alias: {str(e)}")
            raise Exception(f"Error creating alias: {str(e)}")
    
    def get_index_total_docs(self, index_name):
        """
        Get the total number of documents in an index.

        Args:
            index_name (str): Name of the index.

        Returns:
            int: Total number of documents in the index.

        Raises:
            ConnectionError: If not connected to Elasticsearch.
        """
        if not self.client:
            raise ConnectionError("Not connected to Elasticsearch")
        try:
            response = self.client.count(index=index_name)
            return response['count']
        except Exception as e:
            print(f"Error getting index total documents: {str(e)}")
            raise Exception(f"Error getting index total documents: {str(e)}")
        
    
    def get_index_info(self, index_name):
        return {
            "name": index_name,
            "exists": self.client.indices.exists(index=index_name),
            "doc_count": self.get_index_total_docs(index_name=index_name),
            "aliases": self.client.indices.get_alias(index=index_name),
            "mappings": self.client.indices.get_mapping(index=index_name),
            "settings": self.client.indices.get_settings(index=index_name)
        }

    def search(self, index_name, query=None, filters=None, sort=None, limit=10, offset=0, aggregations=None):
        """
        Perform a search query on an Elasticsearch index with optional filters, sorting, pagination, and aggregations.

        Args:
            index_name (str): The name of the Elasticsearch index to search.
            query (dict, optional): The main search query (e.g., match, term, bool, etc.).
            filters (list of dict, optional): A list of filter clauses (e.g., term, range).
            sort (list of dict, optional): A list of sorting conditions (e.g., [{"field": "desc"}]).
            limit (int, optional): The maximum number of results to return. Default is 10.
            offset (int, optional): The starting offset for results (used for pagination). Default is 0.
            aggregations (dict, optional): Aggregation definitions for grouped results.

        Returns:
            dict: The search results or an error response if the query fails.
        """
        try:
            self.connect()

            params = {
                "index": index_name,
                "query": query,
                "filters": filters,
                "sort": sort,
                "limit": limit,
                "offset": offset,
                "aggregations": aggregations
            }
            print(f"Received parameter: {params}")
            
            if not self.client.indices.exists(index=index_name):
                print(f"Index '{index_name}' does not exist.")
                return {"error": "index does not exist"}
            

            search_body = {
                "from": offset,
                "size": limit,
            }

            if query:
                search_body["query"] = query
            
            if filters:
                search_body.setdefault("query", {"bool": {}})
                search_body["query"]["bool"].setdefault("filter", []).extend(filters)
            
            if sort:
                search_body["sort"] = sort
            
            if aggregations:
                search_body["aggs"] = aggregations

            response = self.client.search(index=index_name, body=search_body)
            
            print(f"Search query executed successfully on index '{index_name}'")
            return response.body
        
        except Exception as e:
            print(f"Failed to execute search on index '{index_name}': {e}" )
            return None