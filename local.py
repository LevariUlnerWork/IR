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

        cII = self.compute_Cij(term_query, term_query,rel_docsIDs) #cII = sum of every freq^2 of the term in each doc from the local data

        words_to_append = []
        if cII != 0:

            term_query_posting = self.posting_files[self.inverted_index[term_query][2]]#term == apple -> posting_ap

            for tweet_data in term_query_posting[term_query]:#[ [7,docid=1,[1,2,3,4,5,6,7],0.35436] , [1,docid=2,[1],0.4567]...]
                if tweet_data[1] in rel_docsIDs:
                    doc_id = tweet_data[1]
                    for term in self.tweetsTerms[doc_id]:
                        if term != term_query and term in self.inverted_index.keys():

                            cIJ = self.compute_Cij(term_query,term,rel_docsIDs)
                            cJJ = self.compute_Cij(term,term,rel_docsIDs)
                            Sij = cIJ / (cII + cJJ - cIJ)

                            if( Sij > self.SijThreshold):
                                if term not in words_to_append:
                                    words_to_append.append(term)

        return words_to_append



    def compute_Cij(self, term1, term2, rel_docsIDs):

        if(term1 not in self.inverted_index.keys() or term2 not in self.inverted_index.keys()):
            return 0

        #Create dict of appearances of term1
        term1_show = {} #{docID: freq_in_doc}
        term1_posting = self.posting_files[self.inverted_index[term1][2]][term1]
        for doc_data in term1_posting:

            doc_id = doc_data[1]
            freq = doc_data[0]
            term1_show[doc_id] = freq

        # Create dict of appearances of term2
        if (term1 == term2): #for case: cii | cjj
            term2_show = term1_show
        else:
            term2_show = {}
            term2_posting = self.posting_files[self.inverted_index[term2][2]][term2]
            for doc_data in term2_posting:

                doc_id = doc_data[1]
                freq = doc_data[0]
                term2_show[doc_id] = freq

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
        final_rank_dict = {} # {docID: points)

        for docTuple in original_rank:

            doc_id = docTuple[0]
            rank = docTuple[1]
            final_rank_dict[doc_id] = rank

        for docTuple in new_rank:
            doc_id = docTuple[0]
            rank = docTuple[1]
            if doc_id not in final_rank_dict.keys():
                final_rank_dict[doc_id] = 0
            final_rank_dict[doc_id] += rank / 2

        return sorted(final_rank_dict.items(), key=operator.itemgetter(1), reverse=True)[:num_docs_to_retrieve] #[(docid,rank)...]