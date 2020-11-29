import math

class Ranker:
    def __init__(self, Iindexer=None):
        self.indexer = Iindexer
        self.tf_idf_dict = {}
        self.docRanker = {}  # dict of COSIM for each doc

        #pass

    @staticmethod
    def rank_relevant_doc(self, relevant_doc):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        for doc_tuple in relevant_doc:
            docID = doc_tuple[0].tweet_id
            maxFreqNum = self.indexer.term_max_freq[docID][1]
            N = 10  # num of docs ??????????????????????????????????????????????
            for term in doc_tuple[0].term_doc_dictionary.keys():
                termFreq = doc_tuple[0].term_doc_dictionary[term][1]  # number of the term in this doc
                tf = termFreq / maxFreqNum
                numOfDocs = self.indexer.inverted_idx[term][0]
                cal = N / numOfDocs
                idf = math.log(cal, 2)
                self.tf_idf_dict[term] = tf * idf

            docRank = 0
            numTermsInQuery = doc_tuple[1]
            for term, num in self.tf_idf_dict.items():
                if term in doc_tuple[2]:
                    docRank += num
                sum += pow(num, 2)

            denominator = math.sqrt(sum) * math.sqrt(numTermsInQuery)

            self.docRanker[docID] = docRank / denominator

        return sorted(relevant_doc.items(), key=lambda item: item[1][0], reverse=True)

    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
