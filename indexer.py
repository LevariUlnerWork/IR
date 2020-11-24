import heapq #TODO: Change to priority queue
class Indexer:

    def __init__(self, config):
        self.inverted_idx = {} # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        self.term_max_freq = {} # (key - DocId): [Maxterm, freq, [single terms]]
        self.postingDictNames = ["posting1"] # Names of posting files
        self.postingDict = {} # (key - term): Heap:[freq, docID, [indexes]]
        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        #TODO: delete t.co from the corpus.
        #TODO: delete 1 time show terms
        #TODO: split posting files
        docID = document.tweet_id
        document_dictionary = document.term_doc_dictionary # document_dictionary = {term:[[indexes],freq]
        freq_terms = {} # save the freq of the term in this doc
        listOfUniques = [] #list of unique terms
        self.term_max_freq[docID] = [] #[[] , , []]
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                #Update the local dicts: freq of the term in this doc:

                freq_terms[term] = document_dictionary[term][1]

                # Update the public inverted index and termMax
                if term not in self.inverted_idx.keys():
                    self.postingDict[term] = []
                    self.inverted_idx[term] = [1,document_dictionary[term][1],self.postingDictNames[0]]#TODO: Change the self.postingDict to the name of the posting file

                else:
                    #update inv_dict:
                    self.inverted_idx[term][0] += 1 # add another doc to the count in the inv_dict
                    self.inverted_idx[term][1] += document_dictionary[term][1]

                heapq.heappush(self.postingDict[term],[document_dictionary[term][1],docID,document_dictionary[term][0]])
                if document_dictionary[term][1] == 1:
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
