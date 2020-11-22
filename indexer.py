import heapq
class Indexer:

    def __init__(self, config):
        self.inverted_idx = {} # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        self.term_max_freq = {} # (key - DocId): [Maxterm, freq, [single terms]]
        self.postingDict = {} # (key - term): Heap:[freq, docID, [indexes]]
        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        docID = document.tweet_id
        document_dictionary = document.term_doc_dictionary # document_dictionary = {term:[[indexes],freq]
        freq_terms = {} # save the freq of the term in this doc
        localDocPostingFile = {}
        listOfUniques = [] #list of unique terms
        self.term_max_freq[docID] = [] #[[] , , []]
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                #Update the freq of the term in this doc:
                if(term not in freq_terms):
                    freq_terms[term] = 1
                    localDocPostingFile[term] = [1,docID,document_dictionary[term][0]]
                else:
                    freq_terms[term] += 1
                    localDocPostingFile[term][0] +=1

                # Update inverted index and termMax
                if term not in self.inverted_idx.keys():
                    self.postingDict[term] = []
                    self.inverted_idx[term] = [1,1,self.postingDict]#TODO: Change the self.postingDict to the name of the posting file


                else:
                    #update inv_dict:
                    if(freq_terms[term] == 1):
                        # update inv_dict:
                        self.inverted_idx[term][0] += 1 # add another doc to the count in the inv_dict
                    self.inverted_idx[term][1] += 1

                if(freq_terms[term] == document_dictionary[term][1]):#if we finished with this term in this doc, we update the posting file
                    heapq.heappush(self.postingDict[term],localDocPostingFile[term])
                    if(freq_terms[term] == 1):
                        listOfUniques.append(term)



            except:
                print('problem with the following key {}'.format(term[0]))


        #update: maxTerm dictiontary
        maxFreq = max(freq_terms.values())
        maxTerms = []
        for i in freq_terms.keys():
            if(freq_terms[i] == maxFreq):
                maxTerms.append(i)
        self.term_max_freq[docID] = [maxTerms,maxFreq,listOfUniques]
