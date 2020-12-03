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
        # relevant_docs = [ {docID: [{terms in query:[tfIdfTermInDoc, TfIdfTermInQuery] }, sumOfAllTfIdfEveryTermDoc ^2, bonus_score]} , sumOfAllTfIdfEveryTermDoc ^2]

        docRanker = []  # List of COSIM for each doc
        tfidfAllTermsInQuery = relevant_doc[1]

        for docID in relevant_doc[0].keys():
            docRank = 0
            tfidfAllTermsInDoc = relevant_doc[0][docID][1]
            docIdBonus = relevant_doc[0][docID][2]

            for term in relevant_doc[0][docID][0].keys():
                tfidfTermInQuery = relevant_doc[0][docID][0][term][1]
                tfidfTermInDoc = relevant_doc[0][docID][0][term][0]
                enumerate = tfidfTermInDoc*tfidfTermInQuery
                denumerator = tfidfAllTermsInDoc*tfidfAllTermsInQuery
                docRank += enumerate / math.sqrt(denumerator)

            docRanker.append((docRank + docIdBonus, docID)) #tuple(cosSim rank, docID)

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
