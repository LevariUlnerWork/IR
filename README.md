# Search_Engine
The is a skeleton of a search engine project for your convenience.
Please follow the instructions provided in the file: intructions.txt

To run our project:
search_engine.py:
def main:
-corpus_path = Gets the corpus path, the default path = "TestData/"
-output_path = Gets the output path of the posting files, default = "posting"
-stemming = Gets boolean value if the stemmer would be use, default is = True
-queries = Gets a list/path of queries (files if this is path), default = ["What to do"]
-num_docs_to_retrieve = Gets the number of relevant tweets to recieve, default = 2000

def run_engine:
-corpus_path = same
-output_path = same
-stemming = same

def load_max_freq(): load our new dictionary.

def search_and_rank_query: Gets a query and give results:
-query = one query to work with
-inverted_index = as it sounds
-term_max_freq = our new dictionary
-num_docs_to_retrieve = same
-stemming = same
-output_path = same

------------------------------------------------------------------------------
Parser:
def __init__:
-Stemming = If there is a stemmer, it would get one. Default = None
-iIndexer = Gets an indexer if it should get, it can get inverted_index dictionary and go without indexer. Default = None
-invIdx = Gets an inverted_index dictionary if it needs one and didn't get any indexer. Default = None

------------------------------------------------------------------------------
Searcher:
def __init__:
-inverted_index = as it sounds
-term_max_freq = our new dictionary
-loadingPath = the path of the posting files


