from parser_module import Parse
from ranker import Ranker
import utils


class Searcher:

    def __init__(self, inverted_index, thisStemmer=None):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.stemmer = thisStemmer
        self.inverted_index = inverted_index

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        postingLoadedNames = [] #Names of posting file which we already loaded.
        posting = []

        relevant_docs = {}
        if (self.stemmer != None):
            query = self.stemmer.stem_list(query)
        for term in query:
            termIndex = query.index(term)
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

                postingName = self.inverted_index[type][term][2]

                if(postingName not in postingLoadedNames): #its a list so i think its should be one by one ???????????????
                    postingLoadedNames.append(postingName) # Add the name of the new file
                    newPosting = utils.load_obj(postingName) # load the file
                    posting.append(newPosting) # Add the dictionary to the posting files
                posting_index = postingLoadedNames.index(postingName)
                posting_doc = posting[posting_index][term] # load the relevant tweets data for the term
                for doc_tuple in posting_doc:
                    doc = doc_tuple[1]
                    if doc not in relevant_docs.keys():
                        relevant_docs[doc] = [1, [term]] #we can delete the number
                    else:
                        if query[termIndex-1] in relevant_docs[doc][2] or term in relevant_docs[doc][1]: #its a term
                            relevant_docs[doc][0] += 1
                        relevant_docs[doc][0] += 1
                        relevant_docs[doc][1].append(term)
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