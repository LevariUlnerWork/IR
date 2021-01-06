import math
import utils
import string
from operator import itemgetter

# DO NOT MODIFY CLASS NAME
class Indexer:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self,config):

        self.inverted_idx = {}  # self.inverted_idx = [inverted_idx_nums, inverted_idx_ents, inverted_idx_others, inverted_idx_strs]
        self.alone_entities_dict = {}
        self.tweetTerms = {} #{TweetId:list of terms}
        self.counterOfTweetTermsFiles = 0
        self.config = config
        self.counterOfTweets=0

        letters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]#letters = [a,b,c....0,1...9]
        for letter in string.ascii_lowercase:
            letters.append(letter)

        self.postingFiles = {}

        for letter in letters:
            self.postingFiles["posting_" + letter] = {}
            for letter2 in letters:
                self.postingFiles["posting_" + letter + letter2] = {}

        self.letters = letters
        self.postingFiles["postingOthers"] = {}
        '''
        the posting files is built in this way:
        {term: [[freq of the term, docID, indexes of the term in this tweet, tf (would be in the end his cossim in this tweet)]]}
        '''

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        self.counterOfTweets += 1
        docID = document.tweet_id
        document_dictionary = document.term_doc_dictionary # document_dictionary = {term:[[indexes],freq]}
        self.tweetTerms[docID] = list(document_dictionary.keys())
        freq_max = sorted(list(document_dictionary.values()),key=itemgetter(1),reverse=True) [0][1] #Gets the maxFreq
        postingFileName = ""

        # Go over each term in the doc
        for term in sorted(list(document_dictionary.keys())):


                #Deciding the type of the term
                if (str(term[0]).lower() not in self.letters):  #others
                    type = 1
                elif(len(term) > 1): # 'J'
                    if str(term[1]).lower() not in self.letters and str(term[1]).lower() != '.': #1400 -> 1.400K
                        type = 1
                    else:  # strings
                        type = 2
                else:  #strings
                    type = 2

                if (' ' in term): #alone entities
                    if term not in self.alone_entities_dict: #fix it
                        self.alone_entities_dict[term] = 0
                    self.alone_entities_dict[term] += 1

                if (type == 1):
                    if(postingFileName != "postingOthers"):
                        postingFileName = "postingOthers"

                elif(len(term)==1):
                    if postingFileName != "posting_" + term.lower():
                        postingFileName = "posting_" + term.lower()

                elif (term[1] == '.'):
                    if postingFileName != "posting_" + term[0].lower():
                        postingFileName = "posting_" + term[0].lower()
                else:
                    if postingFileName !="posting_" + str(term[0]).lower() + str(term[1]).lower():
                        postingFileName = "posting_" + term[0].lower() + term[1].lower()

                indexes_t = document_dictionary[term][0]
                freq_t = document_dictionary[term][1]
                tf = freq_t / freq_max

                if term not in self.inverted_idx.keys():
                    self.postingFiles[postingFileName][term] = []
                    self.postingFiles[postingFileName][term].append([freq_t, docID, indexes_t,tf])
                    self.inverted_idx[term] = [1, freq_t, postingFileName]

                else:
                    #update inv_dict:
                    self.inverted_idx[term][0] += 1 # add another doc to the count in the inv_dict
                    self.inverted_idx[term][1] += freq_t
                    self.postingFiles[postingFileName][term].append([freq_t, docID, indexes_t,tf])


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.save_obj(self.tweetTerms, "TweetTerm_%s" % (self.counterOfTweetTermsFiles))
        self.computeTfIdf( self.counterOfTweets)
        self.deleteSingleEntities()
        inv_dict = {'inverted_idx': self.inverted_idx, 'posting': self.postingFiles}
        utils.save_obj(inv_dict, "inverted_idx")

    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        return utils.load_obj(fn)

    def changeTweetTermsDict(self):
        utils.save_obj(self.tweetTerms, "TweetTerm_%s" % (self.counterOfTweetTermsFiles))
        self.counterOfTweetTermsFiles += 1
        self.tweetTerms = {}


    def computeTfIdf(self, numberOfTweets):
        counterTweetsFiles = self.counterOfTweetTermsFiles
        postingFile = {}
        postingFileName = ""
        while counterTweetsFiles >= 0:
            tweetsFile = utils.load_obj( "TweetTerm_%s" % (counterTweetsFiles))
            for tweet in tweetsFile.keys():
                docSensorPerTerm = {}
                tfIdfThisTweet = {}
                for term in sorted(tweetsFile[tweet]):

                    #First - get the posting file
                    if (str(term[0]).lower() not in self.letters):  # others
                        type = 1
                    elif (len(term) > 1):
                        if str(term[1]).lower() not in self.letters and str(term[1]).lower() != '.':
                            type = 1
                        else:  # strings
                            type = 2
                    else:  # strings
                        type = 2

                    sopposedPostingName = ""

                    if(type == 1):
                        postingFileName = "postingOthers"
                    elif len(term) == 1:
                            postingFileName = "posting_" + term.lower()
                    elif term[1] == '.':
                            postingFileName = "posting_" + term[0].lower()
                    else:
                        postingFileName = "posting_" + str(term[0]).lower() + str(term[1]).lower()


                    tf = 1
                    #docID = 1
                    #Posting = {word:[[docID:13][][][docID:1]]   tinkle:[[][docID:1][][]]] }
                    #sensor = {word:3, tinkle:1}
                    for docData in range (len(self.postingFiles[postingFileName][term])):
                        if self.postingFiles[postingFileName][term][docData][1] == tweet:
                            tf = self.postingFiles[postingFileName][term][docData][3]
                            docSensorPerTerm[term] = docData
                            break
                    idf_Term = math.log2(numberOfTweets / self.inverted_idx[term][0])
                    tfIdfThisTweet[term] = tf*idf_Term #tfidf = {word: 3.45324, tinkle:21234}

                tfIdfThisTweetPowList = [math.pow(x,2) for x in tfIdfThisTweet.values()] #{word:5.2}
                denominator = math.sqrt(sum(tfIdfThisTweetPowList))
                for term in sorted(tweetsFile[tweet]):
                    #First - get the posting file
                    if (str(term[0]).lower() not in self.letters):  # others
                        type = 1
                    elif (len(term) > 1):
                        if str(term[1]).lower() not in self.letters and str(term[1]).lower() != '.':
                            type = 1
                        else:  # strings
                            type = 2
                    else:  # strings
                        type = 2

                    sopposedPostingName = ""

                    if (type == 1):
                        postingFileName = "postingOthers"
                    elif len(term) == 1:
                        postingFileName = "posting_" + term.lower()
                    elif term[1] == '.':
                        postingFileName = "posting_" + term[0].lower()
                    else:
                        postingFileName = "posting_" + str(term[0]).lower() + str(term[1]).lower()

                    enumerate = tfIdfThisTweet[term]
                    self.postingFiles[postingFileName][term][docSensorPerTerm[term]][3] = enumerate / denominator #Cossim of the term in this tweet
            counterTweetsFiles -= 1


    def deleteSingleEntities(self):
        for term in self.alone_entities_dict.keys():
            if (self.alone_entities_dict[term] == 1):
                self.postingFiles[self.inverted_idx[term][2]].pop(term)
                self.inverted_idx.pop(term)
        self.alone_entities_dict = {}



    def isfloat(self, value):
        if(value[0] == 'i' or value[0] == 'I'):
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False

