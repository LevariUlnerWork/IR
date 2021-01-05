import string
from parser_module import Parse
from ranker import Ranker
import utils
import math
import operator


class LocalMethod:

    def __init__(self, inverted_index, loadingPath, posting_files):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.tweetsTerms = utils.load_obj( "TweetTerm_%s" % (0))
        self.inverted_index = inverted_index
        self.posting_files = posting_files
        self.loadingPath = loadingPath
        self.SijThreshold = 0.7

    def new_words_to_query(self):
        print ("hi")

    def compute_Cij(self):
        print ("hello")




    def compute_final_rank(self,original_rank,new_rank,num_docs_to_retrieve):
        '''
        this function gets the 2 ranks of: the original query and the new one, and returns the top k of
        the average rank.
        '''
        final_rank_dict = {}

        for docTuple in original_rank:
            doc_id = docTuple[0]
            rank = docTuple[1]
            if doc_id not in final_rank_dict.keys():
                final_rank_dict[doc_id] = rank

        for docTuple in new_rank:
            doc_id = docTuple[0]
            rank = docTuple[1]
            if doc_id not in final_rank_dict.keys():
                final_rank_dict[doc_id] = 0
            final_rank_dict[doc_id] += rank / 2

        return sorted(final_rank_dict.items(), key=operator.itemgetter(1), reverse=True)[:num_docs_to_retrieve]