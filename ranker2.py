import math
from operator import itemgetter

class Ranker:
    def __init__(self):
        pass


    @staticmethod
    def rank_relevant_docs(relevant_doc):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        sorted_relevant_doc = sorted(relevant_doc.items(),key=itemgetter(1), reverse=True)
        return sorted_relevant_doc

    @staticmethod
    def retrieve_top_k(relevant_docs, k=None):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        return ranked_results
