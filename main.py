from demo import ELKConnector, KibanaClient, DataGenerator
from demo import search_queries, search_filters, aggregations, sortings
from demo import index_name_example_1, index_name_example_2, alias_name_example, index_mappings_example
import os

elk_credentials = {
    "host": os.getenv("ELK_HOSTE"),
    "user": os.getenv("ELK_USERNAME"),
    "pass": os.getenv("ELK_PASSWORD"),
    "cert": {
        "ca_cert": os.getenv("ELK_CA_CERT"),
        "client_cert": os.getenv("ELK_CERT"),
        "client_key": os.getenv("ELK_KEY")
    },
    "kibana_host": os.getenv("KIBANA_HOSTE"),
}


connector = ELKConnector(**elk_credentials)
connector.connect()
connector.health()
connector.info()



connector.create_index(index_name=index_name_example_1, index_body=index_mappings_example)
connector.put_alias_for_index(index_name=index_name_example_1, alias_name=alias_name_example)

data_gen = DataGenerator()
for doc in range(900):
    random_data = data_gen.generate_random_data()
    connector.index_document(index_name=index_name_example_1, document_body=random_data)

info = connector.get_index_info(index_name=index_name_example_1)

results = connector.search(index_name=index_name_example_1, query=search_queries['match_all_query'], filters=None, sort=sortings['sort_desc'], limit=100, offset=0, aggregations=aggregations['aggregation1'])

connector.delete_index(index_name=index_name_example_1)
connector.close()

