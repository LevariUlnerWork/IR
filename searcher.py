import string
from parser_module import Parse
from ranker import Ranker
import utils
import math


class Searcher:

    def __init__(self, inverted_index, term_max_freq, loadingPath):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index
        self.term_max_freq = term_max_freq
        self.loadingPath = loadingPath

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        postingLoadedNames = [] # Names of posting file which we already loaded.
        posting = [] # List of posting files which were loaded already

        query_dict = {}
        for termInd in range(len(query)):
            term = query[termInd]
            if(term not in query_dict.keys()):
                query_dict[term] = 0
            query_dict[term] += 1

        # TFIDF for the whole terms in in the query:
        tfIdfAllTermsInQueryPow = self.tfPowForTermQuery(query_dict)

        relevant_docs = [{}, tfIdfAllTermsInQueryPow]  #relevant_docs = [ {docID: [{terms in query:[tfIdfTermInDoc, TfIdfTermInQuery] } sumOfAllTfIdfEveryTermDoc ^2, bonus_score]} , sumOfAllTfIdfEveryTermDoc ^2]

        for termIndex in range(len(query_dict.keys())):
            term = list(query_dict.keys())[termIndex]

            try:  # an example of checks that you have to do
                # Update the local dicts: freq of the term in this doc:

                type = [0, 1, 2, 3]
                t = term[0]
                # Deciding the type of the term
                if (self.isfloat(term) == True):  # numbers
                    type = 0
                elif (term[0] not in string.ascii_lowercase and term[0] not in string.ascii_uppercase):  # others
                    type = 1
                elif (' ' in term):  # entities
                    type = 2
                else:  # strings
                    type = 3

                if(term not in self.inverted_index.keys()):
                    if(term.lower() in self.inverted_index.keys()):
                        term = term.lower()
                        type=3
                    else:
                        continue
                postingNames = self.inverted_index[term][2]


                numOfDocsPerTerm = 0

                for postingName in postingNames:
                    if(postingName not in postingLoadedNames):
                        postingLoadedNames.append(postingName) # Add the name of the new file
                        newPosting = utils.load_obj(self.loadingPath + postingName) # load the file
                        posting.append(newPosting) # Add the dictionary to the posting files
                    posting_index = postingLoadedNames.index(postingName)
                    posting_doc = posting[posting_index][term] # load the relevant tweets data per term
                    for doc_tuple in posting_doc:

                        numOfDocsPerTerm += 1

                        docID = doc_tuple[1]
                        freq = doc_tuple[0]
                        maxFreqInDoc = self.term_max_freq[docID][0]

                        #TFIDF for this specific term in this specific doc:
                        tfTermInDoc = freq /  maxFreqInDoc
                        idfTermInDoc = math.log((len(self.term_max_freq.keys()) / self.inverted_index[term][0]), 2)

                        #TFIDF for this specific term in this query:
                        tfTermInQuery = query_dict[term] / max(query_dict.values()) #IDF would be equal 1


                        if docID not in relevant_docs[0].keys():

                            # TFIDF for the whole terms in in the doc:
                            tfIdfAllTermsInDocPow = self.tfPowForTerm(docID)

                            relevant_docs[0][docID] = [{term:[tfTermInDoc*idfTermInDoc, tfTermInQuery]}, tfIdfAllTermsInDocPow, 0] #we can delete the number

                        else:
                            if termIndex > 0 and query_dict[list(query_dict.keys())[termIndex-1]] in relevant_docs[0][docID][0].keys(): #its a term
                                relevant_docs[0][docID][2] += 1 #bonous
                            relevant_docs[0][docID][0][term] = [tfTermInDoc*idfTermInDoc, tfTermInQuery]


            except:
                pass
        return relevant_docs

    def isfloat(self,value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False


    def tfPowForTerm(self,docID):
        '''
        This function gets tweet id and count the sum of TF^2 of all the terms in this tweet
        '''
        tfSquareSum = 0
        for term in self.term_max_freq[docID][1].keys():

            type = [0, 1, 2, 3]
            t = term[0]
            # Deciding the type of the term
            if (self.isfloat(term) == True):  # numbers
                type = 0
            elif (term[0] not in string.ascii_lowercase and term[0] not in string.ascii_uppercase):  # others
                type = 1
            elif (' ' in term):  # entities
                type = 2
            else:  # strings
                type = 3
            if(term not in self.inverted_index.keys()):
                continue

            tfTerm = self.term_max_freq[docID][1][term] / self.term_max_freq[docID][0]
            idfTermInDoc = math.log((len(self.term_max_freq.keys()) / self.inverted_index[term][0]), 2)
            tfSquareSum += math.pow( (tfTerm*idfTermInDoc) ,2)
        return tfSquareSum

    def tfPowForTermQuery(self,term_query):
        '''
        This function gets tweet id and count the sum of TF^2 of all the terms in this tweet
        '''
        tfSquareSum = 0
        for term in term_query.keys():
            tfSquareSum += math.pow( (term_query[term]/max(term_query.values())) ,2)
        return tfSquareSum