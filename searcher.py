from parser_module import Parse
from ranker import Ranker
import utils
import math


class Searcher:

    def __init__(self, inverted_index, term_max_freq):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index
        self.term_max_freq = term_max_freq

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        postingLoadedNames = [] # Names of posting file which we already loaded.
        posting = [] # List of posting files which were loaded already

        relevant_docs = {} #{docID: [{terms in query:tfidf} , bonus_score]}
        query_dict = {}
        for termInd in range(len(query)):
            term = query[termInd]
            if(term not in query_dict.keys()):
                query_dict[term] = 0
            query_dict[term] += 1

        for termIndex in range(len(query_dict.keys())):
            term = list(query_dict.keys())[termIndex]

            try:  # an example of checks that you have to do
                # Update the local dicts: freq of the term in this doc:

                type = [0, 1, 2, 3]

                # Deciding the type of the term
                if (self.isfloat(term) == True):  # numbers
                    type = 0
                elif (len(term) == 1):  # others
                    type = 1
                elif (' ' in term):  # entities
                    type = 2
                else:  # strings
                    type = 3

                postingNames = self.inverted_index[type][term][2]


                numOfDocsPerTerm = 0

                for postingName in postingNames:
                    if(postingName not in postingLoadedNames): #its a list so i think its should be one by one ???????????????
                        postingLoadedNames.append(postingName) # Add the name of the new file
                        newPosting = utils.load_obj(postingName) # load the file
                        posting.append(newPosting) # Add the dictionary to the posting files
                    posting_index = postingLoadedNames.index(postingName)
                    posting_doc = posting[posting_index][term] # load the relevant tweets data per term
                    for doc_tuple in posting_doc:
                        docID = doc_tuple[1]
                        freq = doc_tuple[0]
                        maxFreqInDoc = self.term_max_freq[docID]
                        tf = freq /  maxFreqInDoc
                        idf = math.log((len(self.term_max_freq) / self.inverted_index[type][term][0]), 2)
                        numOfDocsPerTerm += 1
                        if docID not in relevant_docs.keys():
                          relevant_docs[docID] = [{term:tf*idf * query_dict[term]},0] #we can delete the number
                        else:
                            if termIndex > 0 and query_dict[list(query_dict.keys())[termIndex-1]] in relevant_docs[docID][0].keys(): #its a term
                                relevant_docs[docID][1] += 1 #bonous
                            relevant_docs[docID][0][term] = tf*idf


            except:
                print('term {} not found in posting'.format(term))
        return relevant_docs

    def isfloat(self,value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False