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

    def new_words_to_query(self,term_query, rel_docsIDs):

        cII = self.compute_Cij(term_query, term_query,rel_docsIDs)
        words_to_append = []
        if cII != 0:
            term_query_posting = self.posting_files[self.inverted_index[term_query][2]]
            for tweet_data in term_query_posting[term_query]:
                if tweet_data[1] in rel_docsIDs:
                    for term in self.tweetsTerms[tweet_data[1]]:
                        if term != term_query and term in self.inverted_index.keys():
                            cIJ = self.compute_Cij(term_query,term,rel_docsIDs)
                            cJJ = self.compute_Cij(term,term,rel_docsIDs)
                            if((cII + cJJ - cIJ) == 0):
                                print(term_query + " " + term)
                            if( cIJ / (cII + cJJ - cIJ) > self.SijThreshold):
                                if term not in words_to_append:
                                    words_to_append.append(term)

        return words_to_append



    def compute_Cij(self,term1,term2,rel_docsIDs):

        if(term1 not in self.inverted_index.keys() or term2 not in self.inverted_index.keys()):
            return 0

        #Create dict of appearance of term1
        term1_show = {}
        term1_posting = self.posting_files[self.inverted_index[term1][2]][term1]
        for doc_data in term1_posting:
            term1_show[doc_data[1]] = doc_data[0]

        # Create dict of appearance of term2
        if (term1 == term2): #for case: cii | cjj
            term2_show = term1_show
        else:
            term2_show = {}
            term2_posting = self.posting_files[self.inverted_index[term2][2]][term2]
            for doc_data in term2_posting:
                term2_show[doc_data[1]] = doc_data[0]

        cij = 0

        for rel_docID in rel_docsIDs:
            if(rel_docID not in term1_show.keys() or rel_docID not in term2_show.keys()): # freq1 * freq2 = 0
                continue
            else:
                term1_freq = term1_show[rel_docID]
                term2_freq = term2_show[rel_docID]
                cij += term1_freq * term2_freq

        return cij

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