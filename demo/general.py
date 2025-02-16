
query = {
    "match_all": {}
}

# Basic match query
query1 = {
    "match": {"name": "AibA4jqBJnQT"}
}

# Match query with filters (age > 30 and active status)
query2 = {
    "match": {"name": "YTa2ryD6eVSe"}
}



query3 = {
    "match_all": {}
}
sort_desc = [{"score": "desc"}]

query4 = {
    "match_all": {}
}
limit4 = 3
offset4 = 5

query5 = {
    "match_all": {}
}
aggregations1 = {
    "age_groups": {
        "terms": {"field": "age"}
    },
    "active_status": {
        "terms": {"field": "active"}
    }
}
query6 = {
    "bool": {
        "must": [{"match": {"active": True}}],
    }
}


query7 = {
    "bool": {
        "must": [
            {
                "match": {
                    "age": 51
                }
            },
            {
                "match": {
                    "email": "YSLhFeXd@yANp3h.com"
                }
            }
        ]
    }
}





filters1 = [
    {"range": {"age": {"gt": 30}}},
    {"term": {"active": False}}
]
filters2 = {
    "bool": {
        "filter": [
            {"range": {"age": {"gte": 30}}},
            {"term": {"metadata.attributes.attributes.value": "trg5iSat2x"}}
        ]
    }
}


search_queries = {
    "match_all_query": query,
    "basic_search_query": query1,
    "sesrch": query7,
    "complex_bool": query6
}

search_filters = {
    "filter1": filters1,
    "filter2": filters2,
}

aggregations = {
    "aggregation1": aggregations1
}

sortings = {
    "sort_desc": sort_desc
}










index_name_example_1 = "test_index_1"
index_name_example_2 = "test_index_2"
alias_name_example = "test_alias"
index_mappings_example = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "default": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": ["lowercase", "asciifolding"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "text"},
            "age": {"type": "integer"},
            "email": {"type": "keyword"},
            "score": {"type": "float"},
            "active": {"type": "boolean"},
            "created_at": {"type": "date", "format": "yyyy-MM-dd"},
            "metadata": {
                "properties": {
                    "name": {"type": "text"},
                    "attributes": {
                        "properties": {
                            "name": {"type": "text"},
                            "attributes": {
                                "properties": {
                                    "value": {"type": "text"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}