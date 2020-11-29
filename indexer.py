import utils
import string
from queue import PriorityQueue
class Indexer:

    def __init__(self, config):
        #self.inverted_idx_nums = {}  # (key - term): [num Of docs, freq in corpus, [pointers to posting files]]
        #self.inverted_idx_others = {}  # (key - term): [num Of docs, freq in corpus, [pointers to posting files]]
        #self.inverted_idx_ents = {}  # (key - term): [num Of docs, freq in corpus,[pointers to posting files]]
        #self.inverted_idx_strs = {}  # (key - term): [num Of docs, freq in corpus, [pointers to posting files]]

        self.inverted_idx = [{}, {}, {}, {}]  # self.inverted_idx = [inverted_idx_nums, inverted_idx_ents, inverted_idx_others, inverted_idx_strs]
        '''
        the inverted index dictionary is a list of 4 dictionaries:
        #self.inverted_idx_nums = {}  # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        #self.inverted_idx_others = {}  # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        #self.inverted_idx_ents = {}  # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        #self.inverted_idx_strs = {}  # (key - term): [num Of docs, freq in corpus, pointer to posting file]
        '''

        self.term_max_freq = {}  # (key - DocId): [[maxterms], freq, [single terms]]

        postingStrsNames = []
        for letter in string.ascii_lowercase:
            postingStrsNames.append("postingStrs_" + letter + "0")
        for letter in string.ascii_uppercase:
            postingStrsNames.append("postingStrs_C" + letter + "0")

        self.postingDictNames = ["postingNums","postingOthr", "postingEnts", postingStrsNames] #Names of posting files
        self.currentFileNumber = 0  # which number of file we are


        self.postingDicts = [{}, {}, {}, [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]]  # self.posting_file = [postingDictNums, postingDictOthers, postingDictEnts, postingDictStrs]
        '''
        the posting files is split to 3 dictionaries of lists:
        #self.postingDictNums = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        #self.postingDictOthers = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        #self.postingDictEnts = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        we also have one list of dictionaries for strings:
        #self.postingDictStrs [a{},b{}...A{},B{}...] = {}  # Current posting file (key - term): Heap:[freq, docID, [indexes]]
        '''
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
        freq_terms = {} # {freq:[terms]} # save the freq of the term in this doc
        listOfUniques = [] #list of unique terms
        self.term_max_freq[docID] = [] #[[] , , []]
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:

                #update the most freqs of one term in the tweet:
                if document_dictionary[term][1] not in freq_terms:
                    freq_terms[document_dictionary[term][1]] = [term]
                else:
                    freq_terms[document_dictionary[term][1]].append(term)



                #Update the local dicts: freq of the term in this doc:
                type = [0,1,2,3]
                t = term[0]
                #Deciding the type of the term
                if(Indexer.isfloat(term) == True):  #numbers
                    type = 0
                elif (term[0] not in string.ascii_lowercase and term[0] not in string.ascii_uppercase):  #others
                    type = 1
                elif (' ' in term): #entities
                    type = 2
                else:  #strings
                    type = 3


                if term not in self.inverted_idx[type].keys():
                    if(type==3):
                        letterIndex = 0
                        if(term[0] in string.ascii_lowercase): #Starts with 'á','b'...
                            letterIndex = string.ascii_lowercase.index(term[0])
                        else:#Starts with 'A','B'...
                            letterIndex = string.ascii_uppercase.index(term[0]) + 26

                        self.postingDicts[3][letterIndex][term] = []
                        self.postingDicts[type][letterIndex][term].append([document_dictionary[term][1], docID, document_dictionary[term][0]])
                        self.inverted_idx[type][term] = [1, document_dictionary[term][1], [self.postingDictNames[type][letterIndex]]]
                    else:
                        self.postingDicts[type][term] = []
                        self.postingDicts[type][term].append([document_dictionary[term][1], docID, document_dictionary[term][0]])
                        self.inverted_idx[type][term] = [1, document_dictionary[term][1], [self.postingDictNames[type]]]

                else:
                    #update inv_dict:
                    self.inverted_idx[type][term][0] += 1 # add another doc to the count in the inv_dict
                    self.inverted_idx[type][term][1] += document_dictionary[term][1]

                    if(type == 3):
                        if (term[0] in string.ascii_lowercase):  # Starts with 'á','b'...
                            letterIndex = string.ascii_lowercase.index(term[0])
                        else:  # Starts with 'A','B'...
                            letterIndex = string.ascii_uppercase.index(term[0]) + 26

                        if term not in self.postingDicts[type][letterIndex].keys():
                            self.postingDicts[type][letterIndex][term] = []
                            self.inverted_idx[type][term][2].append(self.postingDictNames[type][letterIndex])
                        self.postingDicts[type][letterIndex][term].append([document_dictionary[term][1], docID, document_dictionary[term][0]])
                    else:
                        if term not in self.postingDicts[type].keys():
                            self.postingDicts[type][term] = []
                            self.inverted_idx[type][term][2].append(self.postingDictNames[type])
                        self.postingDicts[type][term].append([document_dictionary[term][1], docID, document_dictionary[term][0]])
                # Update the public inverted index and termMax

                if document_dictionary[term][1] == 1:
                    listOfUniques.append(term)



            except:
                print('problem with the following key {}'.format(term))


        #update: term_max_freq dictiontary
        maxTerms = freq_terms[max(freq_terms.keys())]
        self.term_max_freq[docID] = [maxTerms, max(freq_terms.keys()), listOfUniques]


    def savePostingFile(self):
        """
        This function is made to order the indexer to output the posting files
        """
        #To save the posting_dict as a file:
        self.currentFileNumber += 1
        for type in range (3):
            utils.save_obj(self.postingDicts[type], self.postingDictNames[type] ) # Saves any posting file
            self.postingDictNames[type] = self.postingDictNames[type][:11] + str(self.currentFileNumber) # Creates new names
            self.postingDicts[type] = {}

        type=3
        for letter in range(26):
            utils.save_obj(self.postingDicts[type][letter], self.postingDictNames[type][letter])  # Saves any posting file
            self.postingDictNames[type][letter] = self.postingDictNames[type][letter][:13] + str(self.currentFileNumber)  # Creates new names
            self.postingDicts[type][letter] = {}
        for letter in range(26,52):
            utils.save_obj(self.postingDicts[type][letter], self.postingDictNames[type][letter])  # Saves any posting file
            self.postingDictNames[type][letter] = self.postingDictNames[type][letter][:14] + str(self.currentFileNumber)  # Creates new names
            self.postingDicts[type][letter] = {}


    def isfloat(value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False
