import math

class Ranker:
    def __init__(self):
        pass


    @staticmethod
    def rank_relevant_doc(relevant_doc):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        docRanker = []  # List of COSIM for each doc
        for docID in relevant_doc.keys():

            enumerate = sum(relevant_doc[docID][0].values())
            denominator = math.sqrt(sum([math.pow(x,2) for x in relevant_doc[docID][0].values()]))
            docRanker.append( ((enumerate/denominator)+relevant_doc[docID][1], docID) ) # tuple: (cosSim,docID)

        return sorted(docRanker, reverse=True)

    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
