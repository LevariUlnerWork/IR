import heapq #TODO: Change to priority queue
class Indexer:

    def __init__(self, config):
        #self.inverted_idx_nums = {} # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        # self.inverted_idx_others = {} # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        #self.inverted_idx_ishus = {} # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        # self.inverted_idx_strs = {} # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        self.inverted_idx = [{},{},{},{}] # self.inverted_idx = [self.inverted_idx_nums,self.inverted_idx_strs, self.inverted_idx_ishus, self.inverted_idx_others]

        #self.term_max_freq = {} # (key - DocId): [Maxterm, freq, [single terms]]

        self.postingDictNames = ["postingNums0","postingStrs0","postingIshus0","postingOthers0"] # Names of posting files
        self.currentFileNumber = 0 # which number of file we are
        #self.postingDictNums = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        # self.postingDictOthers = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        #self.postingDictIshus = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        # self.postingDictStrs = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        self.postingDicts = [{},{},{},{}] #self.posting_file = [self.postingDictNums,self.postingDictStrs, self.postingDictIshus, self.postingDictOthers]

        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        #TODO: delete 1 time show terms
        #TODO: split posting files

        docID = document.tweet_id
        document_dictionary = document.term_doc_dictionary # document_dictionary = {term:[[indexes],freq]
        freq_terms = {} # save the freq of the term in this doc
        listOfUniques = [] #list of unique terms
        #self.term_max_freq[docID] = [] #[[] , , []]
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                #Update the local dicts: freq of the term in this doc:
                type = [0,1,2,3]
                freq_terms[term] = document_dictionary[term][1]
                if(Indexer.isfloat(term) == True):
                    type = 0
                elif (len(term) == 1 ):
                    type = 1
                elif (' ' in term):
                    type = 2
                else:
                    type = 3
                # Update the public inverted index and termMax
                if term not in self.inverted_idx[type].keys():
                    self.postingDicts[type][term] = []
                    self.inverted_idx[type][term] = [1,document_dictionary[term][1],self.postingDictNames[type]]#TODO: Change the self.postingDict to the name of the posting file

                else:
                    #update inv_dict:
                    self.inverted_idx[type][term][0] += 1 # add another doc to the count in the inv_dict
                    self.inverted_idx[type][term][1] += document_dictionary[term][1]

                heapq.heappush(self.postingDicts[type][term],[document_dictionary[term][1],docID,document_dictionary[term][0]])
                if document_dictionary[term][1] == 1:
                    listOfUniques.append(term)



            except:
                print('problem with the following key {}'.format(term[0]))

        """
        #update: maxTerm dictiontary
        maxFreq = max(freq_terms.values())
        maxTerms = []
        for i in freq_terms.keys():
            if(freq_terms[i] == maxFreq):
                maxTerms.append(i)
        self.term_max_freq[docID] = [maxTerms,maxFreq,listOfUniques]
        """

    def savePostingFile(self):
        """
        This function is made to order the indexer to output the posting files
        """
        #To save the posting_dict as a file:
        # utils.save_obj(self.postingDicts, self.postingDictNames[0] )

        self.currentFileNumber += 1
        self.postingDictNames.insert(0, "posting%s" % (self.currentFileNumber))


    def isfloat(value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False