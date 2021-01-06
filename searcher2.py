import string
from parser_module import Parse
from ranker2 import Ranker
import utils
import math


class Searcher:

    def __init__(self, parser, indexer, model=None):
        """
        :param inverted_index: dictionary of inverted index
        """
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self.inverted_index = indexer.inverted_idx
        self.posting_files = indexer.postingFiles

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        query_as_list = self._parser.parse_sentence(query)
        # thisStemmer = self._parser.stemming
        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, ranked_doc_ids, query_as_list







    def _relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        query_dict = {} #{term:freq in query}
        for termInd in range(len(query)):
            term = query[termInd]
            if(term not in query_dict.keys()):
                query_dict[term] = 0
            query_dict[term] += 1

        query_tf = {}
        for term in query_dict:
            freq_max_query = max(list(query_dict.values()))
            query_tf[term] = query_dict[term]/freq_max_query

        tfIdfThisQueryPowList = [math.pow(x, 2) for x in query_tf.values()]
        denominator = math.sqrt(sum(tfIdfThisQueryPowList))

        for term in query_dict:
            query_dict[term] = query_tf[term] / denominator

        postingFileName = ""

        relevant_docs = {}  #relevant_docs = {tweetId: rank}
        query_terms = sorted(list(query_dict.keys()))
        for term in query_terms:
                if(term not in self.inverted_index.keys()):
                    continue

                postingFileName = self.inverted_index[term][2]

                for tweetData in self.posting_files[postingFileName][term]:
                    doc_id = tweetData[1]
                    tfidf = tweetData[3] * query_dict[term]
                    relevant_docs[doc_id] = tfidf

        return relevant_docs

    def isfloat(self,value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False
